def validate_name_email(string, type):
    """

    Args:
        string:
        type:

    Returns:

    """
    lower_case_name = string.lower()
    if type == "name":
        return lower_case_name.title()
    else:
        return lower_case_name