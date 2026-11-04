# Intentional security test: SQL injection vulnerability.
import sqlite3


def get_user(username):
    connection = sqlite3.connect("users.db")

    query = (
        "SELECT * FROM users WHERE username = '"
        + username
        + "'"
    )

    return connection.execute(query).fetchall()