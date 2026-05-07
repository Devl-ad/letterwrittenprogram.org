# Smart Writing Finance – Django Dashboard

A full-featured Django member dashboard for the Smart Writing Finance letter-writing platform.

## Features

| Module | Description |
|--------|-------------|
| **Dashboard** | Stats: balance, earnings, letters count, pending payouts |
| **Write Letter** | Submit letters with live word counter |
| **View Letters** | Filter by Pending / Approved / Declined |
| **Letter Detail** | Full letter view with earnings + admin note |
| **Deposit** | Crypto (BTC, USDT, ETH). Banking & cards: Coming Soon |
| **Withdrawal** | Bank transfer. Crypto & cards: Coming Soon |
| **Profile** | Edit personal info + photo |
| **Settings** | Change password + 2FA (TOTP) |
| **Admin Panel** | Approve/decline letters, confirm deposits, process withdrawals |

## Tech Stack

- **Framework:** Django 4.2
- **Auth / 2FA:** django-two-factor-auth + django-otp
- **UI:** Bootstrap 5.3 + Bootstrap Icons
- **Font:** Inter (Google Fonts)
- **Database:** SQLite (dev) → PostgreSQL for production

## Setup

```bash
cd smartwriting
chmod +x setup.sh
./setup.sh
python manage.py runserver
```

## URLs

| URL | View |
|-----|------|
| `/dashboard/` | Main dashboard |
| `/letters/write/` | Write a letter |
| `/letters/` | View all letters |
| `/letters/<id>/` | Letter detail |
| `/payments/deposit/` | Deposit page |
| `/payments/withdrawal/` | Withdrawal page |
| `/account/profile/` | User profile |
| `/account/settings/` | Settings + 2FA |
| `/admin/` | Django admin (approve letters, etc.) |

## Admin Workflow

1. User submits letter → status = **Pending**
2. Admin goes to `/admin/letters/letter/`
3. Select letters → **"Approve selected letters & credit payment"**
4. User's balance is credited $25.00 per letter automatically
5. User can then withdraw their balance

## Crypto Wallets

Update wallet addresses in `smartwriting/settings.py`:

```python
CRYPTO_WALLETS = {
    'BTC': 'your-btc-address',
    'USDT': 'your-usdt-trc20-address',
    'ETH': 'your-eth-address',
}
```

## Responsive Design

- ✅ Desktop: Sidebar + topbar layout
- ✅ Mobile: Hidden sidebar with hamburger + sticky bottom navigation
- ✅ All pages fully responsive

## Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Switch to PostgreSQL
- [ ] Configure email backend (for password reset)
- [ ] Set up static file serving (whitenoise or nginx)
- [ ] Enable HTTPS
# letterwrittenprogram.org
