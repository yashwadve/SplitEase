# SplitEase

A Django web app for splitting group expenses fairly and settling up with the fewest possible payments — built for roommates, trips, and any shared-expense group.

## Features

- **Groups** — create groups, add/remove members, upload a cover image
- **Expenses** — log expenses with equal, custom-amount, percentage, or share-based splits
- **Smart settle-up** — a debt-simplification algorithm reduces a tangle of individual debts down to the minimum number of payments needed to clear every balance
- **Balance tracking** — per-group and overall "you owe / you're owed" balances on the dashboard
- **Settlement history** — record and track payments between members
- **Notifications** — get notified when added to a group
- **Profiles** — avatar, display name, and UPI ID for easy pay-back

## Tech stack

- **Backend:** Django
- **Frontend:** Bootstrap 5, Bootstrap Icons, vanilla JS
- **Database:** (set via `DATABASES` in `settings.py`)

## Project structure

```
splitease/
├── core/            # Landing page, dashboard
├── accounts/        # Custom user model, auth, profile
├── groups/          # Groups & membership
├── expenses/        # Expenses, categories, splits
├── settlements/      # Balance calculation & debt simplification
├── notifications/   # In-app notifications
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    └── <app>/*.html
```

## Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd splitease

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (optional, for /admin)
python manage.py createsuperuser

# Run the dev server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to view the app.

## Settings notes

- Add `MEDIA_URL` / `MEDIA_ROOT` for group images, receipts, and avatars.
- Add to `settings.py` so error messages render as Bootstrap's `alert-danger`:
  ```python
  from django.contrib.messages import constants
  MESSAGE_TAGS = {constants.ERROR: 'danger'}
  ```

## How the settle-up algorithm works

1. Each expense's amount is credited to the payer and debited (split) across participants.
2. Completed settlements adjust balances the same way.
3. Net balances are separated into creditors (owed money) and debtors (owe money).
4. Debtors and creditors are greedily matched off, generating the minimum number of transactions needed to zero out every balance — instead of naively repaying each individual expense split one by one.

## Status

All core flows (auth, groups, expenses with all split types, settlements, notifications) are built and manually tested through the UI.
