# Setup Guide - Football Booking Automation System

## Prerequisites

- Python 3.9+
- PostgreSQL database
- Google Chrome (for Selenium)
- WhatsApp Web access
- Merky FC HQ account

## Installation Steps

### 1. Install Dependencies

```bash
# Install pipenv if not already installed
pip install pipenv

# Install project dependencies
pipenv install

# Activate the virtual environment
pipenv shell
```

### 2. Configure Secrets

Create a `.streamlit/secrets.toml` file based on the example:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and fill in your actual credentials:

- **PostgreSQL**: Your database connection details
- **Admin**: Password for admin dashboard access
- **Merky FC**: Your Merky FC HQ website credentials
- **WhatsApp**: Your WhatsApp group ID
- **Booking**: Configure thresholds and preferences

### 3. Database Setup

The database tables will be created automatically when you run the app for the first time. However, if you have an existing database, you need to run the migration:

```python
# In Python shell or script
from database import DatabaseHandler

db = DatabaseHandler(environment='live')

# Create base tables
db.create_tables('create_player_table.sql')
db.create_tables('create_signup_table.sql')
db.create_tables('create_booking_table.sql')

# Update schema for new features
db.create_tables('update_booking_table.sql')
db.create_tables('create_available_slots_cache.sql')
```

### 4. WhatsApp Group ID Setup

To get your WhatsApp group ID:

1. Open WhatsApp Web
2. Right-click on your group
3. Inspect element
4. Find the group ID in the data attributes
5. Add it to `secrets.toml`

### 5. Chrome WebDriver

The Selenium bot will automatically download ChromeDriver using `webdriver-manager`. Ensure you have Google Chrome installed.

### 6. Run the Application

```bash
streamlit run src/app.py
```

## Features Overview

### Player Signup
- New players can register with name and email
- Existing players can select from dropdown
- Guest players can be added (linked to host)
- Automatic validation of email and names

### Automatic Booking
- Monitors signup count in real-time
- Triggers booking at 14 players (half pitch) or 18 players (full pitch)
- Scrapes available times from Merky FC HQ
- Books pitch automatically
- Sends WhatsApp confirmation

### WhatsApp Integration
- Auto-notifications when players sign up/remove
- Booking confirmation messages
- End-of-month invoice summaries

### Admin Dashboard
- **Overview**: Current week status, recent bookings, scraper status
- **Bookings**: Manual booking, booking history, CSV export
- **Available Slots**: View cached availability, refresh scraper
- **Invoices**: Generate monthly reports, send via WhatsApp
- **Settings**: View configuration, test WhatsApp, database stats

### Background Scraper
- Runs every 5 minutes (configurable)
- Caches available pitch times
- Reduces API calls during booking

## Configuration Options

### Booking Thresholds

Edit in `.streamlit/secrets.toml`:

```toml
[booking]
half_pitch_threshold = 14  # Players needed for half pitch
full_pitch_threshold = 18   # Players needed for full pitch
preferred_time = "19:00"    # Preferred booking time
auto_book_enabled = true    # Enable/disable auto-booking
```

### Scraper Interval

Edit in `src/scraper_service.py`:

```python
service = ScraperService(db, scrape_interval_minutes=5)
```

## Troubleshooting

### Selenium Issues

If the Selenium bot fails:

1. Check Chrome is installed
2. Update Chrome to latest version
3. Clear ChromeDriver cache: `rm -rf ~/.wdm`
4. Run with `headless=False` for debugging

### WhatsApp Issues

If WhatsApp messages don't send:

1. Ensure WhatsApp Web is logged in
2. Check group ID is correct
3. Try sending a test message from admin dashboard
4. Check `pywhatkit` has browser access

### Database Issues

If tables don't create:

1. Check PostgreSQL is running
2. Verify credentials in `secrets.toml`
3. Check user has CREATE TABLE permissions
4. Manually run SQL files from `src/sql/`

### Background Scraper

If scraper doesn't start:

1. Check it's enabled in admin dashboard
2. Look for errors in console
3. May not work on Streamlit Cloud (stateless)
4. Consider using GitHub Actions as alternative

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Deploy on [share.streamlit.io](https://share.streamlit.io)
3. Add secrets in Streamlit Cloud dashboard
4. Note: Background scraper may not work (use GitHub Actions)

### Alternative: Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

COPY Pipfile* ./
RUN pip install pipenv && pipenv install --system --deploy

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py"]
```

## Maintenance

### Monthly Tasks

1. Review invoices in admin dashboard
2. Send invoices via WhatsApp
3. Export booking history as CSV
4. Backup database

### Weekly Tasks

1. Monitor signup counts
2. Verify automatic bookings
3. Check scraper status
4. Test WhatsApp notifications

## Support

For issues or questions:

1. Check this SETUP.md file
2. Review the main README.md
3. Check error messages in Streamlit app
4. Review logs in terminal

## Security Notes

- Never commit `.streamlit/secrets.toml` to git (already in `.gitignore`)
- Keep Merky FC credentials secure
- Use strong admin password
- Regularly rotate passwords
- Backup database regularly
