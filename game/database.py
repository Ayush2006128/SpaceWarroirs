import sqlite3
import os
from pathlib import Path

DB_PATH = Path("sw_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY,
            high_score INTEGER DEFAULT 0,
            highest_level INTEGER DEFAULT 1,
            music BOOLEAN DEFAULT 1,
            sfx BOOLEAN DEFAULT 1,
            mouse_ctrl BOOLEAN DEFAULT 0
        )
    ''')
    cursor.execute('SELECT count(*) FROM game_state')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO game_state (id, high_score, highest_level, music, sfx, mouse_ctrl)
            VALUES (1, 0, 1, 1, 1, 0)
        ''')
    conn.commit()
    conn.close()

def get_state():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT high_score, highest_level, music, sfx, mouse_ctrl FROM game_state WHERE id=1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "high_score": row[0],
            "highest_level": row[1],
            "music": bool(row[2]),
            "sfx": bool(row[3]),
            "mouse_ctrl": bool(row[4])
        }
    return {"high_score": 0, "highest_level": 1, "music": True, "sfx": True, "mouse_ctrl": False}

def save_high_score(score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE game_state SET high_score = ? WHERE id=1', (score,))
    conn.commit()
    conn.close()

def save_highest_level(level):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE game_state SET highest_level = ? WHERE id=1', (level,))
    conn.commit()
    conn.close()

def save_settings(music, sfx, mouse_ctrl):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE game_state 
        SET music = ?, sfx = ?, mouse_ctrl = ? 
        WHERE id=1
    ''', (int(music), int(sfx), int(mouse_ctrl)))
    conn.commit()
    conn.close()

def reset_to_default():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE game_state 
        SET music = 1, sfx = 1, mouse_ctrl = 0
        WHERE id=1
    ''')
    conn.commit()
    conn.close()
