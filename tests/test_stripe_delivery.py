import hashlib
import hmac
import json
import time

import pytest
import stripe
from app import create_app
from app.extensions import db
from app.models import User, Subscription, StripeWebhookEvent


class Config:
    TESTING = True
    SECRET_KEY = 'testing-only'
    STRIPE_SECRET_KEY = 'sk_test_fake'
    STRIPE_WEBHOOK_SECRET = 'whsec_test_fake'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True
    RATELIMIT_ENABLED = False


@pytest.fixture
def app():
    app = create_app(Config)
    with app.app_context():
        user = User(username='alice', email='alice@example.com', stripe_customer_id='cus_alice')
        user.set_password('example-password')
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


def send(app, event_id='evt_one', kind='customer.subscription.created', secret=None):
    payload = json.dumps({'id': event_id, 'object': 'event', 'type': kind,
                          'data': {'object': {'id': 'sub_one'}}})
    timestamp = str(int(time.time()))
    digest = hmac.new((secret or Config.STRIPE_WEBHOOK_SECRET).encode(),
                      f'{timestamp}.{payload}'.encode(), hashlib.sha256).hexdigest()
    return app.test_client().post('/api/v1/stripe/webhook', data=payload,
        content_type='application/json', headers={'Stripe-Signature': f't={timestamp},v1={digest}'})


def live(status='active', customer='cus_alice'):
    return dict(id='sub_one', customer=customer, status=status,
                items={'data': [{'price': {'id': 'price_pro'}, 'current_period_end': 2000000000}]})


def test_signed_webhook_accepts_without_csrf_and_deduplicates(app, monkeypatch):
    calls = []
    monkeypatch.setattr(stripe.Subscription, 'retrieve', lambda sid: calls.append(sid) or live())
    assert send(app).status_code == 200
    assert send(app).status_code == 200
    assert len(calls) == 1
    assert Subscription.query.count() == 1
    assert StripeWebhookEvent.query.count() == 1
    assert User.query.first().is_pro
    # Browser mutations remain protected.
    assert app.test_client().post('/auth/register', json={}).status_code == 400


def test_cancellation_and_delayed_created_event_use_current_state(app, monkeypatch):
    monkeypatch.setattr(stripe.Subscription, 'retrieve', lambda sid: live())
    assert send(app).status_code == 200
    monkeypatch.setattr(stripe.Subscription, 'retrieve', lambda sid: live('canceled'))
    assert send(app, 'evt_deleted', 'customer.subscription.deleted').status_code == 200
    assert send(app, 'evt_delayed_created').status_code == 200
    assert not User.query.first().is_pro
    assert Subscription.query.first().status == 'canceled'


def test_invalid_signature_never_changes_access(app):
    assert send(app, secret='incorrect').status_code == 400
    assert StripeWebhookEvent.query.count() == Subscription.query.count() == 0


def test_missing_customer_retries_without_marking_processed(app, monkeypatch):
    monkeypatch.setattr(stripe.Subscription, 'retrieve', lambda sid: live(customer='cus_missing'))
    assert send(app).status_code == 503
    assert StripeWebhookEvent.query.count() == 0
    monkeypatch.setattr(stripe.Subscription, 'retrieve', lambda sid: live())
    assert send(app).status_code == 200


def test_stripe_failure_retries_without_marking_processed(app, monkeypatch):
    def unavailable(sid):
        raise stripe.APIConnectionError('offline')
    monkeypatch.setattr(stripe.Subscription, 'retrieve', unavailable)
    assert send(app).status_code == 502
    assert StripeWebhookEvent.query.count() == 0
