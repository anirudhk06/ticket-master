import uuid


def valid_uuid(uuid_str):
    """Validate UUID string."""
    try:
        uuid.UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False