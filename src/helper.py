import streamlit as st
import re

def validate_name_email(string, type):
    """

    Args:
        string:
        type:

    Returns:

    """
    string = remove_whitepaces(string)
    lower_case_name = string.lower()
    if type == "name":
        return lower_case_name.title()
    else:
        return lower_case_name


def validate_name(name: str):
    if name:
        if re.match(r'^[A-Za-z ]*$', name):
            return True
        else:
            st.error("Invalid input: Only letters and spaces are allowed.")
            return False


def validate_email(email:str):
    acceptable_email_id = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']

    if "@" not in email:
        return False
    else:
        email_suffix = email.split('@')[1]
        if email_suffix in acceptable_email_id:
            return True
        else:
            return False

def remove_whitepaces(string):
    return string.replace(" ","")

def check_if_empty(string):
    if string == '':
        return True
    else:
        return False







