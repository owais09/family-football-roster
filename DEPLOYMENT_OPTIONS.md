# Deployment Options & Recommendations 🚀

## TL;DR - Best Options for Your App

### 🏆 **RECOMMENDED: Railway + Supabase**
- **Why**: Easiest setup, handles Selenium, affordable, PostgreSQL included
- **Cost**: ~$5-10/month
- **Effort**: Low
- **Setup Time**: 30 minutes

### 🥈 **Runner-up: DigitalOcean App Platform + Supabase**
- **Why**: Reliable, good for scaling, Docker support
- **Cost**: ~$7-15/month
- **Effort**: Medium
- **Setup Time**: 1 hour

### 🥉 **Budget Option: Fly.io + Neon Database**
- **Why**: Free tier available, modern platform
- **Cost**: Free - $5/month
- **Effort**: Medium
- **Setup Time**: 1-2 hours

---

## Why NOT Streamlit Cloud?

Your app has features that **won't work** on Streamlit Cloud:

❌ **Background Scraper** - Cloud is stateless, threads don't persist  
❌ **Selenium Bot** - No browser/Chrome available  
❌ **WhatsApp Integration** - No browser access for pywhatkit  
❌ **Long-running Tasks** - Gets killed after inactivity  

**What WOULD work on Streamlit Cloud:**
- ✅ Basic player signup
- ✅ Manual booking (without Selenium)
- ✅ Admin dashboard (view only)
- ✅ Invoice viewing

---

## Detailed Options Analysis

## Option 1: Railway + Supabase ⭐ RECOMMENDED

### What is it?
- **Railway**: Modern platform for deploying apps (supports Docker, Selenium, background tasks)
- **Supabase**: Free PostgreSQL database with generous limits

### Why This Combo?
- ✅ Handles Selenium/Chrome out of the box
- ✅ Background scraper works
- ✅ Easy deployment (connect GitHub)
- ✅ Free PostgreSQL (500MB, 2GB bandwidth/month)
- ✅ Simple pricing ($5/month base + usage)
- ✅ No DevOps knowledge needed

### Setup Steps

#### 1. Database: Supabase (Free)

```bash
# Go to https://supabase.com
# Create account (free)
# Create new project
# Get connection details from Settings → Database
```

Connection string format:
```
postgres://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

#### 2. App Deployment: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli  # or brew install railway

# Login
railway login

# In your project directory
railway init

# Link to GitHub repo (recommended)
railway link

# Set environment variables
railway variables set POSTGRES_HOST=db.[PROJECT-REF].supabase.co
railway variables set POSTGRES_USER=postgres
railway variables set POSTGRES_PASSWORD=[your-password]
railway variables set POSTGRES_DB=postgres
railway variables set POSTGRES_PORT=5432

# Add other secrets (admin password, Merky FC, WhatsApp)
railway variables set ADMIN_PASSWORD=your-admin-password
railway variables set MERKY_FC_USERNAME=your-username
railway variables set MERKY_FC_PASSWORD=your-password
railway variables set WHATSAPP_GROUP_ID=your-group-id

# Deploy
railway up
```

#### 3. Configure Chrome for Selenium

Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "apt-get update && apt-get install -y wget gnupg && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google.list && apt-get update && apt-get install -y google-chrome-stable && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0",
    "healthcheckPath": "/_stcore/health"
  }
}
```

**Cost**: 
- Database: Free (Supabase)
- App: ~$5-10/month (Railway)
- **Total: $5-10/month**

---

## Option 2: DigitalOcean App Platform + Supabase

### Why This?
- ✅ Very reliable platform
- ✅ Docker support (best for Selenium)
- ✅ Easy scaling
- ✅ Good documentation

### Setup Steps

#### 1. Database: Supabase (same as above)

#### 2. Create Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY Pipfile* ./
RUN pip install pipenv && pipenv install --system --deploy

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run Streamlit
CMD ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

#### 3. Deploy to DigitalOcean

```bash
# Install doctl CLI
brew install doctl  # or download from DigitalOcean

# Authenticate
doctl auth init

# Create app from GitHub repo
doctl apps create --spec .do/app.yaml
```

Create `.do/app.yaml`:
```yaml
name: family-football-app
services:
- name: web
  github:
    repo: your-username/family-football-roster
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile
  http_port: 8080
  instance_size_slug: basic-xs
  instance_count: 1
  envs:
  - key: POSTGRES_HOST
    value: db.[PROJECT-REF].supabase.co
  - key: POSTGRES_USER
    value: postgres
  - key: POSTGRES_PASSWORD
    value: ${POSTGRES_PASSWORD}
    type: SECRET
  - key: ADMIN_PASSWORD
    value: ${ADMIN_PASSWORD}
    type: SECRET
```

**Cost**:
- Database: Free (Supabase)
- App: $7/month (Basic plan)
- **Total: $7/month**

---

## Option 3: Fly.io + Neon Database (Budget-Friendly)

### Why This?
- ✅ Generous free tier
- ✅ Modern platform
- ✅ Docker-based
- ✅ Good for small apps

### Setup Steps

#### 1. Database: Neon (Free tier: 10GB)

```bash
# Go to https://neon.tech
# Create project (free)
# Get connection string
```

#### 2. Deploy to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app (creates fly.toml)
flyctl launch

# Set secrets
flyctl secrets set POSTGRES_HOST=your-neon-host
flyctl secrets set POSTGRES_USER=your-user
flyctl secrets set POSTGRES_PASSWORD=your-password
flyctl secrets set POSTGRES_DB=your-db
flyctl secrets set ADMIN_PASSWORD=your-admin-password

# Deploy
flyctl deploy
```

Create `fly.toml`:
```toml
app = "family-football"
primary_region = "lhr"  # London

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024
```

**Cost**:
- Database: Free (Neon)
- App: Free tier (1 shared CPU, 256MB RAM) or $3/month for better specs
- **Total: Free - $3/month**

---

## Option 4: Self-Hosted (VPS) - Most Control

### Platforms:
- **Hetzner**: €4.50/month (Best value)
- **DigitalOcean Droplet**: $6/month
- **Linode**: $5/month
- **Vultr**: $5/month

### Why This?
- ✅ Full control
- ✅ Cheapest for long term
- ✅ Can host database + app together
- ✅ No platform limitations

### Setup Steps

```bash
# 1. Create VPS (Ubuntu 22.04)

# 2. SSH into server
ssh root@your-server-ip

# 3. Install dependencies
apt update && apt upgrade -y
apt install -y python3-pip python3-venv postgresql nginx certbot

# 4. Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt update && apt install -y google-chrome-stable

# 5. Set up PostgreSQL
sudo -u postgres psql
CREATE DATABASE football_db;
CREATE USER football_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE football_db TO football_user;
\q

# 6. Clone your repo
git clone https://github.com/your-username/family-football-roster.git
cd family-football-roster

# 7. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install pipenv
pipenv install --system

# 8. Create .streamlit/secrets.toml
mkdir -p .streamlit
nano .streamlit/secrets.toml
# Add your secrets

# 9. Set up systemd service
sudo nano /etc/systemd/system/football-app.service
```

Add to service file:
```ini
[Unit]
Description=Family Football App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/family-football-roster
Environment="PATH=/root/family-football-roster/venv/bin"
ExecStart=/root/family-football-roster/venv/bin/streamlit run src/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 10. Start service
sudo systemctl daemon-reload
sudo systemctl enable football-app
sudo systemctl start football-app

# 11. Set up Nginx reverse proxy
sudo nano /etc/nginx/sites-available/football-app
```

Add to nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/football-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 12. Set up SSL (optional but recommended)
sudo certbot --nginx -d your-domain.com
```

**Cost**: €4.50 - $6/month (includes database + app)

---

## Comparison Table

| Option | Cost/Month | Ease of Setup | Selenium | Background Scraper | PostgreSQL | Auto-Deploy |
|--------|-----------|---------------|----------|-------------------|------------|-------------|
| **Railway + Supabase** ⭐ | $5-10 | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ✅ Free | ✅ |
| **DigitalOcean + Supabase** | $7 | ⭐⭐⭐⭐ | ✅ | ✅ | ✅ Free | ✅ |
| **Fly.io + Neon** | Free-$3 | ⭐⭐⭐ | ✅ | ✅ | ✅ Free | ✅ |
| **Self-Hosted VPS** | €4.50-6 | ⭐⭐ | ✅ | ✅ | ✅ Included | ❌ |
| **Streamlit Cloud** | Free | ⭐⭐⭐⭐⭐ | ❌ | ❌ | ❌ Need external | ✅ |

---

## My Recommendation 🎯

### For Your Use Case: **Railway + Supabase**

**Why?**
1. **It Just Works**: Selenium, scraper, everything works out of the box
2. **Quick Setup**: 30 minutes from zero to deployed
3. **Auto-Deploy**: Push to GitHub → automatic deployment
4. **Free Database**: Supabase free tier is generous (500MB)
5. **Easy Scaling**: Can upgrade if needed
6. **Good DX**: Nice dashboard, logs, metrics

**Setup Checklist:**
```bash
# 1. Supabase (5 min)
✓ Create account at supabase.com
✓ Create project
✓ Copy connection details

# 2. Railway (10 min)
✓ Create account at railway.app
✓ Connect GitHub repo
✓ Add environment variables
✓ Deploy

# 3. Test (15 min)
✓ Visit your Railway URL
✓ Test player signup
✓ Test admin dashboard
✓ Verify background scraper starts
✓ Check database connections
```

---

## Database Options Deep Dive

### Free PostgreSQL Options

1. **Supabase** ⭐ RECOMMENDED
   - Free tier: 500MB database, 2GB bandwidth
   - Auto backups
   - Easy dashboard
   - PostgreSQL extensions available
   - **Verdict**: Best for most apps

2. **Neon**
   - Free tier: 10GB database (wow!)
   - Serverless (scales to zero)
   - Very fast
   - **Verdict**: Great for growth

3. **ElephantSQL**
   - Free tier: 20MB (too small!)
   - Shared servers
   - **Verdict**: Too limited

4. **Railway PostgreSQL**
   - Free trial, then paid
   - $5/month for 1GB
   - Integrated with Railway
   - **Verdict**: Convenient if using Railway

### Paid PostgreSQL Options

If you outgrow free tiers:

1. **Supabase Pro**: $25/month (8GB)
2. **Neon Scale**: $20/month (unlimited)
3. **Railway**: $5/month (1GB) + usage
4. **DigitalOcean Managed**: $15/month (1GB)

---

## WhatsApp Integration Note ⚠️

Your current `pywhatkit` implementation **requires a browser window**. This won't work in cloud environments.

### Solutions:

#### Option 1: Use WhatsApp Business API (Recommended for Production)
```python
# Use official API instead of pywhatkit
# Libraries: yowsup, whatsapp-business-api
# Cost: Free for low volume
```

#### Option 2: Use Twilio WhatsApp
```python
# Use Twilio's WhatsApp integration
# pip install twilio
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Your message',
    to='whatsapp:+1234567890'
)
# Cost: $0.005/message
```

#### Option 3: Use Alternative Services
- **Vonage** (formerly Nexmo): WhatsApp API
- **MessageBird**: WhatsApp integration
- **Infobip**: Enterprise messaging

I can help you implement any of these if needed!

---

## Action Plan 🎯

### Immediate Next Steps:

1. **Choose your platform** (I recommend Railway)
2. **Set up database** (Supabase free tier)
3. **Create Railway account** and connect GitHub
4. **Add environment variables** in Railway dashboard
5. **Deploy** and test
6. **Monitor** first few days

### Week 1 Goals:
- ✅ App deployed and accessible
- ✅ Database connected
- ✅ Player signups working
- ✅ Admin dashboard accessible

### Week 2 Goals:
- ✅ Selenium booking tested
- ✅ Background scraper running
- ✅ WhatsApp integration working
- ✅ First auto-booking successful

---

## Need Help?

I can create step-by-step deployment scripts for any option you choose. Just let me know which platform you prefer!
