
users = """
    CREATE TABLE IF NOT EXISTS users (
        user_id         TEXT,
        mention         TEXT,
        reg_date        DATE,
        rating          NUMERIC(18, 2) DEFAULT 0,
        referal_id      TEXT
    );
"""

content = """
    CREATE TABLE IF NOT EXISTS content (
        key             TEXT,
        text            TEXT,
        media_type      TEXT,
        media           TEXT
    );
"""

db_tables = [users, content]
