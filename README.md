
# Family Football App

The **Family Football App** is a Streamlit-based application designed to help manage weekly football games. It includes features for player signups, booking management, and an admin dashboard for tracking earnings and participant data.

## Features

### Player Signup
- Players can sign up for the weekly football game.
- Participants are tracked by week (using the ISO week format).
- New and existing players are supported.
- Players can remove their names from the weekly list.

### Admin Dashboard
- Password-protected admin access.
- View a summary of weekly earnings and participants.
- Add new bookings, including details like the date, amount, and number of players.

### Database Operations
The app connects to a database through a `DatabaseHandler` class to:
- Create necessary tables for players, signups, and bookings.
- Fetch and display participant and booking data.
- Add or remove player signups and bookings.

## Prerequisites

Before running the application, ensure the following are installed and set up:

- **Python 3.9+**
- **Streamlit**
- **pandas**
- A database configured for the `DatabaseHandler` (e.g., PostgreSQL or SQLite).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/family-football-app.git
   cd family-football-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Configure your database environment (e.g., staging, production) in the `DatabaseHandler` class.
   - Make sure the required SQL scripts for creating tables are present (e.g., `create_player_table.sql`, `create_signup_table.sql`, `create_booking_table.sql`).

## Running the App

Run the Streamlit app:
```bash
streamlit run app.py
```

## File Structure

```plaintext
.
|-- app.py                # Main application file
|-- database.py           # Database handler for CRUD operations
|-- helper.py             # Helper functions (e.g., data validation)
|-- signups.py            # Signup-related operations
|-- requirements.txt      # Dependencies
|-- create_player_table.sql
|-- create_signup_table.sql
|-- create_booking_table.sql
```

## Code Breakdown

### app.py

#### **Initialization**
- Initializes the `DatabaseHandler` with the environment (`staging`).
- Configures Streamlit page layout and title.
- Creates required database tables for players, signups, and bookings.

#### **Player Signup Section**
- Displays the number of participants signed up for the current week.
- Signup form for players to:
  - Enter name and email (validated using `validate_name_email` from `helper.py`).
  - Choose whether they are a new or existing player.
- Allows players to remove themselves from the signup list.
- Displays the list of participants for the current week.

#### **Admin Dashboard**
- Password-protected access (`Oma1123581321-`).
- Displays a summary of weekly bookings and total earnings.
- Allows admins to add new bookings, specifying:
  - Booking date
  - Booking amount
  - Number of players

### database.py
- Contains the `DatabaseHandler` class, which abstracts database operations.
- Methods for creating tables, inserting data, fetching data, and deleting records.

### signups.py
- Contains functions for handling player signup logic:
  - `add_player_signup`: Adds a player to the signup list.
  - `is_already_signed_up`: Checks if a player is already signed up.

### helper.py
- Utility functions for data validation:
  - `validate_name_email`: Validates names and email addresses.

## How to Use the App

### Player Signup
1. Open the app and select "Player Signup" from the sidebar.
2. Enter your name, email, and select your player type (new or existing).
3. Click "Sign Up" to register for the weekly game.
4. To remove your name from the list, enter your email in the removal form and click "Remove Player."

### Admin Dashboard
1. Select "Admin Dashboard" from the sidebar.
2. Enter the admin password (`Oma1123581321-`).
3. View the list of bookings and total earnings.
4. Add new bookings using the provided form.

## Future Enhancements
- Integrate WhatsApp notifications for weekly updates.
- Add player profiles with history of participation.
- Enable dynamic password management for the admin dashboard.
- Expand the database to track game performance metrics.

## Contributing
If you want to contribute to this project, feel free to fork the repository and submit a pull request. Make sure to add tests and documentation for new features.

## License
This project is licensed under the MIT License.
