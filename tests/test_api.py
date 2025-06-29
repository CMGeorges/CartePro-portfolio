import requests

BASE_URL = "http://localhost:5000/api/v1"

def print_response(resp):
    print(f"[{resp.request.method}] {resp.url}")
    print(f"Status: {resp.status_code}")
    try:
        print("Response:", resp.json())
    except Exception:
        print("Response (non-JSON):", resp.text)
    print("-" * 60)

def test_health():
    resp = requests.get(f"{BASE_URL}/")
    print_response(resp)

def test_generate_qr():
    data = {"url": "https://example.com"}
    resp = requests.post(f"{BASE_URL}/generate", json=data)
    print_response(resp)

def test_card_lifecycle():
    # Création
    data = {
        "name": "Alice Test",
        "email": "alice@example.com",
        "title": "CEO",
        "phone": "123-456-7890",
        "website": "https://alice.com",
        "instagram": "@alice",
        "linkedin": "linkedin.com/in/alice"
    }
    resp = requests.post(f"{BASE_URL}/cards", json=data)
    print_response(resp)
    if resp.status_code not in (200, 201) or 'id' not in resp.json():
        print("❌ Création de carte échouée, tests suivants annulés.")
        return None
    card_id = resp.json()['id']

    # Lecture
    resp = requests.get(f"{BASE_URL}/cards/{card_id}")
    print_response(resp)

    # Mise à jour
    update_data = {"phone": "987-654-3210"}
    resp = requests.put(f"{BASE_URL}/cards/{card_id}", json=update_data)
    print_response(resp)

    # Suppression
    resp = requests.delete(f"{BASE_URL}/cards/{card_id}")
    print_response(resp)

    return card_id

def test_checkout_session():
    # Remplace price_XXXXXX par un vrai Price ID Stripe pour un vrai test
    data = {"price_id": "price_XXXXXX"}
    resp = requests.post(f"{BASE_URL}/create-checkout-session", json=data)
    print_response(resp)

def test_config():
    resp = requests.get(f"{BASE_URL}/config")
    print_response(resp)

if __name__ == "__main__":
    print("=== Test API Health ===")
    test_health()
    print("=== Test QR Code Generation ===")
    test_generate_qr()
    print("=== Test Card Lifecycle ===")
    test_card_lifecycle()
    print("=== Test Stripe Checkout Session ===")
    test_checkout_session()
    print("=== Test Stripe Config ===")
    test_config()