# Deploy to Railway - Step by Step 🚂

This is the recommended deployment method. Follow these steps exactly.

## Prerequisites

- GitHub account
- Your code pushed to GitHub
- 10 minutes of time

---

## Step 1: Set Up Database (Supabase) - 5 minutes

### 1.1 Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub (easiest)

### 1.2 Create New Project
1. Click "New Project"
2. Choose organization (or create one)
3. Fill in:
   - **Name**: `family-football-db`
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you (e.g., `London` for UK)
4. Click "Create new project"
5. Wait 2 minutes for database to spin up

### 1.3 Get Connection Details
1. In your project, go to **Settings** (gear icon)
2. Click **Database** in sidebar
3. Scroll to **Connection string**
4. Copy the **URI** (looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`)
5. Save this somewhere safe!

**Your connection details:**
```
Host: db.xxxxxxxxxxxx.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: [the password you created]
```

---

## Step 2: Deploy to Railway - 5 minutes

### 2.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click "Login"
3. Sign in with GitHub (recommended)
4. Authorize Railway

### 2.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. If this is your first time:
   - Click "Configure GitHub App"
   - Choose your account
   - Select "Only select repositories"
   - Choose `family-football-roster`
   - Click "Install"
4. Back in Railway, select your `family-football-roster` repo

### 2.3 Configure Deployment
Railway will automatically detect your `Dockerfile` and start building.

1. Wait for initial build (2-3 minutes)
2. It will likely fail - that's OK! We need to add environment variables

### 2.4 Add Environment Variables

Click on your service → **Variables** tab → **RAW Editor**

Paste this and fill in YOUR values:

```bash
# PostgreSQL (from Supabase)
POSTGRES_HOST=db.xxxxxxxxxxxx.supabase.co
POSTGRES_PORT=5432
POSTGRES_DATABASE=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-supabase-password

# Admin
ADMIN_PASSWORD=your-chosen-admin-password

# Merky FC (add these when ready)
MERKY_FC_USERNAME=your-merky-username
MERKY_FC_PASSWORD=your-merky-password

# WhatsApp (add this when ready)
WHATSAPP_GROUP_ID=your-whatsapp-group-id

# Booking Settings
BOOKING_PREFERRED_TIME=19:00
BOOKING_AUTO_ENABLED=true
BOOKING_HALF_PITCH_THRESHOLD=14
BOOKING_FULL_PITCH_THRESHOLD=18
```

Click **Update Variables**

### 2.5 Redeploy

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Click "⋮" (three dots) → **Restart Deployment**
4. Wait for it to build and deploy (2-3 minutes)

### 2.6 Get Your URL

1. Go to **Settings** tab
2. Scroll to **Domains**
3. Click "Generate Domain"
4. Railway will give you a URL like: `family-football-app-production.up.railway.app`
5. Click the URL to open your app!

---

## Step 3: Initialize Database - 2 minutes

### 3.1 Open Your App
Visit your Railway URL (e.g., `your-app.up.railway.app`)

### 3.2 Tables Auto-Create
The tables will be created automatically on first run! Just visit any page and the app will:
1. Connect to database
2. Create `player_dimensions` table
3. Create `weekly_signups` table
4. Create `booking_references` table
5. Run schema updates

You should see the app load successfully.

### 3.3 Verify Database
Back in Supabase:
1. Go to **Table Editor**
2. You should see 4 tables:
   - `player_dimensions`
   - `weekly_signups`
   - `booking_references`
   - `available_slots_cache`

---

## Step 4: Test Everything - 5 minutes

### 4.1 Test Player Signup
1. Go to your Railway URL
2. Click **Player Signup**
3. Select "New Player"
4. Enter:
   - Name: "Test User"
   - Email: "test@example.com"
5. Click Submit
6. Should see success message!

### 4.2 Test Admin Dashboard
1. Click **Admin Dashboard** in sidebar
2. Enter your admin password
3. Explore all 5 tabs:
   - ✅ Overview
   - ✅ Bookings
   - ✅ Available Slots
   - ✅ Invoices
   - ✅ Settings

### 4.3 Check Database
In Supabase:
1. Go to **Table Editor** → `player_dimensions`
2. You should see "Test User" entry
3. Go to `weekly_signups`
4. You should see a signup record

---

## Step 5: Configure Advanced Features (Optional)

### 5.1 Add Merky FC Credentials
When ready to enable auto-booking:

1. Railway → Your service → **Variables**
2. Add:
   ```
   MERKY_FC_USERNAME=your-actual-username
   MERKY_FC_PASSWORD=your-actual-password
   ```
3. Redeploy

### 5.2 Add WhatsApp Group ID
To enable notifications:

1. Get your WhatsApp group ID (see SETUP.md)
2. Railway → Variables
3. Add:
   ```
   WHATSAPP_GROUP_ID=your-group-id
   ```
4. Test in Admin Dashboard → Settings → "Send Test Message"

---

## Troubleshooting

### "Can't connect to database"
**Solution:**
1. Check Supabase project is active
2. Verify connection string in Railway variables
3. Make sure all 5 POSTGRES_* variables are set
4. Check Supabase **Settings** → **Database** → Connection pooling is enabled

### "Selenium/Chrome not working"
**Solution:**
1. Make sure you're using the `Dockerfile` (not Nixpacks)
2. Railway → Settings → Builder should be "Dockerfile"
3. Redeploy

### "App keeps restarting"
**Solution:**
1. Check Railway **Deployments** → Logs
2. Look for errors
3. Most common: Missing environment variables
4. Make sure Streamlit is listening on `0.0.0.0:8501`

### "Background scraper not working"
**Solution:**
1. Check Railway **Observability** → Metrics
2. Make sure app is not sleeping (should show as "Active")
3. Railway free tier may pause apps - upgrade to Hobby ($5/mo) if needed

### Build fails
**Solution:**
```bash
# Check your Dockerfile is in the root directory
ls -la Dockerfile

# Make sure Pipfile.lock is committed
git add Pipfile.lock
git commit -m "Add Pipfile.lock"
git push

# Railway will auto-redeploy
```

---

## Monitoring Your App

### Railway Dashboard
- **Deployments**: See build logs, deployment history
- **Observability**: 
  - Metrics (CPU, Memory, Network)
  - Logs (real-time application logs)
- **Variables**: Environment configuration
- **Settings**: Domain, deployment settings

### Check App Health
Visit: `your-app-url.railway.app/_stcore/health`

Should return: `ok`

### View Logs
Railway → Your service → **Observability** → **Logs**

Filter by:
- `error` - See errors
- `warning` - See warnings
- `streamlit` - Streamlit specific logs

---

## Cost Breakdown

### Free Tier (Trial Credits)
- Railway gives you $5 free credits
- Typical usage: ~$5-7/month
- Free credits last ~1 month

### After Trial (Hobby Plan)
- **Base**: $5/month subscription
- **Usage**: ~$2-3/month (compute + bandwidth)
- **Total**: ~$7-8/month

### Database (Supabase Free)
- ✅ 500MB storage (plenty for this app)
- ✅ 2GB bandwidth/month
- ✅ Automatic backups
- ✅ Free forever

**Total Monthly Cost: $7-8/month** (after trial)

---

## Updating Your App

### Automatic Deployments
Railway watches your GitHub repo. To update:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Railway automatically:
# 1. Detects the push
# 2. Builds new Docker image
# 3. Deploys new version
# 4. Zero downtime!
```

### Manual Deployment
Railway → Deployments → Click "Deploy" → Select commit

### Rollback
Railway → Deployments → Find previous deployment → "Redeploy"

---

## Next Steps

✅ **You're Live!** Share your Railway URL with players  
✅ **Test Thoroughly** - Try all features  
✅ **Set Up Monitoring** - Check Railway logs daily for first week  
✅ **Add Real Credentials** - Merky FC, WhatsApp when ready  
✅ **Invite Players** - Start small, then scale up  

---

## Support

### Railway Issues
- [Railway Discord](https://discord.gg/railway)
- [Railway Docs](https://docs.railway.app)
- [Railway Status](https://status.railway.app)

### Supabase Issues
- [Supabase Discord](https://discord.supabase.com)
- [Supabase Docs](https://supabase.com/docs)
- [Supabase Status](https://status.supabase.com)

### App Issues
- Check logs in Railway
- Review SETUP.md
- Test locally first: `streamlit run src/app.py`

---

## Success Checklist ✅

Before going live:

- [ ] App accessible via Railway URL
- [ ] Database connected (check Supabase)
- [ ] Player signup works
- [ ] Admin dashboard accessible
- [ ] Tables created in database
- [ ] Test user appears in database
- [ ] Logs show no errors
- [ ] Health check passes
- [ ] Background scraper starts (check logs)
- [ ] Booking status displays correctly

**All checked? You're ready to launch! 🚀**
