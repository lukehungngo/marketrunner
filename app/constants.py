from datetime import datetime

DEFAULT_BTC_FROM_DATE = "2014-10-01 00:00:00"


def datetime_to_string(now=None):
    if now is None:
        now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def check_and_convert_date_format(date_string):
    try:
        # Check if the input is in the format YYYY-MM-DD HH:MM:SS
        datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return date_string  # If it matches, return the original string
    except ValueError:
        try:
            # Check if the input is in the format YYYY-MM-DD
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")

            # Convert it to the format YYYY-MM-DD 00:00:00
            new_date_string = date_obj.strftime("%Y-%m-%d 00:00:00")
            return new_date_string
        except ValueError:
            # If the format is incorrect, return None or raise an error
            raise ValueError(
                "Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format."
            )
