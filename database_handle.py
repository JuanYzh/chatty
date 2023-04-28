# -*- coding: utf-8 -*-
# Copyright (c) 2023 by WenHuan Yang-Zhang.
# Date: 2023-03.01
# Ich und google :)
from cryptography.fernet import Fernet
import datetime
import sqlite3
import os

# Please generate a key and paste here # key = Fernet.generate_key()
key = ""


# encrypted
def encrypted_key(text):
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(text.encode('utf-8'))
    return encrypted_text.decode('utf-8')

# decrypt
def decrypt_key(text_encrypted):
    if text_encrypted is str and text_encrypted.startswith("sk-"):
        return text_encrypted
    elif text_encrypted is str:
        text_encrypted = bytes(text_encrypted, "utf-8")
    cipher_suite = Fernet(key)
    try:
        decrypted_text = cipher_suite.decrypt(text_encrypted).decode('utf-8')
    except Exception as err:
        return ""
    return decrypted_text


def time_now():
    return datetime.datetime.now().timestamp()


def create_database_and_tables():
    database_path = "./data"
    if not os.path.exists(database_path):
        os.makedirs(database_path)
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect("./data/chatty.db")
    cursor = conn.cursor()

    # Create the 'setting' table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS setting (
        ID INTEGER PRIMARY KEY,
        key TEXT,
        theme TEXT DEFAULT ''
    )
    """)

    # Create the 'chat_title' table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_title (
        ID INTEGER PRIMARY KEY,
        title_name TEXT UNIQUE,
        create_time REAL
    )
    """)

    # Create the 'chat_config' table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_config (
        ID INTEGER PRIMARY KEY,
        title_id INTEGER UNIQUE,
        role TEXT,
        content TEXT DEFAULT '',
        token INTEGER DEFAULT NULL,
        max_memory INTEGER DEFAULT NULL,
        temperature INTEGER,
        model TEXT,
        FOREIGN KEY (title_id) REFERENCES chat_title (ID) ON DELETE CASCADE
    )
    """)

    # Create the 'chat_history' table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        ID INTEGER PRIMARY KEY,
        title_id INTEGER,
        role TEXT,
        content TEXT,
        time REAL,
        token INTEGER DEFAULT NULL,
        page INTEGER DEFAULT NULL,
        FOREIGN KEY (title_id) REFERENCES chat_title (ID) ON DELETE CASCADE
    )
    """)

    # Commit the changes and close the connection
    conn.commit()
    return conn


def insert_setting(conn, api_key):
    # Connect to the database
    cursor = conn.cursor()
    # delete setting table
    cursor.execute(f"DELETE FROM setting")
    conn.commit()
    # Insert the api key
    keys = [(key, None) for key in api_key]
    cursor.executemany("""
    INSERT OR IGNORE INTO setting  (key , theme )
    VALUES (?, ?)
    """, keys)
    # Commit the changes and close the connection
    conn.commit()


def insert_chat_title(conn, chat_title):
    # Connect to the database
    cursor = conn.cursor()

    # Insert the chat_title into the table, ignoring if title_name already exists
    cursor.executemany("""
    INSERT OR IGNORE INTO chat_title (title_name, create_time)
    VALUES (?, ?)
    """, chat_title)

    # Commit the changes and close the connection
    conn.commit()


def insert_chat_title(conn, chat_config):
    # Connect to the database
    cursor = conn.cursor()

    # Insert the chat_title into the table, ignoring if title_name already exists
    cursor.executemany("""
    INSERT OR IGNORE INTO chat_title (title_name, create_time)
    VALUES (?, ?)
    """, chat_config)

    # Commit the changes and close the connection
    conn.commit()


def insert_or_update_chat_config(conn, chat_config_data):
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO chat_config (title_id, role, content, token, max_memory, temperature, model)
        VALUES (:title_id, :role, :content, :token, :max_memory, :temperature, :model)
    """, chat_config_data)
    conn.commit()


def title_id_get(conn, chat_titles):
    cursor = conn.cursor()
    title_id_dict = {}
    for title in chat_titles:
        cursor.execute("SELECT ID FROM chat_title WHERE title_name=?", (title,))
        result = cursor.fetchone()
        if result:
            title_id = result[0]
            title_id_dict.update({title:title_id})
    return title_id_dict


def insert_chat_history_bulk(conn, chat_history_list):
    # Fetch all title_id and time pairs from the database
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title_id, time FROM chat_history
    """)

    existing_title_time_pairs = set(cursor.fetchall())

    # Filter out chat_history_list entries that already exist in the database
    filtered_chat_history_list = [
        chat_history for chat_history in chat_history_list
        if (chat_history["title_id"], chat_history["time"]) not in existing_title_time_pairs
           and (chat_history["title_id"] and chat_history["time"])
    ]
    # Bulk insert filtered data
    cursor.executemany("""
        INSERT INTO chat_history (title_id, role, content, time, token, page)
        VALUES (:title_id, :role, :content, :time, :token, :page)
    """, filtered_chat_history_list)

    # Commit the transaction
    conn.commit()


def api_key_get(conn):
    cursor = conn.cursor()
    cursor.execute("""
            SELECT key FROM setting
        """)
    keys = cursor.fetchall()
    key_list = []
    if not keys:
        return key_list
    for key in keys:
        key_list.append(key[0])
    return key_list


def load_chat_map(conn):
    cursor = conn.cursor()
    # Get data from chat_title, chat_config, and chat_history tables
    cursor.execute("SELECT * FROM chat_title")
    chat_titles = cursor.fetchall()
    cursor.execute("SELECT * FROM chat_config")
    chat_configs = cursor.fetchall()
    cursor.execute("SELECT * FROM chat_history")
    chat_histories = cursor.fetchall()
    chat_map = {}
    # Combine data into the chat_map dictionary
    #chat_histories = sorted(chat_histories, key=lambda x: x[4], reverse=False)
    for title in chat_titles:
        title_id, title_name, create_time = title
        chat_map[title_name] = {
            "model": None,
            "creative": None,
            "scenario": None,
            "create_time": create_time,
            "message": []
        }

        for config in chat_configs:
            if config[1] == title_id:
                chat_map[title_name]["model"] = config[-1]
                chat_map[title_name]["creative"] = config[-2]
                chat_map[title_name]["scenario"] = config[3]

        for history in chat_histories:
            if history[1] == title_id:
                chat_map[title_name]["message"].append({
                    "role": history[2],
                    "content": history[3]
                })
    return chat_map


def delete_chat_history_by_title_id(conn, title):
    cursor = conn.cursor()
    cursor.execute("select id FROM chat_title WHERE title_name=?", (title,))
    title_id = cursor.fetchone()
    if title_id:
        cursor.execute("DELETE FROM chat_history WHERE title_id=?", (title_id[0],))
        conn.commit()


def delete_chat(conn, title):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_title WHERE title_name=?", (title,))
    conn.commit()


if __name__ == '__main__':
    # Call the function to create the database and tables
    conn = create_database_and_tables()
    load_chat_map(conn)