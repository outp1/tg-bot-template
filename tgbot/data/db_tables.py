
users = """
    CREATE TABLE IF NOT EXISTS users (
        user_id         TEXT,
        mention         TEXT,
        reg_date        TIMESTAMPTZ(0),
        rating          NUMERIC(18, 2) DEFAULT 0,
        referal_id      TEXT,
        ban_date        TIMESTAMPTZ(0),
        unbanned_date   TIMESTAMPTZ(0),
        user_history    TEXT,
        message_history TEXT
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
