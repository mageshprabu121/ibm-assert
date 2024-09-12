from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_database():
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            question TEXT NOT NULL,
            transcript TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    create_database()

@app.post("/save-assessment")
async def save_assessment(request: Request):
    data = await request.json()
    name = data['name']
    email = data['email']
    questions = data['questions']
    transcripts = data['transcripts']

    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()

    try:
        for i, question in enumerate(questions):
            transcript = transcripts[i] if i < len(transcripts) else None
            cursor.execute('''
                INSERT INTO assessments (name, email, question, transcript)
                VALUES (?, ?, ?, ?)
            ''', (name, email, question, transcript))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"status": "success"}
