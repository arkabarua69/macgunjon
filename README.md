# Mac GunJon

Full-featured e-commerce platform for selling digital products, websites, bots, and automation tools.

## Features

- Product catalog with categories, variants, and multi-currency pricing (USD/GBP)
- Session-based shopping cart
- Stripe payment integration
- Digital product delivery with secure download tokens
- Order management and tracking
- AI-powered chatbot for customer support
- Email notifications (order confirmation, delivery, password reset)
- REST API with JWT authentication
- Admin dashboard with analytics
- Responsive Bootstrap 5 frontend

## Tech Stack

- Python 3.12 / Django 5.2
- PostgreSQL
- Redis (cache, sessions, Celery broker)
- Celery + django-celery-beat (async tasks, scheduled jobs)
- Stripe (payments)
- Amazon SES (transactional email)
- Sentry (error tracking)
- Docker + Nginx (deployment)

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+

### Installation

```bash
git clone https://github.com/yourusername/macgunjon.git
cd macgunjon
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment

Copy the example and configure:

```bash
cp .env.example .env
```

Edit `.env` with your database, Stripe, email, and Sentry credentials.

### Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Run

```bash
python manage.py runserver
```

### Docker

```bash
docker-compose up -d
```

## Project Structure

```
macgunjon/          Project settings, URLs, WSGI
products/           Product catalog, categories, reviews
cart/               Shopping cart
orders/             Order processing
payments/           Stripe integration
delivery/           Digital product delivery tokens
coupons/            Discount coupons
users/              Authentication, profiles, addresses
notifications/      Email tasks and logs
analytics/          Sales reporting
dashboard/          Admin dashboard views
chatbot/            AI customer support
blog/               Blog posts
pages/              Static pages (about, contact, FAQ)
api/                REST API endpoints
templates/          HTML templates
static/             CSS, JS, images
```

## License

Copyright 2024 Mac GunJon. All rights reserved.
