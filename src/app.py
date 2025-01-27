import streamlit as st
from datetime import datetime
import pandas as pd
from database import DatabaseHandler
from signups import add_player_signup,is_already_signed_up
from helper import validate_name_email

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
st.title("⚽ Family Football App")
st.markdown("Welcome to the Family Football Management App! 🎉")

db.create_tables('create_player_table.sql')
db.create_tables('create_signup_table.sql')
db.create_tables('create_booking_table.sql')


# --- Sidebar ---
st.sidebar.header("Navigation")
menu = st.sidebar.radio("Go to", ["Player Signup", "Admin Dashboard"])

current_date = datetime.now()

current_year = current_date.isocalendar()[0]
current_week = current_date.isocalendar()[1]

# --- Player Signup Section ---
if menu == "Player Signup":
    # Format as YYYY-WWW
    current_week = f"{current_year}-W{current_week:02d}"

    participants = db.fetch_signups(current_week)
    participants_df = pd.DataFrame(participants, columns=["name", "email_id"])

    all_player_signup = db.get_all_players_in_db()
    st.metric(f"Participants signed up for week: {current_week}", len(participants))

    choice = st.selectbox("Player Type", ["Select", "New Player", "Existing Player"],
                          index=None)

    # Signup form
    with st.form("signup_form"):
        st.subheader("Signup to Weekly Football")

        if choice =='New Player':
            name = st.text_input("Your Name", placeholder="Enter your name")
            email = st.text_input("Your Email", placeholder="Enter your Email")
            name = validate_name_email(name, 'name')
            email = validate_name_email(email, 'email')
        elif choice == 'Existing Player':
            email = st.selectbox("Choose name", all_player_signup['email_id'].to_list(),index=None)
            name = all_player_signup[all_player_signup['email_id']==email]['name']

        submitted = st.form_submit_button("Sign Up")
        if submitted:
            add_player_signup(db, choice, name, current_week, email)
            st.success(f"Thanks for signing up, {name}!")

    with st.form("removal form"):
        st.subheader("Remove name from weekly list")
        player_email_to_delete = st.text_input("Enter Player Email to Remove:")
        player_email_to_delete = validate_name_email(player_email_to_delete, 'email')
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
    st.subheader("Participants")
    if participants:
        st.write(pd.DataFrame(participants, columns=["Name","Email"]))
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
    else:
        st.error("Invalid password.")

