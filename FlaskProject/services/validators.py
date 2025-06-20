
def validate_non_empty_string(field_value, field_name="Field"):
    if field_value is None or str(field_value).strip() == '':
        raise ValueError(f"{field_name} cannot be empty.")
    return field_value.strip()
