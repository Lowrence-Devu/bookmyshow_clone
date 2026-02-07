# BookMySeat – Deployment Guide

## Option 1: Render (Recommended)

Render offers a free tier with PostgreSQL and is well-suited for Django.

### Deploy with Blueprint (One-Click)

1. **Push your code to GitHub** (if not already)
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign up
   - Click **New** → **Blueprint**
   - Connect your GitHub repo and select it
   - Render will detect `render.yaml` automatically
   - Click **Apply** – it will create the database and web service

3. **Create admin user** (after first deploy)
   - In Render Dashboard → Your service → **Shell**
   - Run:
     ```bash
     python manage.py createsuperuser
     ```
   - Follow the prompts to set username, email, password

4. **Add movies & data**
   - Visit `https://your-app.onrender.com/admin/`
   - Log in with your superuser credentials
   - Add movies, theaters, and seats

### Environment Variables (optional)

In Render Dashboard → Service → **Environment**:

| Key | Value |
|-----|-------|
| `RAZORPAY_KEY_ID` | Your Razorpay key (for payments) |
| `RAZORPAY_KEY_SECRET` | Your Razorpay secret |
| `DEBUG` | `False` (default) |

### Notes

- **Free tier**: App may sleep after 15 min of inactivity (cold start ~30–60 sec)
- **Media files**: Stored on Render’s disk; consider S3/Cloudinary for production
- **Email**: Set `EMAIL_BACKEND` and SMTP env vars for real email

---

## Option 2: Vercel

Vercel runs Django as a serverless app. **Limitations**: no persistent file storage (media uploads won’t persist), migrations must be run manually.

### Deploy on Vercel

1. **Install Vercel CLI** (optional)
   ```bash
   npm i -g vercel
   ```

2. **Configure environment variables**
   - In [vercel.com](https://vercel.com) → Project → Settings → Environment Variables, add:
   - `DATABASE_URL` – PostgreSQL connection string (e.g. from Render, Neon, Supabase)
   - `SECRET_KEY` – Generate a secure random string
   - `DEBUG` – `False`

3. **Deploy**
   ```bash
   vercel
   ```
   Or connect your GitHub repo in the Vercel dashboard.

4. **Run migrations** (required after deploy)
   - Use a DB client, or run locally:
     ```bash
     DATABASE_URL="your-postgres-url" python manage.py migrate
     ```

### Vercel limitations

- Media uploads are not persistent (use S3/Cloudinary)
- Run migrations manually or via a cron job
- Cold starts may add latency

---

## PostgreSQL Database

If you use Vercel or another host without a built-in DB:

### Free PostgreSQL options

- **Render** – [render.com](https://render.com) → New → PostgreSQL (free tier)
- **Neon** – [neon.tech](https://neon.tech)
- **Supabase** – [supabase.com](https://supabase.com)

Use the connection string as `DATABASE_URL`.

---

## Quick checklist

- [ ] Code pushed to GitHub
- [ ] `DATABASE_URL` set (for non-Render hosts)
- [ ] `SECRET_KEY` set (for non-Render hosts)
- [ ] `DEBUG=False` in production
- [ ] Admin user created (`createsuperuser`)
- [ ] Movies, theaters, seats added in admin

---

## URLs after deploy

| URL | Description |
|-----|-------------|
| `https://your-app.onrender.com/` | Home |
| `https://your-app.onrender.com/movies/` | Movies |
| `https://your-app.onrender.com/admin/` | Django admin |
| `https://your-app.onrender.com/admin/dashboard/` | Analytics dashboard |
