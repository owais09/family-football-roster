import streamlit as st


def add_player_signup(db, choice, name, week, email, host_player_id=None):
    """
    Main function to handle player signup. Coordinates sub-tasks for adding or verifying a player.

    Args:
        db: DatabaseHandler instance
        choice (str): Player type ("New Player", "Existing Player", "Guest")
        name (str): Player's name.
        week (str): Week of the signup (e.g., "2025-W03").
        email (str): Player's email.
        host_player_id (int, optional): ID of player bringing the guest (for guests only)

    Returns:
        str: Success or error message.
    """
    try:
        # Step 1: Check if the player exists
        player_id = db.get_player_id(email)
        # Step 2: Prompt the user for player type
        player_id = handle_new_player_signup(db, choice, name, email, player_id, host_player_id)
        # Step 3: Check if the player is already signed up
        if is_already_signed_up(db, player_id, week):
            st.error( "You have already signed up for this week!")
        else:
            add_signup(db,name,week, player_id)
            st.success(f"Thanks for signing up, {name}!")

    except Exception as e:
        print(f"An error occurred: str({e}")
        return f"An error occurred: {str(e)}"


# ------------------------
# Helper Functions
# ------------------------

def get_player_id(db, email):
    """
    Fetch the player ID based on the provided email.

    Args:
        cursor: Database cursor.
        email (str): Email of the player.

    Returns:
        int or None: Player ID if found, None otherwise.
    """
    result = db.get_player_id(email)
    return result[0] if result else None


def handle_new_player_signup(db, choice, name, email, player_id, host_player_id=None):
    """
    Handle the creation of a new player if not found in the database.

    Args:
        db: DatabaseHandler instance
        choice (str): Player type
        name (str): Name of the player.
        email (str): Email of the player.
        player_id (int): Existing player ID if found
        host_player_id (int, optional): ID of player bringing the guest

    Returns:
        int or None: New player ID if created successfully, None otherwise.
    """
    if choice == "New Player":
        if player_id:
            st.error('Player already in database')
        else:
            player_id = db.add_player_signup(name, email, brought_by_player_id=None)
    elif choice == "Existing Player":
        if player_id:
            pass
        else:
            st.error("Player not found in the database. Please correct the name and try again.")
    elif choice =='Guest':
        if not host_player_id:
            st.error("⚠️ Please select who is bringing this guest!")
            return None
        # Guest email format: Guest-<host_email>-<guest_name>
        if email:
            email = f'Guest-{email}-{name}'
        # Create guest linked to host player
        player_id = db.add_player_signup(name, email, brought_by_player_id=host_player_id)
    return player_id

def is_already_signed_up(db, player_id, week):
    """
    Check if the player is already signed up for the specified week.

    Args:
        cursor: Database cursor.
        player_id (int): Player ID.
        week (str): Week of the signup.

    Returns:
        bool: True if the player is already signed up, False otherwise.
    """
    rows = db.get_signup_by_player_id(week, player_id)
    if rows:
        return True
    else:
        return False


def add_signup(db, name, week, player_id):
    """
    Add a player signup to the database.

    Args:
        cursor: Database cursor.
        player_id (int): Player ID.
        week (str): Week of the signup.

    Returns:
        None
    """
    return db.add_weekly_signups(name,week, player_id)
