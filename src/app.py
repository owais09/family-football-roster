from gc import disable

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from database import DatabaseHandler
from signups import add_player_signup,is_already_signed_up
from helper import validate_name_email,validate_email, validate_name
from booking_manager import BookingManager
from whatsapp import WhatsAppNotifier
from invoice_generator import InvoiceGenerator
from scraper_service import get_scraper_service, scrape_now

# Initialize the database handler and services (cached for performance)
@st.cache_resource
def get_database_handler():
    """Get or create database handler (singleton)"""
    environment = 'live'
    return DatabaseHandler(environment=environment)

@st.cache_resource
def get_services(_db):
    """Get or create service instances (singleton)"""
    booking_mgr = BookingManager(_db)
    whatsapp = WhatsAppNotifier(_db)
    invoice_gen = InvoiceGenerator(_db)
    return booking_mgr, whatsapp, invoice_gen

# Initialize (only once thanks to caching)
try:
    with st.spinner("Connecting to database..."):
        db = get_database_handler()
    with st.spinner("Initializing services..."):
        booking_manager, whatsapp_notifier, invoice_generator = get_services(db)
except Exception as e:
    st.error(f"⚠️ Failed to initialize app: {str(e)}")
    st.info("Please check your database connection and environment variables.")
    st.stop()

# No background scraper - we'll scrape on-demand when admin needs it
# This is more efficient and works on all platforms
scraper_service = None

# Set up page config
st.set_page_config(
    page_title="Family Football App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main app
with st.container():
    st.markdown("""
        <style>
            .header-container {
                text-align: center;
                background-color: #000000;
                color: white;
                padding: 15px;
                border-radius: 10px;
                border: 5px solid #6699cc;
            }
            .header-container h1 {
                font-size: clamp(1.2rem, 4vw, 3rem);  /* Scales between 1.5rem and 3rem */
            }
            .header-container h3 {
                font-size: clamp(1rem, 2.0vw, 1.2rem);  /* Scales between 1rem and 1.5rem */
            }
        </style>

        <div class="header-container">
            <h1>⚽ Family Football App ⚽</h1>
            <h3>Welcome to the Family Football Signup App! 🎉</h3>
        </div>
    """, unsafe_allow_html=True)

# Initialize database schema (only runs once)
@st.cache_resource
def init_database_schema(_db):
    """Initialize database tables and schema (runs once)"""
    tables_to_create = [
        'create_player_table.sql',
        'create_signup_table.sql',
        'create_booking_table.sql',
        'update_booking_table.sql',
        'create_available_slots_cache.sql',
        'alter_players_add_guest_host.sql'  # Add guest-host relationship
    ]
    
    for table_file in tables_to_create:
        try:
            _db.create_tables(table_file)
        except Exception:
            pass  # Table/column may already exist
    
    return True

# Run schema initialization (cached, so only happens once)
try:
    with st.spinner("Setting up database schema..."):
        init_database_schema(db)
except Exception as e:
    st.warning(f"Schema initialization warning: {str(e)}")
    # Continue anyway - tables might already exist


# --- Sidebar ---
# st.sidebar.header("Navigation")
# menu = st.sidebar.radio("Go to", ["Player Signup", "Admin Dashboard"])

current_date = datetime.now()

current_year = current_date.isocalendar()[0]
current_week_num = current_date.isocalendar()[1]

current_week = f"{current_year}-W{current_week_num:02d}"

# Cache participant data for 10 seconds to improve performance
@st.cache_data(ttl=10)
def get_current_participants(week):
    signups = db.fetch_signups(week)
    return pd.DataFrame(signups, columns=["name", "email_id"]).dropna()

@st.cache_data(ttl=10)
def get_current_booking_status(week):
    return booking_manager.get_booking_status(week)

participants_df = get_current_participants(current_week)
participants = participants_df.values.tolist() if not participants_df.empty else []

# Get booking status
booking_status = get_current_booking_status(current_week)

with st.container():
    st.markdown(f"""
        <style>
            .participant-header {{
                text-align: center; 
                color: #80dfff; 
                font-weight: bold;
                font-size: 1.1rem;  /* Default size for desktops */
                margin-top: 10px;
            }}

            /* Adjust font size for tablets */
            @media screen and (max-width: 768px) {{
                .participant-header {{
                    font-size: 1rem;  /* Slightly smaller text for tablets */
                }}
            }}

            /* Further reduce font size on mobile screens */
            @media screen and (max-width: 480px) {{
                .participant-header {{
                    font-size: 0.9rem;  /* Smaller text for mobile phones */
                }}
            }}
        </style>
        <p class="participant-header">
             Participants Signed Up for Week {current_week}: {len(participants)}
        </p>
    """, unsafe_allow_html=True)

st.sidebar.header("Navigation")
menu = st.sidebar.radio("Go to", ["Player Signup", "Admin Dashboard"])


# --- Player Signup Section ---
if menu == "Player Signup":
    # Cache player list for 30 seconds to avoid constant DB queries
    @st.cache_data(ttl=30)
    def get_all_players():
        return db.get_all_players_in_db()
    
    all_player_signup = get_all_players()
    
    # Signup form - using container for consistent styling with dynamic fields
    with st.container():
        st.markdown("""
            <style>
                .subheader {
                    font-size: 1.5rem;
                    color: #6B8E23;
                    text-align: center;
                    font-weight: bold;
                }
                @media screen and (max-width: 768px) {
                    .subheader { font-size: 1.2rem; }
                }
                @media screen and (max-width: 480px) {
                    .subheader { font-size: 1rem; }
                }
            </style>
            <p class="subheader">Signup to Weekly Football ✅</p>
        """, unsafe_allow_html=True)

        # Selectbox for player type
        choice = st.selectbox("", ["Select", "New Player", "Existing Player", "Guest"], index=0)

        name = 'Placeholder'
        email = 'Placeholder'
        # Handle form fields based on player type
        if choice == 'New Player':
            name = st.text_input("", placeholder="Enter your name", max_chars=50)
            email = st.text_input("", placeholder="Enter your Email", max_chars=50)
        elif choice == 'Existing Player':
            email = st.selectbox("", all_player_signup['email_id'], index=None)
            if email:
                name = str(all_player_signup['name'][all_player_signup['email_id']==email].values[0])
        elif choice == 'Guest':
            name = st.text_input("", placeholder="Enter guest name",max_chars=50)
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.selectbox("Who is bringing this guest?", all_player_signup['email_id'], index=None, 
                               help="Select the player who is responsible for this guest")
        
        # Submit button
        submitted = st.button("Submit", key="signup_submit", use_container_width=True)
    
    if submitted:
        if name =='Placeholder' and email == 'Placeholder':
            st.error('Signup Type missing. Choose player type')
        elif not name or not email:
            st.error("Name and email are required!")
        elif choice == 'New Player' and (not validate_email(email) or not validate_name(name)):
            st.error("Invalid name or email. Please try again.")
        else:
            # For guests, get the host's player_id
            host_player_id = None
            if choice == 'Guest':
                host_player_id = db.get_player_id(email)
                if host_player_id:
                    host_player_id = host_player_id[0]  # Extract ID from tuple
            
            add_player_signup(db, choice, name, current_week, email, host_player_id=host_player_id)
            
            # Refresh participant count
            participants = db.fetch_signups(current_week)
            current_count = len(participants)
            
            # Send WhatsApp notification
            try:
                whatsapp_notifier.send_signup_update(
                    name, "signed up", current_week, current_count, 
                    booking_status['threshold_half'], booking_status['threshold_full']
                )
            except Exception as e:
                st.warning(f"Could not send WhatsApp notification: {e}")
            
            # Check if automatic booking should be triggered
            try:
                booking_result = booking_manager.check_and_book(current_week)
                if booking_result and booking_result.get('status') != 'already_booked':
                    st.balloons()
                    
                    # Handle different booking types
                    if booking_result.get('status') == 'two_thirds_booked':
                        st.success("🎉 2 Third Pitches automatically booked!")
                    else:
                        st.success("🎉 Pitch automatically booked!")
                    
                    # Prepare booking details for WhatsApp
                    booking_details = {
                        'date': booking_result['slot']['date'],
                        'time': booking_result['slot']['time'],
                        'pitch_type': booking_result['slot']['pitch_type'],
                        'player_count': booking_result['player_count'],
                        'cost_per_player': booking_result['cost_per_player'],
                        'total_cost': booking_result['total_cost'],
                    }
                    
                    # Handle confirmation number (different for single vs 2 thirds)
                    if booking_result.get('status') == 'two_thirds_booked':
                        # Multiple confirmations
                        conf_numbers = [c.get('confirmation', {}).get('confirmation_number', 'N/A') 
                                      for c in booking_result.get('confirmations', [])]
                        booking_details['confirmation_number'] = ', '.join(conf_numbers)
                    else:
                        # Single confirmation
                        booking_details['confirmation_number'] = booking_result.get('confirmation', {}).get('confirmation_number', 'N/A')
                    
                    whatsapp_notifier.send_booking_confirmation(booking_details)
            except Exception as e:
                st.warning(f"Automatic booking check failed: {e}")
            
            st.rerun()
    
    with st.form("removal_form"):
        st.markdown("""
            <style>
                .subheader-red {
                    font-size: 1.5rem;
                    color: #B55A4A; /* Dull Red */
                    text-align: center;
                    font-weight: bold;
                }
                @media screen and (max-width: 658px) {
                    .subheader-red { font-size: 1.2rem; }
                }
                @media screen and (max-width: 400px) {
                    .subheader-red { font-size: 1rem; }
                }
            </style>
            <p class="subheader-red">Remove name from weekly signup 🚫</p>
        """, unsafe_allow_html=True)

        player_email_to_delete = st.selectbox("", participants_df['email_id'].to_list(), index=None)
        delete_button = st.form_submit_button("Remove Player")
        if delete_button:
            player_id_list = db.get_player_id(player_email_to_delete)
            player_id = player_id_list[0]
            if is_already_signed_up(db,player_id,current_week):
                # Get player name before deletion
                player_name = participants_df[participants_df['email_id'] == player_email_to_delete]['name'].values[0]
                
                db.delete_signups(player_email_to_delete,  current_week)
                
                # Send WhatsApp notification
                try:
                    participants = db.fetch_signups(current_week)
                    current_count = len(participants)
                    whatsapp_notifier.send_signup_update(
                        player_name, "removed themselves", current_week, current_count,
                        booking_status['threshold_half'], booking_status['threshold_full']
                    )
                except Exception as e:
                    st.warning(f"Could not send WhatsApp notification: {e}")
                
                st.rerun()
            else:
                st.error('No record found')
            #
            # WhatsApp Notification
            # player_list = "\n".join([f"- {p[0]}" for p in fetch_signups(current_week)])
            # message = f"New signup for Week {current_week}!\n\nCurrent Participants:\n{player_list}"
            # send_whatsapp_message(message)
            # st.info("The updated player list has been sent to WhatsApp!")


    # Show participant list
    with st.container():
        st.markdown(f"""
            <style>
                .participant-header-second {{
                    text-align: center; 
                    color: #FFFFFF; 
                    font-weight: bold;
                    font-size: 1.1rem;  /* Default size for desktops */
                    margin-top: 10px;
                }}

                /* Adjust font size for tablets */
                @media screen and (max-width: 768px) {{
                    .participant-header-second {{
                        font-size: 1rem;  /* Slightly smaller text for tablets */
                    }}
                }}

                /* Further reduce font size on mobile screens */
                @media screen and (max-width: 480px) {{
                    .participant-header-second {{
                        font-size: 0.9rem;  /* Smaller text for mobile phones */
                    }}
                }}
            </style>
            <p class="participant-header-second">
                 Participants Signed Up for Week {current_week}
            </p>
        """, unsafe_allow_html=True)

    if participants:

        players_df = pd.DataFrame(participants, columns=["Name", "Email"])
        players_df.index += 1
        st.write(players_df)
    else:
        st.write("No one has signed up yet! Be the first!")
    
    # Show booking status with progress bars (moved to bottom)
    st.markdown("""
        <style>
            /* Center and bold metric labels and values */
            .stMetric label {
                text-align: center !important;
                justify-content: center !important;
                font-weight: bold !important;
            }
            .stMetric [data-testid="stMetricValue"] {
                text-align: center !important;
                justify-content: center !important;
                font-weight: bold !important;
            }
            /* Center and bold captions */
            .stCaption {
                text-align: center !important;
                font-weight: bold !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("1 Third Pitch (14 players)", f"{booking_status['current_count']}/{booking_status['threshold_half']}")
        if booking_status['players_needed_half'] > 0:
            st.progress(booking_status['current_count'] / booking_status['threshold_half'])
            st.caption(f"{booking_status['players_needed_half']} more needed")
        else:
            st.progress(1.0)
            st.caption("✅ Ready to book!")
    
    with col2:
        st.metric("2 Third Pitches (18 players)", f"{booking_status['current_count']}/{booking_status['threshold_full']}")
        if booking_status['players_needed_full'] > 0:
            st.progress(booking_status['current_count'] / booking_status['threshold_full'])
            st.caption(f"{booking_status['players_needed_full']} more for 2 thirds")
        else:
            st.progress(1.0)
            st.caption("✅ Ready to book 2 thirds!")
    
    # Show booking confirmation if exists
    if booking_status['is_booked']:
        st.success("⚽ Pitch already booked for this week!")

# --- Admin Dashboard Section ---
if menu == "Admin Dashboard":
    st.header("🔐 Admin Dashboard")
    
    # Admin password protection
    admin_password = st.text_input("Enter Admin Password", type="password")
    
    from config import get_admin_password
    
    if admin_password == get_admin_password():
        st.success("Welcome, Admin!")
        
        # Create tabs for different admin sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "⚽ Bookings", 
            "🔍 Available Slots",
            "💰 Invoices",
            "⚙️ Settings"
        ])
        
        # TAB 1: Overview
        with tab1:
            st.subheader("Weekly Overview")
            
            # Current week status
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Signups", booking_status['current_count'])
            with col2:
                status_text = "✅ Booked" if booking_status['is_booked'] else "⏳ Pending"
                st.metric("Booking Status", status_text)
            with col3:
                if booking_status['status'] == 'ready_full':
                    st.metric("Pitch Type", "Full Pitch Ready")
                elif booking_status['status'] == 'ready_half':
                    st.metric("Pitch Type", "Half Pitch Ready")
                else:
                    st.metric("Players Needed", booking_status['players_needed_half'])
            
            # Recent bookings
            st.subheader("Recent Bookings")
            bookings = db.fetch_bookings()
            if bookings:
                booking_df = pd.DataFrame(bookings, columns=["Week", "Date", "Amount", "Players"])
                booking_df = booking_df.head(10)
                st.dataframe(booking_df, use_container_width=True)
                
                total_sum = booking_df['Amount'].sum()
                st.metric("Total (Last 10 bookings)", f"£{total_sum:.2f}")
            else:
                st.info("No bookings recorded yet.")
            
            # Availability Cache Status
            st.subheader("Availability Cache")
            cached_slots = db.get_available_slots(None)
            if cached_slots and len(cached_slots) > 0:
                # Get latest scrape time
                latest_scrape = cached_slots[0][6] if len(cached_slots[0]) > 6 else None
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Cached Slots", len(cached_slots))
                with col2:
                    if latest_scrape:
                        age = datetime.now() - latest_scrape
                        age_str = f"{int(age.total_seconds() / 60)} min ago"
                        st.metric("Last Scraped", age_str)
                st.info("💡 Slots are scraped automatically when you open the 'Available Slots' tab")
            else:
                st.info("No slots cached yet. Open the 'Available Slots' tab to scrape.")
        
        # TAB 2: Bookings Management
        with tab2:
            st.subheader("Booking Management")
            
            # Manual booking form
            st.markdown("### 📝 Manual Booking")
            
            st.warning("⚠️ **Important:** Clicking 'Book Pitch' will ACTUALLY book on Merky FC HQ website. This is NOT a test!")
            
            # Get available slots for selection
            booking_pitch_filter = st.selectbox("Select Pitch Type First", ["half_pitch", "full_pitch", "third_pitch"], key="booking_pitch_filter")
            available_for_booking = db.get_available_slots(booking_pitch_filter)
            
            if available_for_booking and len(available_for_booking) > 0:
                # Show available slots to choose from
                slot_options = []
                slot_map = {}
                for idx, slot in enumerate(available_for_booking):
                    # slot structure: (slot_id, date, time, pitch_type, price, available, scraped_at)
                    date_str = slot[1].strftime('%Y-%m-%d') if hasattr(slot[1], 'strftime') else str(slot[1])
                    time_str = slot[2].strftime('%H:%M') if hasattr(slot[2], 'strftime') else str(slot[2])
                    price = float(slot[4])
                    
                    display_text = f"{date_str} at {time_str} - £{price:.2f}"
                    slot_options.append(display_text)
                    slot_map[display_text] = {
                        'date': date_str,
                        'time': time_str,
                        'pitch_type': slot[3],
                        'price': price
                    }
                
                st.info(f"📅 {len(slot_options)} available slots found. Select one to book:")
                
                with st.form("manual_booking_form"):
                    selected_slot_display = st.selectbox("Choose Available Slot", slot_options)
                    selected_slot = slot_map[selected_slot_display]
                    
                    player_count = st.number_input("Expected Players", min_value=1, value=14)
                    
                    st.markdown(f"**You are about to book:**")
                    st.markdown(f"- Date: {selected_slot['date']}")
                    st.markdown(f"- Time: {selected_slot['time']}")
                    st.markdown(f"- Pitch: {selected_slot['pitch_type']}")
                    st.markdown(f"- Total Cost: £{selected_slot['price']:.2f}")
                    st.markdown(f"- Cost per player: £{selected_slot['price']/player_count:.2f}")
                    
                    manual_book_button = st.form_submit_button("🚨 Book Pitch on Merky FC (REAL BOOKING)")
                    
                    if manual_book_button:
                        booking_date = selected_slot['date']
                        booking_time = selected_slot['time']
                        pitch_type = selected_slot['pitch_type']
            else:
                st.info("No available slots in cache. Click '🔄 Refresh Now' in the 'Available Slots' tab to scrape latest availability.")
                
                # Fallback: manual date/time entry
                st.markdown("### Or Enter Date/Time Manually (Use with caution)")
                with st.form("manual_booking_form_fallback"):
                    col1, col2 = st.columns(2)
                    with col1:
                        booking_date = st.date_input("Booking Date", value=datetime.now() + timedelta(days=7))
                        booking_time = st.time_input("Booking Time", value=datetime.strptime("19:00", "%H:%M").time())
                    with col2:
                        pitch_type = st.selectbox("Pitch Type", ["half_pitch", "full_pitch", "third_pitch"])
                        player_count = st.number_input("Expected Players", min_value=1, value=14)
                    
                    manual_book_button = st.form_submit_button("⚠️ Book Pitch (May fail if not available)")
                    
                    if manual_book_button:
                        booking_date = booking_date.strftime('%Y-%m-%d')
                        booking_time = booking_time.strftime('%H:%M')
            
            # Booking execution (only runs if button was clicked)
            if 'manual_book_button' in locals() and manual_book_button:
                
                with st.spinner("Booking pitch on Merky FC HQ..."):
                    try:
                        result = booking_manager.manual_book(
                            booking_date if isinstance(booking_date, str) else booking_date.strftime('%Y-%m-%d'),
                            booking_time if isinstance(booking_time, str) else booking_time.strftime('%H:%M'),
                            pitch_type,
                            current_week,
                            player_count
                        )
                            
                        if result:
                            st.success("✅ Booking successful on Merky FC HQ!")
                            st.json(result)
                            
                            # Send WhatsApp notification
                            booking_details = {
                                'date': booking_date if isinstance(booking_date, str) else booking_date.strftime('%Y-%m-%d'),
                                'time': booking_time if isinstance(booking_time, str) else booking_time.strftime('%H:%M'),
                                'pitch_type': pitch_type,
                                'player_count': player_count,
                                'cost_per_player': result.get('cost_per_player', 0),
                                'total_cost': result.get('total_cost', 0),
                                'confirmation_number': result['confirmation'].get('confirmation_number')
                            }
                            whatsapp_notifier.send_booking_confirmation(booking_details)
                        else:
                            st.error("❌ Booking failed on Merky FC website")
                    except Exception as e:
                        st.error(f"Error during booking: {str(e)}")
            
            # Booking history
            st.markdown("### 📚 Booking History")
            all_bookings = db.fetch_bookings()
            if all_bookings:
                bookings_df = pd.DataFrame(all_bookings, columns=["Week", "Date", "Amount", "Players"])
                st.dataframe(bookings_df, use_container_width=True)
                
                # Export option
                csv = bookings_df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"bookings_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No bookings yet")
        
        # TAB 3: Available Slots
        with tab3:
            st.subheader("Available Pitch Times")
            
            # Check if we need to auto-scrape (cache empty or stale)
            cached_slots_check = db.get_available_slots(None)
            should_auto_scrape = False
            
            if not cached_slots_check or len(cached_slots_check) == 0:
                should_auto_scrape = True
                st.info("🔄 Cache is empty, auto-scraping availability...")
            else:
                # Check if cache is stale (older than 30 minutes)
                latest_scrape = cached_slots_check[0][6] if len(cached_slots_check[0]) > 6 else None
                if latest_scrape:
                    age = datetime.now() - latest_scrape
                    if age.total_seconds() > 1800:  # 30 minutes
                        should_auto_scrape = True
                        st.info("🔄 Cache is stale (>30 min), auto-refreshing...")
            
            # Auto-scrape if needed
            if should_auto_scrape:
                with st.spinner("Scraping Merky FC HQ for available times..."):
                    try:
                        results = scrape_now(db, ['half_pitch', 'full_pitch'])
                        if results:
                            success_count = sum(1 for r in results.values() if r.get('success'))
                            st.success(f"✅ Scraped {success_count}/2 pitch types successfully")
                    except Exception as e:
                        st.warning(f"Auto-scrape failed: {str(e)}. Use manual refresh below.")
            
            # Manual refresh controls
            col1, col2 = st.columns([3, 1])
            with col1:
                filter_pitch_type = st.selectbox("Filter by Pitch Type", ["All", "half_pitch", "full_pitch", "third_pitch"])
            with col2:
                if st.button("🔄 Manual Refresh"):
                    with st.spinner("Scraping availability..."):
                        try:
                            results = scrape_now(db, ['half_pitch', 'full_pitch'])
                            if results:
                                for pitch_type, result in results.items():
                                    if result['success']:
                                        st.success(f"{pitch_type}: {result['slot_count']} slots found")
                                    else:
                                        st.error(f"{pitch_type}: {result.get('error', 'Unknown error')}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Scrape failed: {str(e)}")
            
            # Display cached slots
            filter_type = None if filter_pitch_type == "All" else filter_pitch_type
            available_slots = db.get_available_slots(filter_type)
            
            if available_slots:
                slots_df = pd.DataFrame(
                    available_slots,
                    columns=["ID", "Date", "Time", "Pitch Type", "Price", "Available", "Scraped At"]
                )
                slots_df = slots_df[["Date", "Time", "Pitch Type", "Price", "Scraped At"]]
                st.dataframe(slots_df, use_container_width=True)
                st.caption(f"Total slots: {len(slots_df)}")
            else:
                st.info("No available slots in cache. Click 'Refresh Now' to scrape.")
        
        # TAB 4: Invoices
        with tab4:
            st.subheader("Monthly Invoices")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                invoice_month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1)
            with col2:
                invoice_year = st.selectbox("Year", range(2024, 2030), index=datetime.now().year - 2024)
            with col3:
                invoice_format = st.selectbox("Format", ["summary", "detailed"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Generate Invoice"):
                    invoice_generator.display_invoice_in_app(invoice_month, invoice_year)
            with col2:
                if st.button("📱 Send via WhatsApp"):
                    with st.spinner("Sending invoice..."):
                        success = invoice_generator.send_invoice_via_whatsapp(
                            invoice_month, invoice_year, invoice_format
                        )
                        if success:
                            st.success("Invoice sent!")
            
            # Export options
            st.markdown("### 📥 Export Options")
            if st.button("Download as CSV"):
                report = invoice_generator.generate_monthly_report(invoice_month, invoice_year)
                if report:
                    csv_data = invoice_generator.generate_csv_export(report)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"invoice_{invoice_year}_{invoice_month:02d}.csv",
                        mime="text/csv"
                    )
        
        # TAB 5: Settings
        with tab5:
            st.subheader("System Settings")
            
            st.markdown("### ⚙️ Booking Thresholds")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Half Pitch Threshold", booking_manager.thresholds['half_pitch'])
            with col2:
                st.metric("Full Pitch Threshold", booking_manager.thresholds['full_pitch'])
            
            st.info("Thresholds are configured in `.streamlit/secrets.toml`")
            
            st.markdown("### 📱 WhatsApp Integration")
            st.metric("Group ID", whatsapp_notifier.group_id)
            
            # Test WhatsApp
            if st.button("Send Test Message"):
                test_msg = f"🧪 Test message from Football App\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                if whatsapp_notifier.send_message(test_msg):
                    st.success("Test message sent!")
                else:
                    st.error("Failed to send test message")
            
            st.markdown("### 🤖 Auto-Booking")
            auto_enabled = "Enabled" if booking_manager.auto_book_enabled else "Disabled"
            st.metric("Status", auto_enabled)
            st.metric("Preferred Time", booking_manager.preferred_time)
            
            st.markdown("### 📊 Database Stats")
            all_players = db.get_all_players_in_db()
            st.metric("Total Players", len(all_players))
            
            all_bookings = db.fetch_bookings()
            st.metric("Total Bookings", len(all_bookings) if all_bookings else 0)
    
    elif admin_password:
        st.error("❌ Incorrect password")
