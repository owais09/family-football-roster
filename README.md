
# Family Football App ⚽

The **Family Football App** is a comprehensive Streamlit-based application designed to automate and streamline the management of weekly football games. It replaces manual WhatsApp lists and spreadsheet tracking with an integrated system that handles player signups, automatic pitch booking, and end-of-month invoicing.

## 🎯 What Problem Does This Solve?

Previously, managing family football required:
- Manually tracking signups in WhatsApp
- Manually booking pitches when enough players signed up
- Manually entering data into spreadsheets
- Manually sending invoices at month-end

Now, everything is automated:
- Players sign up through the app
- System automatically books pitch when threshold reached (14 or 18 players)
- WhatsApp notifications sent automatically
- Monthly invoices generated with one click

## ✨ Key Features

### 🎮 Player Signup
- **New Players**: Register with name and email
- **Existing Players**: Quick signup via dropdown
- **Guest Players**: Bring friends (linked to host account)
- **Real-time Count**: See live participant count with progress bars
- **Easy Removal**: Remove yourself from the list anytime

### 🤖 Automatic Booking
- **Smart Thresholds**: Auto-books at 14 players (half pitch) or 18 players (full pitch)
- **Web Scraping**: Checks available times on Merky FC HQ website
- **Intelligent Selection**: Picks best time slot based on preferences
- **Instant Confirmation**: Completes booking and stores details
- **WhatsApp Alert**: Notifies group when pitch is booked

### 📱 WhatsApp Integration
- **Signup Notifications**: Updates when players join/leave
- **Booking Confirmations**: Details of booked pitch (date, time, cost)
- **Monthly Invoices**: Automated billing summaries
- **Customizable**: All messages formatted professionally

### 📊 Admin Dashboard
- **Overview Tab**: Current week status, recent bookings, system health
- **Bookings Tab**: Manual booking, history, CSV export
- **Available Slots Tab**: View cached pitch availability, force refresh
- **Invoices Tab**: Generate and send monthly reports
- **Settings Tab**: Configure system, test integrations, view stats

### 🕷️ Background Scraper
- **Automatic Updates**: Refreshes available times every 5 minutes
- **Cache System**: Fast lookups without constant API calls
- **Error Handling**: Robust retry logic
- **Status Monitoring**: Track scraper health in admin dashboard

### 💾 Database Management
- **PostgreSQL Backend**: Reliable data storage
- **Three Main Tables**: Players, signups, bookings
- **Availability Cache**: Scraped pitch times
- **Easy Queries**: Pre-built SQL for common operations

## 🚀 Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

### Prerequisites

- **Python 3.9+**
- **PostgreSQL** database
- **Google Chrome** (for Selenium automation)
- **WhatsApp** access (for notifications)
- **Merky FC HQ** account (for pitch booking)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/family-football-app.git
cd family-football-app

# Install dependencies
pipenv install

# Set up configuration
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials

# Run the app
pipenv run streamlit run src/app.py
```

## 📖 Usage Guide

### For Players

1. Open the app
2. Select player type (New/Existing/Guest)
3. Fill in details
4. Click Submit
5. Receive WhatsApp confirmation

### For Admins

1. Navigate to "Admin Dashboard"
2. Enter admin password
3. Access five tabs:
   - **Overview**: Monitor current status
   - **Bookings**: Manage pitch reservations
   - **Available Slots**: Check pitch availability
   - **Invoices**: Generate monthly bills
   - **Settings**: Configure system

## 📁 Project Structure

```plaintext
family-football-roster/
├── src/
│   ├── app.py                    # Main Streamlit application
│   ├── database.py               # PostgreSQL database handler
│   ├── signups.py                # Player signup logic
│   ├── helper.py                 # Validation utilities
│   ├── booking_bot.py            # Selenium automation for Merky FC
│   ├── booking_manager.py        # Booking orchestration
│   ├── whatsapp.py               # WhatsApp notifications
│   ├── invoice_generator.py      # Monthly invoice creation
│   ├── scraper_service.py        # Background availability scraper
│   └── sql/                      # SQL query files
│       ├── create_*.sql          # Table creation
│       ├── update_*.sql          # Schema migrations
│       ├── get_*.sql             # Data queries
│       └── insert_*.sql          # Data insertion
├── .streamlit/
│   └── secrets.toml              # Configuration (not in git)
├── Pipfile                       # Python dependencies
├── README.md                     # This file
├── SETUP.md                      # Detailed setup guide
└── .gitignore                    # Git ignore rules
```

## 🔧 Technical Details

### Architecture

```
User Interface (Streamlit)
    ↓
Booking Manager → Monitors signups
    ↓
Booking Bot → Selenium automation
    ↓
Merky FC Website → Books pitch
    ↓
Database → Stores confirmation
    ↓
WhatsApp → Notifies group
```

### Key Components

**booking_bot.py**: Selenium-based web scraper
- Navigates Merky FC HQ website
- Filters by pitch type
- Extracts available times
- Completes booking process

**booking_manager.py**: Business logic orchestrator
- Monitors signup thresholds
- Selects optimal time slots
- Triggers booking bot
- Stores results in database

**scraper_service.py**: Background task manager
- Runs on schedule (every 5 min)
- Caches availability data
- Reduces booking latency

**invoice_generator.py**: Billing system
- Queries monthly data
- Calculates per-player costs
- Formats reports
- Sends via WhatsApp

**whatsapp.py**: Notification system
- Signup updates
- Booking confirmations
- Monthly invoices
- Custom messages

## 🎬 How It Works

### Player Signup Flow

1. Player opens app and selects player type
2. Fills in name/email (or selects from dropdown)
3. Clicks Submit
4. System validates input
5. Adds to database and increments counter
6. Sends WhatsApp update to group
7. Checks if threshold reached (14 or 18)
8. If yes, triggers automatic booking

### Automatic Booking Flow

1. Threshold reached (14 or 18 players)
2. System checks if pitch already booked
3. If not, scrapes available times from Merky FC
4. Selects best time based on preferences
5. Logs into Merky FC account
6. Completes booking process
7. Extracts confirmation number
8. Stores in database
9. Sends WhatsApp confirmation with details

### Monthly Invoice Flow

1. Admin selects month/year in dashboard
2. System queries all bookings for that month
3. Joins with signup data to get player attendance
4. Calculates cost per player per session
5. Aggregates totals
6. Formats as readable report
7. Sends via WhatsApp or exports as CSV

## 🔮 Future Enhancements

### Planned Features
- Email notifications as alternative to WhatsApp
- Player profiles with participation history
- Automated payment collection (Stripe/PayPal)
- Mobile app version (React Native)
- Waitlist functionality when pitch is full
- Multi-sport support (basketball, tennis, etc.)
- Weather integration (auto-cancel if rain)
- Player ratings and team balancing
- Tournament mode with brackets

### Potential Improvements
- Machine learning for optimal time prediction
- Dynamic pricing based on demand
- Integration with calendar apps
- SMS notifications as backup
- Multi-language support
- Dark mode UI
- Progressive Web App (PWA)
- Push notifications

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Family Football Team

## 🙏 Acknowledgments

- Merky FC HQ for the pitch
- Streamlit for the amazing framework
- The Python community for excellent libraries

## 📞 Support

Having issues? Check these resources:

1. [SETUP.md](SETUP.md) - Detailed setup guide
2. [GitHub Issues](https://github.com/your-repo/issues) - Report bugs
3. Admin Dashboard → Settings → Test integrations

## ⚠️ Disclaimer

This application automates booking on Merky FC HQ website. Use responsibly and in accordance with their terms of service. The authors are not responsible for any issues arising from automated bookings.

---

**Made with ❤️ for family football**
