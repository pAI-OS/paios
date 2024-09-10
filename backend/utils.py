from datetime import datetime, timezone

# Returns dict with null fields removed (e.g., for OpenAPI spec compliant
# responses without having to set nullable: true)
def remove_null_fields(data):
    if isinstance(data, dict):
        return {k: remove_null_fields(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_null_fields(item) for item in data if item is not None]
    else:
        return data

# Returns dict with only keys_to_include (e.g., for OpenAPI spec compliant
# responses without unexpected fields present)
def filter_dict(data, keys_to_include):
    return {k: data[k] for k in keys_to_include if k in data}

# Converts a db result into a dict with named fields (e.g.,
# ["x", "y"], [1, 2] -> { "x": 1, "y": 2})
def zip_fields(fields, result):
    return {field: result[i] for i, field in enumerate(fields)}

# Returns current timestamp in UTC in ISO 8601 format
def get_current_timestamp():
    current_time = datetime.now(timezone.utc)
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    return formatted_time