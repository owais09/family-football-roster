import psycopg2
import streamlit as st
import os
import pandas as pd
from config import get_database_config


class DatabaseHandler:
    def __init__(self, environment):
        self.environment = environment
        self.conn = self.init_connection()

    def init_connection(self):
        # Get database config from secrets.toml or environment variables
        db_config = get_database_config()
        
        try:
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password'],
                connect_timeout=10)  # 10 second timeout
            
            # Set autocommit for DDL operations to avoid transaction issues
            conn.set_session(autocommit=False)
            return conn
        except psycopg2.OperationalError as e:
            raise Exception(f"Database connection failed: {str(e)}. Please check your DATABASE_URL environment variable.")
        except Exception as e:
            raise Exception(f"Unexpected database error: {str(e)}")
    
    def ensure_connection(self):
        """Ensure connection is in a good state, rollback if needed"""
        try:
            if self.conn.closed:
                self.conn = self.init_connection()
            # Check if we're in a failed transaction
            if self.conn.status != psycopg2.extensions.STATUS_READY:
                self.conn.rollback()
        except Exception:
            # Reconnect if there's any issue
            self.conn = self.init_connection()

    def load_sql(self, file_name):
        sql_path = os.path.join("src", "sql", file_name)
        with open(sql_path, 'r') as file:
            return file.read()

    def create_tables(self, table_query_name):
        create_tables_query = self.load_sql(table_query_name)
        with self.conn.cursor() as cur:
            try:
                cur.execute(create_tables_query)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                # Silently ignore if table already exists
                if "already exists" not in str(e).lower():
                    raise

    def get_player_id(self,email):
        player_id_query = self.load_sql("get_player_id_from_player_dimensions.sql")
        with self.conn.cursor() as cur:
            try:
                cur.execute(player_id_query, (email,))
                player_id = cur.fetchall()
                if player_id:
                    player_id = player_id[0]
                return player_id

            except Exception as e:
                self.conn.rollback()
                st.error(f"An error occurred: {str(e)}")

    def add_player_signup(self, name, email, brought_by_player_id=None):
        """
        Add a new player to the database
        
        Args:
            name (str): Player name
            email (str): Player email
            brought_by_player_id (int, optional): ID of player who brought this guest
                                                  None for regular players
        
        Returns:
            int: player_id of newly created player
        """
        add_player_query = self.load_sql("insert_new_player_entry.sql")
        with self.conn.cursor() as cur:
            try:
                cur.execute(add_player_query, (name, email, brought_by_player_id))
                player_id = cur.fetchone()[0]
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                st.error(f"An error occurred: {str(e)}")
        return player_id

    def add_weekly_signups(self, name, week, player_id):
        with self.conn.cursor() as cur:
            try:
                signup_query = self.load_sql("add_weekly_signup_entry.sql")
                cur.execute(signup_query, (week, player_id,))
                self.conn.commit()
                st.success(f"Player {name} signed up for week {week}!")
            except Exception as e:
                self.conn.rollback()
                st.error(f"An error occurred: {str(e)}")

    def get_all_players_in_db(self):
        player_id_query = self.load_sql("get_all_player_in_database.sql")
        all_players_in_db = pd.read_sql(player_id_query,con= self.conn)
        return all_players_in_db

    def fetch_signups(self, week):
        self.ensure_connection()  # Ensure connection is good
        fetch_signups_query = self.load_sql("get_weekly_signups.sql")
        with self.conn.cursor() as cur:
            cur.execute(fetch_signups_query, (week,))
            rows = cur.fetchall()
        return rows

    def get_signup_by_player_id(self, week, player_id):
        fetch_signups_query = self.load_sql("check_weekly_signups.sql")
        with self.conn.cursor() as cur:
            try:
                cur.execute(fetch_signups_query, (week, player_id))
                rows = cur.fetchall()
                return rows
            except Exception as e:
                self.conn.rollback()
                st.error(f"An error occurred: {str(e)}")

    def delete_signups(self, email, week):
        player_id_list = self.get_player_id(email)
        player_id = player_id_list[0]
        if player_id:
            delete_signups_query = self.load_sql("delete_weekly_signup.sql")
            with self.conn.cursor() as cur:
                try:
                    cur.execute(delete_signups_query, (player_id, week))
                    self.conn.commit()
                    st.success("Signup deleted successfully!")
                except Exception as e:
                    self.conn.rollback()
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.error('No record found')

    def insert_bookings(self, week, session_date, amount, number_of_players):
        fetch_bookings_query = self.load_sql("insert_session_details.sql")
        with self.conn.cursor() as cur:
            cur.execute(fetch_bookings_query, (week, session_date,amount, number_of_players))
            self.conn.commit()

    def fetch_bookings(self):
        fetch_bookings_query = self.load_sql("fetch_booking.sql")
        with self.conn.cursor() as cur:
            cur.execute(fetch_bookings_query)
            rows = cur.fetchall()
        return rows

    def check_booking_exists(self, week):
        """Check if a booking already exists for the given week"""
        query = self.load_sql("check_booking_exists.sql")
        with self.conn.cursor() as cur:
            cur.execute(query, (week,))
            result = cur.fetchone()
        return result is not None

    def insert_booking_with_details(self, week, session_date, booking_time, pitch_type, 
                                    booking_amount, cost_per_player, number_of_players, 
                                    auto_booked, booking_confirmation, merky_booking_id):
        """Insert a new booking with full details"""
        query = self.load_sql("insert_booking_with_details.sql")
        with self.conn.cursor() as cur:
            try:
                cur.execute(query, (week, session_date, booking_time, pitch_type, 
                                   booking_amount, cost_per_player, number_of_players,
                                   auto_booked, booking_confirmation, merky_booking_id, 'confirmed'))
                booking_id = cur.fetchone()[0]
                self.conn.commit()
                return booking_id
            except Exception as e:
                self.conn.rollback()
                st.error(f"An error occurred while inserting booking: {str(e)}")
                return None

    def cache_available_slots(self, slots_data):
        """Cache available slots from scraper"""
        query = self.load_sql("cache_available_slots.sql")
        with self.conn.cursor() as cur:
            try:
                for slot in slots_data:
                    cur.execute(query, (slot['date'], slot['time'], slot['pitch_type'], 
                                       slot['price'], slot['available']))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                st.error(f"An error occurred while caching slots: {str(e)}")

    def get_available_slots(self, pitch_type=None):
        """Get available slots from cache"""
        query = self.load_sql("get_available_slots.sql")
        with self.conn.cursor() as cur:
            cur.execute(query, (pitch_type, pitch_type))
            rows = cur.fetchall()
        return rows

    def get_bookings_for_month(self, month, year):
        """Get all bookings for a specific month"""
        query = self.load_sql("get_bookings_for_month.sql")
        with self.conn.cursor() as cur:
            cur.execute(query, (month, year))
            rows = cur.fetchall()
        return rows

    def get_monthly_player_costs(self, month, year):
        """
        Calculate player costs for monthly invoicing
        Includes guests - guests are expensed to their host player
        
        Returns:
            list of tuples: (name, email, sessions_attended, total_cost, weeks_attended, guest_names[])
        """
        # Try new query with guest support first
        try:
            query = self.load_sql("get_monthly_player_costs_with_guests.sql")
            with self.conn.cursor() as cur:
                cur.execute(query, (month, year))
                rows = cur.fetchall()
            return rows
        except Exception as e:
            # Fallback to old query if column doesn't exist yet
            if "brought_by_player_id" in str(e) or "column" in str(e).lower():
                query = self.load_sql("get_monthly_player_costs.sql")
                with self.conn.cursor() as cur:
                    cur.execute(query, (month, year))
                    rows = cur.fetchall()
                # Add empty guest list for backward compatibility
                return [(row[0], row[1], row[2], row[3], row[4], []) for row in rows]
            else:
                raise

    def close_connection(self):
        if self.conn:
            self.conn.close()
