from psycopg2.errors import UniqueViolation


def clean_integrity_error(error):
    """Helper to convert an IntegrityError from psycopg2 to a field name string"""
    try:
        if not isinstance(error.__cause__, UniqueViolation):
            return None
        return error.__cause__.args[0].split(":")[1].split("(")[1].split(")")[0]
    except:
        return None
