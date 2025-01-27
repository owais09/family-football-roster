import psycopg2
import streamlit as st
import os
import pandas as pd


class DatabaseHandler:
    def __init__(self, environment):
        self.environment = environment
        self.conn = self.init_connection()

    def init_connection(self):
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"])

    def load_sql(self, file_name):
        sql_path = os.path.join("src", "sql", file_name)
        with open(sql_path, 'r') as file:
            return file.read()

    def create_tables(self, table_query_name):
        create_tables_query = self.load_sql(table_query_name)
        with self.conn.cursor() as cur:
            cur.execute(create_tables_query)
            self.conn.commit()

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

    def add_player_signup(self, name, email):
        add_player_query = self.load_sql("insert_new_player_entry.sql")
        with self.conn.cursor() as cur:
            try:
                cur.execute(add_player_query, (name, email))
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

    def close_connection(self):
        if self.conn:
            self.conn.close()
