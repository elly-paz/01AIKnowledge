import sqlite3


DB_NAME = "knowledge.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()



def add_note(title, content):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notes(title, content)
        VALUES (?,?)
        """,
        (title, content)
    )

    conn.commit()
    conn.close()



def get_notes():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, content 
        FROM notes
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


def search_notes(keyword):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, content
        FROM notes
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY id DESC
        """,
        (f"%{keyword}%", f"%{keyword}%")
    )

    data = cursor.fetchall()

    conn.close()

    return data