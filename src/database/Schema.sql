-- ================================================
-- SOLIVITE DATABASE SCHEMA
-- ================================================

CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    email    TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS moments (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL,
    title    TEXT,
    target   TEXT,
    location TEXT,
    date     TEXT,
    time     TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS invitations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id         INTEGER NOT NULL,
    receiver_email    TEXT    NOT NULL,
    message           TEXT,
    schedule_date     TEXT,
    schedule_time     TEXT,
    relationship_type TEXT,
    status            TEXT    NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (sender_id) REFERENCES users(id)
);