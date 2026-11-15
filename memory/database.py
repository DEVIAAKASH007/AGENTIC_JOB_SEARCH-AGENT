import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver


DB_PATH = "career_agent.db"


def get_sqlite_connection():
    """
    Create a SQLite connection for persistent storage.
    """
    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )


def get_checkpointer():
    """
    Return a persistent LangGraph SQLite checkpointer.
    """
    connection = get_sqlite_connection()

    checkpointer = SqliteSaver(connection)

    # Create required SQLite tables
    checkpointer.setup()

    return checkpointer