# Quick Start Guide ⚡

Get up and running in 5 minutes!

## Step 1: Install Dependencies (2 min)

```bash
pipenv install
```

## Step 2: Configure Secrets (2 min)

```bash
# Copy the example file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit with your details
nano .streamlit/secrets.toml
```

**Minimum required configuration:**

```toml
[postgres]
host = "your-db-host"
database = "your-db-name"
user = "your-username"
password = "your-password"

[admin]
password = "your-admin-password"
```

**Optional (for full features):**

```toml
[merky_fc]
username = "your-merky-account"
password = "your-merky-password"

[whatsapp]
group_id = "your-group-id"
```

## Step 3: Run the App (1 min)

```bash
pipenv run streamlit run src/app.py
```

The app will open at `http://localhost:8501`

## First Time Setup

### Database Tables

Tables are created automatically on first run. If you need to manually create them:

```python
from src.database import DatabaseHandler

db = DatabaseHandler(environment='live')
db.create_tables('create_player_table.sql')
db.create_tables('create_signup_table.sql')
db.create_tables('create_booking_table.sql')
db.create_tables('update_booking_table.sql')
db.create_tables('create_available_slots_cache.sql')
```

### Test the System

1. **Test Player Signup:**
   - Go to "Player Signup"
   - Add yourself as a new player
   - Check you appear in the list

2. **Test Admin Dashboard:**
   - Go to "Admin Dashboard"
   - Enter your admin password
   - Explore the 5 tabs

3. **Test WhatsApp (Optional):**
   - Admin Dashboard → Settings tab
   - Click "Send Test Message"
   - Check your WhatsApp group

## What's Working?

✅ **Out of the Box:**
- Player signup/removal
- Database storage
- Admin dashboard
- Booking status display
- Progress bars

⚙️ **Needs Configuration:**
- Automatic booking (needs Merky FC credentials)
- WhatsApp notifications (needs group ID)
- Background scraper (needs Chrome installed)

## Common Issues

### "Can't connect to database"
- Check PostgreSQL is running
- Verify credentials in `secrets.toml`
- Test connection: `psql -h host -U user -d database`

### "Selenium not working"
- Install Chrome: `brew install --cask google-chrome` (Mac)
- Clear cache: `rm -rf ~/.wdm`
- Test manually: Set `headless=False` in booking_bot.py

### "WhatsApp not sending"
- Check WhatsApp Web is logged in
- Verify group ID is correct
- Try pywhatkit manually first

## Next Steps

1. Read [SETUP.md](SETUP.md) for detailed configuration
2. Invite your players to use the app
3. Set up Merky FC credentials for auto-booking
4. Configure WhatsApp for notifications
5. Test end-to-end with a few friends

## Getting Help

- **Setup Issues**: See [SETUP.md](SETUP.md)
- **Usage Questions**: See [README.md](README.md)
- **Bugs**: Open a GitHub issue
- **Admin Tools**: Dashboard → Settings → Database Stats

## Tips

💡 **Start Simple**: Get basic signups working first, then add automation  
💡 **Test Everything**: Use the admin dashboard to test each feature  
💡 **Backup Database**: Before enabling auto-booking  
💡 **Monitor Logs**: Keep terminal open to see errors  
💡 **Gradual Rollout**: Invite a few people first, then scale up  

---

**Ready to revolutionize your family football? Let's go! ⚽**
