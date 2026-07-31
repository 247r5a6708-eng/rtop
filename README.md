# 🏴‍☠️ Road to One Piece — Placement Prep Web App

An end-to-end placement preparation tracker themed around One Piece, built with Django + SQLite.

## Features
- Register / Login / Logout / Forgot Password (with show/hide password toggle)
- Dashboard with a GitHub-style activity calendar (heatmap), progress bars, current streak, and coin balance
- **Daily Challenge**: one DSA question, one Aptitude problem, and one Technical question rotate in on the
  dashboard every day. Marking them solved updates the Voyage Log calendar and earns coins — just like a
  LeetCode daily streak.
- **Coins & Streak Repair**: earn 5 coins per solved question. Missed a day? Spend 10 coins on the Profile
  page to backfill a missed day in the last 60 days and keep your streak alive (like a streak freeze).
- **One Piece badges**: a themed badge (East Blue Rookie → ... → Wano Warrior) unlocks every 50 active days,
  shown in a gallery on the Profile page.
- **Profile page**: upload a profile picture (shown as the logo in the navbar on every page), edit your bio,
  view your coins/streak/badges.
- DSA section: 25 patterns × 20 questions = **500 questions**, each linking to LeetCode/GeeksforGeeks, with a solved checklist
- Interview section: **Top 150** most-asked questions with a marked/unmarked checklist
- Aptitude section: 25 topics (Basic → Advanced) with concept notes + worked examples + **500 practice problems**
- Technical section: **100 CS concepts** (OOP, DBMS, OS, Computer Networks, Software Engineering, System Design),
  each with its own full learning page (explanation + example + prev/next navigation) and a paginated,
  domain-filterable list — plus **500 technical interview questions**
- "King of the Pirates" crown banner unlocked once every DSA, Aptitude and Technical question is marked solved
- Dark (black & white "Marine steel") theme and Light (warm gold) theme, togglable on every page — including
  the login page — and saved per-user
- Fully responsive (mobile/tablet/desktop) — pure CSS, no framework needed

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data       # loads all 500+150+500+100+500 content
python manage.py createsuperuser # optional, for /admin/
python manage.py runserver
```

Visit http://127.0.0.1:8000/

> **Upgrading from an older copy of this project?** This version adds a `Badge` model and two new
> `Profile` fields (`avatar`, `coins`), plus a `Pillow` dependency for image uploads. Just run
> `pip install -r requirements.txt` then `python manage.py migrate` again — your existing data
> (users, progress, activity log) is preserved; only the new fields/tables are added.

## Notes on security
- CSRF protection enabled on all forms (Django default)
- Passwords hashed via Django's PBKDF2 hasher
- Django's password validators enforce minimum length / common-password checks on registration
- `SECRET_KEY` in `config/settings.py` is a placeholder — **change it** before any real deployment
- Password reset uses Django's console email backend by default (the reset link is printed to the
  terminal running `runserver`) — swap `EMAIL_BACKEND` in `config/settings.py` for a real SMTP backend
  to send actual emails
- Uploaded avatars are stored under `media/avatars/` and served via Django in `DEBUG` mode only —
  for production, serve `MEDIA_ROOT` through your web server / object storage instead
- Before deploying publicly: set `DEBUG = False`, set a real `SECRET_KEY`, restrict `ALLOWED_HOSTS`,
  and enable `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` / `SECURE_SSL_REDIRECT` (reminders are
  commented at the bottom of settings.py)

## Tech stack
Django 5/6, SQLite, Pillow (for avatar uploads), vanilla CSS + JS (no build step), custom-built
calendar heatmap widget (no external JS charting library needed).

## A note on question content
All 2,000+ practice items are seeded via `python manage.py seed_data` (see `core/management/commands/seed_data.py`).
Core patterns/topics include real, well-known LeetCode/GeeksforGeeks problems and concepts curated by hand;
remaining slots in each 20-question set are filled with additional practice prompts linked to the relevant
LeetCode tag page or a Google site-search of GeeksforGeeks (GfG's own `?s=` search parameter no longer works
and was redirecting to their homepage — this has been fixed) so every link is valid and topic-accurate.
You can freely edit `seed_data.py` (or use the Django admin at `/admin/`) to swap in your own exact question lists.

## What's new in this version
- Fixed: theme toggle not working on the login page (it required login before — now works for everyone)
- Fixed: GeeksforGeeks links redirecting to the homepage instead of relevant results
- Dark mode is now a true black & white theme (light mode unchanged)
- Added: Daily Challenge card, coins, streak counter, One Piece milestone badges, streak repair,
  full Profile page with avatar upload, per-concept learning pages with pagination
