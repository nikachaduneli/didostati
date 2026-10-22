# Didostati

Simple e-commerce shop. Django + DRF backend in `backend/` (PostgreSQL database, Redis for the cache and login
tokens), Vue 3 (Vite) frontend in `frontend/`.

## Run with Docker
```bash
cp .env.example .env                                      # optional: change passwords / secret key / ports
docker compose up -d --build                              # shop on http://localhost:8000, admin on /admin/
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_demo    # optional demo data
```
Services: `db` (PostgreSQL), `redis`, `backend` (gunicorn; runs migrations and collectstatic on start) and `nginx`
(serves `/static/` and `/media/`, forwards the rest). Data lives in the `postgres`, `redis` and `media` volumes.

## Local development (without Docker for Django)
Start only PostgreSQL and Redis, then run Django and Vite on your machine:
```bash
docker compose up -d db redis
.venv/bin/pip install -r backend/requirements.txt
cd backend
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py seed_demo          # optional demo categories/products/blogs/pages
../.venv/bin/python manage.py createsuperuser    # admin login
cd ../frontend && npm install
```
Django connects to `localhost:5432` and `localhost:6379` by default; override with `POSTGRES_HOST`, `POSTGRES_PORT`
and `REDIS_URL` (e.g. `REDIS_URL=redis://localhost:6380` when `REDIS_HOST_PORT=6380`).

## Backend apps
- `core` – shared abstract models (translations, auto slug, address fields)
- `catalog` – categories, colours, products (+ `seed_demo` command)
- `content` – pages, blog posts, contact messages
- `accounts` – addresses, register/login (bearer tokens stored in Redis, see `accounts/tokens.py`)
- `orders` – cart pricing, orders

## Development servers (two terminals)
```bash
cd backend  && ../.venv/bin/python manage.py runserver     # API + admin on :8000
cd frontend && npm run dev                                 # shop on http://localhost:5173
```
Admin panel: http://localhost:8000/admin/

## Single-server mode
`cd frontend && npm run build`, then `runserver` serves the shop at http://localhost:8000/.

## Editing content in the admin
- **Pages**: `about` and `contact` (menu links use these slugs).
- **Blogs**: cover image + rich editor; insert images anywhere, click an image to align it
  (left / centre / right) and drag its corner handles or use the toolbar to resize it.
- **Products**: price, discount %, colours, several pictures (optionally tied to a colour), "popular" flag.
- Currency is set in `frontend/src/config.js`.

## Card payments

Checkout can charge cards through **Bank of Georgia** and **TBC Bank**. Both accept Visa and Mastercard from any
country, so customers abroad can pay. Prices are in GEL.

Fill in the credentials in `backend/config/settings.py` ("Card payments"). A bank appears at checkout only when its
credentials are set:

| Setting | Where to get it |
|---|---|
| `BOG_CLIENT_ID`, `BOG_CLIENT_SECRET` | Bank of Georgia online payments (https://api.bog.ge/docs/en/payments/introduction) |
| `TBC_API_KEY`, `TBC_CLIENT_ID`, `TBC_CLIENT_SECRET` | TBC developer portal (https://developers.tbcbank.ge); register the callback URL in the merchant dashboard (ecom.tbcpayments.ge) |
| `SITE_URL` | Public HTTPS address of the shop, e.g. `https://didostati.ge`. The banks call back to `SITE_URL/api/payments/bog/callback/` and `.../tbc/callback/`, so they must be reachable from the internet |

Flow: the order is saved as *awaiting payment* → the customer is sent to the bank's page → the bank returns them to
`/payment/return` and also calls the callback. The status is always read back from the bank's API, never trusted from
the request. When an order is confirmed paid, the owner email (`ORDER_NOTIFICATION_EMAIL`) is sent once.

For local testing without a bank, set `PAYMENT_MOCK_ENABLED = True` (adds a fake gateway; never enable in production).
`PAYMENT_CASH_ON_DELIVERY = False` removes the pay-on-delivery option.
