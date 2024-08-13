from sqlite3 import IntegrityError

from psycopg2.errors import UniqueViolation


def clean_integrity_error(error):
    """Helper to convert an IntegrityError from psycopg2/sqlite3 to a field name string"""
    try:
        if isinstance(error.__cause__, UniqueViolation):
            return error.__cause__.args[0].split(":")[1].split("(")[1].split(")")[0]
        if isinstance(error.__cause__, IntegrityError):
            return error.__cause__.args[0].split(": ")[1].split(".")[1]
        return None
    except Exception:
        return None
