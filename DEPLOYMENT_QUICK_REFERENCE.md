# Deployment Quick Reference 🚀

## My Recommendation: Railway + Supabase

**Why?** Works out of the box, $5-10/month, 30-minute setup

---

## Three-Step Deployment

### 1️⃣ Database (5 min) - [supabase.com](https://supabase.com)
```
✓ Create account
✓ New project → "family-football-db"
✓ Copy connection string
✓ Save credentials
```

### 2️⃣ App (10 min) - [railway.app](https://railway.app)
```
✓ Create account (use GitHub)
✓ New Project → Deploy from GitHub
✓ Select your repo
✓ Add environment variables (see below)
✓ Generate domain
```

### 3️⃣ Test (5 min)
```
✓ Visit Railway URL
✓ Test player signup
✓ Login to admin dashboard
✓ Check database in Supabase
```

---

## Environment Variables for Railway

Copy-paste this into Railway → Variables → RAW Editor:

```bash
# Database (from Supabase)
POSTGRES_HOST=db.xxxxxxxxxxxx.supabase.co
POSTGRES_PORT=5432
POSTGRES_DATABASE=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-supabase-password

# Admin
ADMIN_PASSWORD=your-admin-password

# Merky FC (optional initially)
MERKY_FC_USERNAME=your-username
MERKY_FC_PASSWORD=your-password

# WhatsApp (optional initially)
WHATSAPP_GROUP_ID=your-group-id

# Booking (defaults work fine)
BOOKING_PREFERRED_TIME=19:00
BOOKING_AUTO_ENABLED=true
BOOKING_HALF_PITCH_THRESHOLD=14
BOOKING_FULL_PITCH_THRESHOLD=18
```

---

## Alternative Options

### Budget Option: Fly.io + Neon
- **Cost**: Free - $3/month
- **Guide**: See DEPLOYMENT_OPTIONS.md
- **Command**: `flyctl launch`

### Self-Hosted: Any VPS
- **Cost**: €4.50/month (Hetzner)
- **Guide**: See DEPLOYMENT_OPTIONS.md
- **Best for**: Full control

---

## What Works Where?

| Feature | Streamlit Cloud | Railway | Fly.io | VPS |
|---------|----------------|---------|--------|-----|
| Player Signup | ✅ | ✅ | ✅ | ✅ |
| Selenium Bot | ❌ | ✅ | ✅ | ✅ |
| Background Scraper | ❌ | ✅ | ✅ | ✅ |
| WhatsApp | ❌ | ✅ | ✅ | ✅ |
| PostgreSQL | Need external | ✅ | ✅ | ✅ |

**Verdict**: Don't use Streamlit Cloud for this app.

---

## Troubleshooting

### Can't connect to database?
```bash
# Test connection from terminal
psql "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
```

### Build failing?
```bash
# Make sure these files exist in root:
✓ Dockerfile
✓ Pipfile
✓ Pipfile.lock

# Check Railway logs:
Railway → Deployments → Logs
```

### App crashes on startup?
```bash
# Check environment variables are set
Railway → Variables

# Missing: POSTGRES_HOST, POSTGRES_PASSWORD, etc.
```

---

## Cost Comparison

| Option | Database | App | Total/Month |
|--------|----------|-----|-------------|
| **Railway + Supabase** | Free | $5-10 | **$5-10** |
| **DigitalOcean + Supabase** | Free | $7 | **$7** |
| **Fly.io + Neon** | Free | Free-$3 | **Free-$3** |
| **VPS (Hetzner)** | Included | - | **€4.50** |

---

## Next Steps After Deployment

### Week 1
- [ ] Share URL with 2-3 test users
- [ ] Monitor Railway logs daily
- [ ] Verify database records in Supabase
- [ ] Test all features manually

### Week 2
- [ ] Add Merky FC credentials
- [ ] Test manual booking
- [ ] Add WhatsApp group ID
- [ ] Test notifications

### Week 3
- [ ] Enable auto-booking
- [ ] Monitor first auto-booking
- [ ] Full rollout to all players
- [ ] Celebrate! 🎉

---

## Important Files

- **RAILWAY_DEPLOY.md** - Detailed Railway guide
- **DEPLOYMENT_OPTIONS.md** - All platform options
- **Dockerfile** - Already configured
- **railway.json** - Already configured
- **.streamlit/secrets.toml.example** - Local dev config

---

## Support Links

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Supabase**: [supabase.com/docs](https://supabase.com/docs)
- **Your App Health**: `your-url.railway.app/_stcore/health`

---

## Quick Commands

```bash
# Local development
pipenv run streamlit run src/app.py

# Deploy to Railway (after setup)
git push origin main  # Auto-deploys!

# View Railway logs
railway logs

# Deploy to Fly.io
flyctl deploy

# SSH into VPS
ssh root@your-server-ip
```

---

**Ready to deploy? Start with [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)!**
