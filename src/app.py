from gc import disable

import streamlit as st
from datetime import datetime
import pandas as pd
from database import DatabaseHandler
from signups import add_player_signup,is_already_signed_up
from helper import validate_name_email,validate_email

# Initialize the database handler
#
environment = 'live'
db = DatabaseHandler(environment=environment)

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

db.create_tables('create_player_table.sql')
db.create_tables('create_signup_table.sql')
db.create_tables('create_booking_table.sql')


# --- Sidebar ---
# st.sidebar.header("Navigation")
# menu = st.sidebar.radio("Go to", ["Player Signup", "Admin Dashboard"])

current_date = datetime.now()

current_year = current_date.isocalendar()[0]
current_week = current_date.isocalendar()[1]

current_week = f"{current_year}-W{current_week:02d}"

participants = db.fetch_signups(current_week)
participants_df = pd.DataFrame(participants, columns=["name", "email_id"]).dropna()

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
    # Format as YYYY-WW

    all_player_signup = db.get_all_players_in_db()
    #
    # choice = st.selectbox("", ["Select", "New Player", "Existing Player"],
    #                       index=None)
    # Signup form
    # Markdown styling
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

    st.markdown("""
        <style>
            /* Center the form and its content */
            .stForm {
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            .stButton > button {
                font-size: 16px;
                padding: 10px 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            .stSelectbox {
                margin-top: -30px;
                margin-bottom: -10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Selectbox for player type
    choice = st.selectbox("", ["Select", "New Player", "Existing Player", "Guest"], index=0)

    name = 'Placeholder'
    email = 'Placeholder'
    # Handle form fields based on player type
    if choice == 'New Player':
        name = st.text_input("", placeholder="Enter your name")
        email = st.text_input("", placeholder="Enter your Email")
        name = validate_name_email(name, 'name')
        email = validate_name_email(email, 'email')
    elif choice == 'Existing Player':
        email = st.selectbox("", all_player_signup['email_id'], index=None)
        name = str(all_player_signup['name'][all_player_signup['email_id']==email])
    elif choice == 'Guest':
        name = st.text_input("", placeholder="Enter your name")
        st.markdown("<br>", unsafe_allow_html=True)
        email = st.selectbox("Host Email", all_player_signup['email_id'], index=None)
    # Now handle the form itself
    with st.form("signup_form"):
        # Submit button
        submitted = st.form_submit_button("Submit")
    if submitted:
        if name =='Placeholder' and email == 'Placeholder':
            st.error('Signup Type missing. Choose player type')
        elif not name or not email:
            st.error("Name and email are required!")
        elif validate_email(email):
            add_player_signup(db, choice, name, current_week, email)
            st.success(f"Thanks for signing up, {name}!")
        else:
            st.error("Invalid email. Please try again.")
    with st.form("removal form"):
        st.markdown("""
            <style>
                .subheader-red {
                    font-size: 1.5rem;
                    color: #B55A4A; /* Dull Red */
                    text-align: center;
                    font-weight: bold;
                }
                @media screen and (max-width: 768px) {
                    .subheader-red { font-size: 1.2rem; }
                }
                @media screen and (max-width: 480px) {
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
                db.delete_signups(player_email_to_delete,  current_week)
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
        st.write(pd.DataFrame(participants, columns=["Name", "Email"]))
    else:
        st.write("No one has signed up yet! Be the first!")

# --- Admin Dashboard Section ---
if menu == "Admin Dashboard":
    st.header("Admin Dashboard")

    # Admin password protection
    admin_password = st.text_input("Enter Admin Password", type="password")
    if admin_password == st.secrets['admin']['password']:
        st.success("Welcome, Admin!")

        # Weekly earnings chart
        st.subheader("Booking Overview")
        bookings = db.fetch_bookings()
        if bookings:
            booking_df = pd.DataFrame(bookings, columns=["Week", "Date", "Amount"])
            total_sum = booking_df['Amount'].sum()
            st.write(booking_df)
            st.metric("Total money spent",total_sum)
        else:
            st.write("No bookings recorded yet.")

        # Add booking form
        with st.form("booking_form"):
            booking_date = st.date_input("Booking Date")
            amount = st.number_input("Booking Amount", min_value=0.0, step=1.0)
            number_of_players = st.text_input("Number of Players", placeholder='How many players played in the session?')
            booking_submitted = st.form_submit_button("Add Booking")
            if booking_submitted:
                db.insert_bookings(current_week,amount,booking_date, number_of_players)
                st.success(f"Booking added for {booking_date} with amount £{amount}!")

