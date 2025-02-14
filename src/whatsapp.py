import pandas as pd
import pywhatkit as pwk
from database import DatabaseHandler
from datetime import datetime

# Example DataFrame with signup details
environment = 'live'
db = DatabaseHandler(environment=environment)

current_date = datetime.now()

current_year = current_date.isocalendar()[0]
current_week = current_date.isocalendar()[1]

current_week = f"{current_year}-W{current_week:02d}"

signups_df = db.fetch_signups(current_week)
signups_df = pd.DataFrame(signups_df, columns=["name", "email"]).dropna()

# Step 1: Format the message
def format_signup_message(signups_df):
    if signups_df.empty:
        return "No signups yet."

    message = "🎉 Weekly Football Signup List 🎉\n\n"
    for idx, row in signups_df.iterrows():
        if idx == 1:
            message += f"{idx + 1}. {row['name']}\n"
        else:
            message += f"{row['name']}\n"
    return message


# Step 2: Get the formatted message
formatted_message = format_signup_message(signups_df)

group_id = 'CHAjDSd8Tm14QZ4rGrqQxc'


# Step 3: Send the message using pywhatkit
def send_whatsapp_message(message):
    try:
        pwk.sendwhatmsg_to_group_instantly(group_id, message)
        print("Message scheduled successfully!")
    except Exception as e:
        print(f"Failed to send message: {e}")



send_whatsapp_message(formatted_message)
