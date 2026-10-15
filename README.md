# BXL Market Chat — Django Web Platform

V1 scope: core marketplace (browse/post/product detail) + real-time buyer-seller chat.
Logistics and POS are later phases.

## Apps
- `accounts` — custom User model, seller storefront pages
- `listings` — categories, products, browse, product detail (site root)
- `posting` — the "Post Your Item" multi-step form
- `chat` — Conversation/Message models + Django Channels consumer for real-time messaging

## Setup
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill in values
4. Redis must be running locally for Channels (`redis-server`)
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. Run with Daphne (ASGI, required for websockets): `daphne bxl_marketchat.asgi:application`
   - Plain `python manage.py runserver` works for HTTP-only testing but won't serve the chat websocket.

## Not yet built
- `templates/` — none scaffolded yet, views reference template paths that need creating
- Wallet/payments (Paystack/Flutterwave) — settings keys are stubbed, no models yet
- `business` app (business directory/posts) — deferred, same as logistics/POS per client scope
