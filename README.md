# Didostati

Simple e-commerce shop. Django + DRF (SQLite) backend in `backend/`, Vue 3 (Vite) frontend in `frontend/`.

## First-time setup
```bash
.venv/bin/pip install django djangorestframework pillow django-ckeditor-5
cd backend
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py seed_demo          # optional demo categories/products/blogs/pages
../.venv/bin/python manage.py createsuperuser    # admin login
cd ../frontend && npm install
```

## Backend apps
- `core` – shared abstract models (translations, auto slug, address fields)
- `catalog` – categories, colours, products (+ `seed_demo` command)
- `content` – pages, blog posts, contact messages
- `accounts` – addresses, register/login
- `orders` – cart pricing, orders

## Development (two terminals)
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
