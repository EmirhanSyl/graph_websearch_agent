from datetime import datetime, timezone


# for getting the current date and time in UTC
def get_current_utc_datetime():
    now_utc = datetime.now(timezone.utc)
    current_time_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
    return current_time_utc

# for checking if an attribute of the state dict has content.
def check_for_content(var):
    """Return the underlying content if ``var`` is a message-like object."""
    if var is None:
        return var
    try:
        return var.content
    except AttributeError:
        return var