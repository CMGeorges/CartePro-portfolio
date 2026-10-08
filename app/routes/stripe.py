from datetime import datetime, timezone

from flask import Blueprint, jsonify, current_app, request
import stripe
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Subscription, User, StripeWebhookEvent
from app.extensions import csrf
from app.errors import APIError

stripe_bp = Blueprint('stripe', __name__)


@stripe_bp.route('/config', methods=['GET'])
def stripe_config():
    try:
        products = stripe.Product.list(limit=5)
        prices = stripe.Price.list(limit=5)
        return jsonify(publicKey=current_app.config.get('STRIPE_PUBLIC_KEY'),
                       products=list(products.data), prices=list(prices.data))
    except stripe.StripeError:
        raise APIError('Unable to load Stripe configuration.', 502)


@stripe_bp.route('/webhook', methods=['POST'])
@csrf.exempt
def stripe_webhook():
    # Stripe authenticates this one endpoint; browser routes retain CSRF protection.
    secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    if not secret:
        raise APIError('Stripe webhook is not configured.', 503)
    try:
        event = stripe.Webhook.construct_event(
            request.get_data(), request.headers.get('Stripe-Signature', ''), secret)
    except (ValueError, stripe.SignatureVerificationError):
        raise APIError('Invalid Stripe signature or payload.', 400)

    event_id = event.get('id')
    event_type = event.get('type')
    if not isinstance(event_id, str) or not event_id.startswith('evt_'):
        raise APIError('Invalid Stripe event.', 400)
    if event_type not in {'customer.subscription.created',
                          'customer.subscription.updated',
                          'customer.subscription.deleted'}:
        return jsonify(status='ignored')
    if db.session.get(StripeWebhookEvent, event_id):
        return jsonify(status='already_processed')

    try:
        subscription_id = event['data']['object']['id']
        # Fetch current Stripe state so delayed events cannot restore canceled access.
        live = stripe.Subscription.retrieve(subscription_id)
        customer = live['customer']
        if not isinstance(customer, str):
            customer = customer['id']
        user = User.query.filter_by(stripe_customer_id=customer).first()
        if not user:
            raise APIError('Stripe customer is not linked yet. Retry delivery.', 503)
        items = live.get('items', {}).get('data', [])
        period_end = live.get('current_period_end')
        if period_end is None and items:
            period_end = items[0].get('current_period_end')
        if not period_end:
            raise APIError('Subscription period is missing. Retry delivery.', 503)
        plan = live.get('plan') or (items[0].get('price', {}) if items else {})
        db.session.add(StripeWebhookEvent(
            id=event_id, event_type=event_type,
            processed_at=datetime.now(timezone.utc).replace(tzinfo=None)))
        db.session.flush()  # Claim delivery and subscription update in one transaction.
        sub = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if sub is None:
            sub = Subscription(user_id=user.id, stripe_subscription_id=subscription_id)
            db.session.add(sub)
        sub.plan_name = plan.get('id', 'subscription')
        sub.status = live['status']
        sub.current_period_end = datetime.fromtimestamp(period_end, timezone.utc).replace(tzinfo=None)
        db.session.commit()
    except APIError:
        db.session.rollback()
        raise
    except stripe.StripeError:
        db.session.rollback()
        raise APIError('Stripe unavailable. Retry delivery.', 502)
    except SQLAlchemyError:
        db.session.rollback()
        if db.session.get(StripeWebhookEvent, event_id):
            return jsonify(status='already_processed')
        raise APIError('Subscription storage unavailable. Retry delivery.', 503)
    except (KeyError, TypeError, ValueError, OverflowError):
        db.session.rollback()
        raise APIError('Incomplete subscription data. Retry delivery.', 503)
    return jsonify(status='success')
