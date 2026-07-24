# EveAccessories — Codebase Summary

## 1. Overview

**EveAccessories** is a server-rendered e-commerce web application for a women's jewelry/accessories store (Arabic RTL storefront branded "Eve Accessories"). It supports product browsing, a session/account-based shopping cart, checkout without payment gateway integration (Cash on Delivery / manual wallet transfer with proof-of-payment upload), and a custom admin dashboard for managing products, categories, orders, and store settings.

**Tech stack:**
- **Backend:** Python 3 / Django 5.1 (monolithic MVT architecture, no DRF/API layer — server-rendered HTML)
- **Database:** SQLite in development, configurable via env vars (any Django-supported engine, e.g. Postgres/MySQL) in production
- **Frontend:** Django templates + Bootstrap 5.3 (via CDN) + Popper.js, custom CSS (`main.css`, `styles.css`), custom web fonts (Zanjabeel family) — no JS framework or bundler (no `package.json`, the root `package-lock.json` is an empty stub)
- **Auth:** Custom email-based `User` model (`AUTH_USER_MODEL = accounts.User`), Django's built-in auth views/tokens, email verification flow via SMTP (Gmail)
- **Other libraries:** `django-cleanup` (auto-delete orphaned media files), `python-dotenv` (env config), `Pillow` (image handling)

## 2. Architecture & Structure

The repo root contains the Django project (`EveAccessories/`) plus top-level `requirements.txt`, `.venv`, and licensing/IDE files. Everything of substance lives under `EveAccessories/`, organized as one project with four apps:

- **`EveAccessories/EveAccessories/`** — Project core: `settings.py`, root `urls.py`, `wsgi.py`/`asgi.py`. Wires together the four apps and static/media serving.
- **`accessories/`** — Product catalog domain: `Category`, `Product`, `ProductImage` models; public views for home, category list, product list/detail, and add/remove-from-cart actions.
- **`accounts/`** — Custom `User` model (email as username, Egyptian governorate/city/address fields, and a denormalized `cart` string field), signup/login/logout, email activation tokens, profile editing, and `RequireAdminLoginMiddleware` which gates any URL matching `ADMIN_LOGIN_REQUIRED_URLS` (i.e. `/dashboard/*`) behind `is_staff`.
- **`orders/`** — `Order`, `OrderEntry` (line items), `OrderLog` (audit trail) models; cart view, checkout (`CreateOrder`), and order confirmation pages.
- **`dashboard/`** — Admin-only back-office: `Setting` model (site-wide config: hero/payment images, per-governorate shipping fees, homepage category count) plus CRUD views for products, categories, order-status management, and dashboard analytics (month/year/all-time sales stats).
- **`templates/`** — Global templates, organized into `partials/{components,icons,layout,sections}` for reusable includes (navbar, footer, product/category cards, icons) and per-feature subfolders (`orders/`, `registration/`, `dashboard/`, `auth/`).
- **`static/`** — CSS, fonts, logo (served via `django.contrib.staticfiles` in dev, `STATIC_ROOT` collection in prod).
- **`media/`** — User-uploaded content: category/product images, organized by app-defined `upload_to` paths.
- Each app follows standard Django layout: `models.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `migrations/`, and (where relevant) `forms.py`.

## 3. Core Workflows

**Storefront browsing → cart → checkout:**
1. `accessories.views.index` reads the singleton `dashboard.Setting` row for hero image/category count, and renders featured categories + newest products.
2. `ProductListView`/`ProductView` (Django generic `ListView`/`DetailView`) support category filtering and pagination.
3. Cart state is stored as a delimited string (`"<product_id>#<variant>-<product_id>#<variant>-..."`) — persisted on `request.session['cart']` for guests, and mirrored into `User.cart` for authenticated users on every add/remove (see `ProductView.post`, `orders.views.remove_from_cart`). Out-of-stock products are blocked from being added.
4. `orders.views.CartView` parses that string back into a `Product` queryset for display.
5. `CreateOrder` (a `CreateView`) does the heavy lifting on submit: re-validates quantities against current stock, enforces a max-2-undelivered-orders-per-user/phone limit, decrements `Product.stock`, creates `OrderEntry` rows priced at `discounted_price`, computes `order_total` (line items + flat shipping fee), auto-confirms Cash-on-Delivery orders, logs an `OrderLog` entry, clears the cart, and redirects to an order-success page.

**Authentication:**
- Custom `LoginForm`/`CreateUserForm` (Egyptian phone-number regex validation) on top of Django's `AuthenticationForm`/`UserCreationForm`.
- Signup creates an active-but-unverified account and emails a token-based activation link (`accounts/tokens.py` + `registration/acc_active_email.html`); `activate()` view validates the token and flips `is_active`.
- Successful login redirects staff/superusers to `/dashboard/`, everyone else to the homepage (or a `?next=` target).

**Admin dashboard (staff-only, enforced by `RequireAdminLoginMiddleware`):**
- CRUD for `Category`/`Product` (supports both uploaded image files and raw image URLs per `ProductImage`, plus bulk category-wide discount application).
- Order pipeline management: `confirm_order` → `deliver_order` → `complete_order`, or `reject_order` (which restocks the cancelled order's items).
- `DashboardView` aggregates month/year/all-time order counts, revenue (`Sum(order_total)`), and items-sold stats via Django ORM aggregation.
- `SettingsView` edits the singleton `Setting` row (hero/payment images, per-governorate shipping costs).

## 4. Key Dependencies

| Package | Purpose |
|---|---|
| `Django==5.1` | Core web framework (ORM, templating, auth, admin, forms) |
| `asgiref==3.8.1` | ASGI support underlying Django (async server interface) |
| `django-cleanup==8.1.0` | Auto-deletes old/orphaned `ImageField` files on model update/delete |
| `django-utils-six` | Python 2/3 compatibility shims for older Django utilities |
| `pillow==10.4.0` | Image processing, required for `ImageField` |
| `python-dotenv==1.0.1` | Loads `.env` file into environment variables for settings |
| `sqlparse==0.5.1` | SQL parsing, a Django dependency (used by the ORM/debug tooling) |
| `tzdata==2024.1` | Timezone database (needed on platforms without system tz data, e.g. Windows) |
| Bootstrap 5.3 / Popper.js (CDN) | Frontend styling and UI components — no local install/build step |

## 5. Configuration & Setup

- **Environment-driven settings** (`EveAccessories/settings.py`, loaded via `python-dotenv`): `SECRET_KEY`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DEVELOPMENT` (toggles SQLite + local static dirs vs. production DB config), `DB_ENGINE`/`DB_NAME`/`DB_USER`/`DB_HOST`/`DB_PASSWORD`, `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` (Gmail SMTP for verification emails). No committed `.env`/`.env.example` — one must be created locally.
- **Database:** SQLite (`db.sqlite3`) when `DEVELOPMENT` is set; otherwise a fully env-configured external database. Migrations exist for both `accessories` and other apps (4 migrations tracked for `accessories`).
- **Static/media:** `STATICFILES_DIRS` in dev, `STATIC_ROOT` collection (`collectstatic`) in prod; `MEDIA_ROOT`/`MEDIA_URL` served directly by Django's URL conf via `static()` helpers (fine for dev, would typically be fronted by a CDN/object storage in real production).
- **Sessions/security:** Signed-cookie session backend, HttpOnly session cookies, standard Django security middleware stack, plus the custom `RequireAdminLoginMiddleware` gating `/dashboard/*`.
- **Running locally:** standard Django workflow — `pip install -r requirements.txt`, create `.env` with the vars above, `python manage.py migrate`, `python manage.py runserver` (from `EveAccessories/manage.py`). No Docker, CI, or process-manager config (e.g. Procfile) is present in the repo.
- **No test suite is implemented** — each app has a stub `tests.py` but no actual test cases were found.
