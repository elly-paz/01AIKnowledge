import sqlite3


DB_NAME = "knowledge.db"


def _get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_has_column(table, column):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return column in columns


def init_db():
    conn = _get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS note_tags(
        note_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY(note_id, tag_id),
        FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
        FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    """)

    if not _table_has_column("notes", "created_time"):
        cursor.execute(
            "ALTER TABLE notes ADD COLUMN created_time DATETIME"
        )
        cursor.execute(
            "UPDATE notes SET created_time = CURRENT_TIMESTAMP WHERE created_time IS NULL"
        )

    conn.commit()
    conn.close()


def add_note(title, content):

    conn = _get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notes(title, content)
        VALUES (?,?)
        """,
        (title, content)
    )

    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id


def add_note_with_tags(title, content, tags):
    note_id = add_note(title, content)
    add_note_tags(note_id, tags)
    return note_id


def get_notes():

    conn = _get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT title, content, created_time
        FROM notes
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


def update_note(note_id, title, content):
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE notes
        SET title = ?, content = ?
        WHERE id = ?
        """,
        (title, content, note_id)
    )

    conn.commit()
    conn.close()


def delete_note(note_id):
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()


def get_notes_by_tag(tag):
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT n.title, n.content, n.created_time
        FROM notes n
        JOIN note_tags nt ON nt.note_id = n.id
        JOIN tags t ON t.id = nt.tag_id
        WHERE t.name = ?
        ORDER BY n.id DESC
        """,
        (tag.strip(),)
    )

    data = cursor.fetchall()

    conn.close()

    return data


def search_notes(keyword):

    conn = _get_connection()

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


def add_tag(name):
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO tags(name) VALUES (?)",
        (name.strip(),)
    )

    conn.commit()
    cursor.execute("SELECT id FROM tags WHERE name = ?", (name.strip(),))
    tag_id = cursor.fetchone()[0]
    conn.close()
    return tag_id


def add_note_tags(note_id, tags):
    if not tags:
        return

    conn = _get_connection()
    cursor = conn.cursor()

    for tag in tags:
        normalized_tag = tag.strip()
        if not normalized_tag:
            continue

        cursor.execute(
            "INSERT OR IGNORE INTO tags(name) VALUES (?)",
            (normalized_tag,)
        )
        cursor.execute(
            "SELECT id FROM tags WHERE name = ?",
            (normalized_tag,)
        )
        tag_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT OR IGNORE INTO note_tags(note_id, tag_id) VALUES (?, ?)",
            (note_id, tag_id)
        )

    conn.commit()
    conn.close()


def get_note_tags(note_id):
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT t.name
        FROM tags t
        JOIN note_tags nt ON nt.tag_id = t.id
        WHERE nt.note_id = ?
        ORDER BY t.name
        """,
        (note_id,)
    )

    tags = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tags


def get_all_tags():
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM tags ORDER BY name"
    )

    tags = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tags


def get_notes_with_tags():
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT n.id, n.title, n.content, GROUP_CONCAT(t.name)
        FROM notes n
        LEFT JOIN note_tags nt ON nt.note_id = n.id
        LEFT JOIN tags t ON t.id = nt.tag_id
        GROUP BY n.id
        ORDER BY n.id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    notes = []
    for row in rows:
        note_id, title, content, tag_string = row
        tags = tag_string.split(",") if tag_string else []
        notes.append((note_id, title, content, tags))

    return notes


def filter_notes_by_tag(tag):
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT n.title, n.content
        FROM notes n
        JOIN note_tags nt ON nt.note_id = n.id
        JOIN tags t ON t.id = nt.tag_id
        WHERE t.name = ?
        ORDER BY n.id DESC
        """,
        (tag.strip(),)
    )

    data = cursor.fetchall()
    conn.close()
    return data