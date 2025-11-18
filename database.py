# database.py
import sqlite3
import json
from datetime import datetime

DB = "analysis_history.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_type TEXT,
        input_preview TEXT,
        summary TEXT,
        fake_label TEXT,
        real_prob REAL,
        fake_prob REAL,
        sentiment_label TEXT,
        sentiment_score REAL,
        emotion_label TEXT,
        topics TEXT,
        keywords TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_analysis(input_type, input_preview, results):
    summary = results.get("summary","")
    fake = results.get("fake",{})
    sentiment = results.get("sentiment",{})
    emotion = results.get("emotion",{})
    topics = results.get("topics",{})
    keywords = results.get("keywords",[])

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (
            input_type, input_preview, summary, fake_label,
            real_prob, fake_prob, sentiment_label, sentiment_score,
            emotion_label, topics, keywords, timestamp
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        input_type,
        input_preview,
        summary,
        fake.get("label","UNKNOWN"),
        float(fake.get("real_prob",0.0)),
        float(fake.get("fake_prob",0.0)),
        sentiment.get("label","UNKNOWN"),
        float(sentiment.get("score",0.0)),
        emotion.get("top_emotion","neutral"),
        topics.get("top_topic","unknown"),
        json.dumps(keywords),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_all_history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT input_type, input_preview, summary, fake_label, real_prob, fake_prob, sentiment_label, emotion_label, topics, keywords, timestamp FROM history ORDER BY ROWID DESC")
    rows = c.fetchall()
    conn.close()
    history = []
    for r in rows:
        history.append({
            "input_type": r[0],
            "input_preview": r[1],
            "summary": r[2],
            "fake_label": r[3],
            "real_prob": r[4],
            "fake_prob": r[5],
            "sentiment_label": r[6],
            "emotion_label": r[7],
            "topics": r[8],
            "keywords": json.loads(r[9] or "[]"),
            "timestamp": r[10]
        })
    return history
