
def validate_non_empty_string(field_value, field_name="Field"):
    if field_value is None or str(field_value).strip() == '':
        raise ValueError(f"{field_name} cannot be empty.")
    return field_value.strip()

def validate_length(value: str, field_name: str, max_length: int) -> str | None:
    """Validate the length of a string. Return error message if invalid, else None."""
    if not value:
        return f"{field_name} is required."
    if len(value) > max_length:
        return f"{field_name} must be at most {max_length} characters."
    return None

def to_bool(value):
    return str(value).lower() in ['true', 'on', '1', 'yes']
