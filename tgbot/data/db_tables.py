reg_date_index = "reg_date"

users = f"""
    CREATE TABLE IF NOT EXISTS users (
        user_id         TEXT,
        mention         TEXT,
        {reg_date_index} TIMESTAMPTZ(0),
        rating          NUMERIC(18, 2) DEFAULT 0,
        referal_id      TEXT,
        ban_date        TIMESTAMPTZ(0),
        unbanned_date   TIMESTAMPTZ(0),
        user_history    JSON,
        message_history JSON,
        role            TEXT
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


moderating_history = """
    CREATE TABLE IF NOT EXISTS moderating_history (
        user_id         TEXT, 
        role            TEXT, 
        action          TEXT,
        date            TEXT
);
"""

advertising = """
    CREATE TABLE IF NOT EXISTS advertising (
        advert_id       TEXT,
        advert_header   TEXT,
        text            TEXT,
        media           JSON,
        media_type      TEXT,
        inline_buts     JSON,
        sending_date    TIMESTAMPTZ(0),
        sending_status  BOOLEAN DEFAULT False
);
"""

advertising_handlers = """
    CREATE TABLE IF NOT EXISTS advertising_handlers (
        handler_id      TEXT,
        advert_id       TEXT,
        message         TEXT
);
"""

db_tables = [users, content, moderating_history, advertising, advertising_handlers]
