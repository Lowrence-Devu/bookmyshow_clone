# BookMySeat - BookMyShow Clone

A Django-based movie ticket booking application inspired by BookMyShow. Full-featured with payment integration, email confirmations, and admin analytics.

## Features

- **User registration and authentication**
- **Genre & Language filters** – Filter movies by genre (Action, Comedy, Drama, etc.) and language (Hindi, English, Tamil, etc.)
- **Movie detail pages with YouTube trailers** – Embed trailers on each movie page
- **Seat selection** – Choose seats with visual layout
- **5-minute seat reservation** – Seats held temporarily until payment
- **Payment gateway (Razorpay)** – Integrated payment with success/failure handling. Demo mode when Razorpay keys not set.
- **Ticket email confirmation** – Booking details sent to user email after successful payment
- **Admin dashboard** – Analytics: total revenue, popular movies, busiest theaters, recent bookings
- **Responsive design** – Works on mobile, tablet, and desktop

## Tech Stack

- **Backend:** Django 3.2
- **Database:** SQLite (local) / PostgreSQL (production)
- **Payment:** Razorpay (optional)
- **Deployment:** Render (recommended) or Vercel – see [DEPLOYMENT.md](DEPLOYMENT.md)

## Prerequisites

- Python 3.8+
- pip

## Quick Start

### 1. Clone and navigate to project
```bash
cd /path/to/djnago-bookmyshow-clone-main
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # On macOS/Linux
# Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create superuser (required for admin & dashboard)
```bash
python manage.py createsuperuser
```
**Admin credentials** – use the username/password you create here for:
- Django Admin: `/admin/`
- Admin Dashboard: `/admin/dashboard/`

### 6. Start the development server
```bash
python manage.py runserver
```

### 7. View the app
Open **http://127.0.0.1:8000/** or **http://localhost:8000/**

---

## Add Movies & Theaters

1. Go to `/admin/`
2. Log in with superuser credentials
3. Add **Movies** (include genre, language, trailer_url for YouTube, ticket_price)
4. Add **Theaters** linked to movies
5. Add **Seats** for each theater

---

## Payment Integration (Razorpay)

For live payments, set environment variables:
```bash
export RAZORPAY_KEY_ID=your_key_id
export RAZORPAY_KEY_SECRET=your_key_secret
```

Without these, the app runs in **Demo Mode** – bookings complete without real payment.

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/movies/` | Movie list with genre/language filters |
| `/movies/movie/<id>/` | Movie detail + trailer |
| `/login/` | Login |
| `/register/` | Register |
| `/profile/` | User profile & bookings |
| `/admin/` | Django admin |
| `/admin/dashboard/` | Admin analytics dashboard |

---

## Responsive Design

The app is mobile-friendly with:
- Responsive navbar and grids
- Touch-friendly buttons and forms
- Responsive seat selection layout
- Viewport-optimized layouts

---

## License

MIT
# Updated Sat Feb  7 20:32:50 IST 2026

# Final update
