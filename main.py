"""
FastAPI backend — wires Track A (retrieve) and Track B (LangGraph agent)
together behind the API endpoints, with Neon persistence, Langfuse
tracing, and real speech transcription.
"""

import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))
sys.path.append(os.path.join(os.path.dirname(__file__), "rag"))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph_session_manager import rehearsal_graph
from retrieve import retrieve
from scorer import generate_session_report
from langfuse import observe, propagate_attributes
from db import init_db, save_session, get_all_sessions
from transcribe import transcribe_audio

app = FastAPI()
init_db()  # ensures the sessions table exists on startup

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Real per-role question banks — Role actually controls this.
QUESTION_BANKS = {
    "SDE": [
        "Tell me about a project you're proud of.",
        "Describe a time you disagreed with a teammate.",
        "How do you approach debugging a hard problem?",
    ],
    "Data Analyst": [
        "Walk me through a time you found an insight in messy data.",
        "How do you decide which metric actually matters for a decision?",
        "Describe a time your analysis was questioned or wrong.",
    ],
    "Product Mgr": [
        "Tell me about a product decision you made with incomplete data.",
        "Describe a time you said no to a stakeholder.",
        "How do you prioritize a roadmap when everything feels urgent?",
    ],
    "UX Design": [
        "Walk me through your design process for a recent project.",
        "Describe a time user feedback changed your design.",
        "How do you balance aesthetics with usability constraints?",
    ],
    "AI/ML Engineer": [
        "Tell me about a model or system you built end to end.",
        "Describe a time your model performed well offline but poorly in production.",
        "How do you evaluate whether an LLM-based feature is actually working?",
    ],
    "DevOps Engineer": [
        "Tell me about an incident you resolved under pressure.",
        "Describe a time you improved a deployment or CI/CD process.",
        "How do you decide what to automate vs leave manual?",
    ],
}
DEFAULT_ROLE = "SDE"

MAX_FOLLOWUPS_PER_QUESTION = 2

sessions = {}


class StartRequest(BaseModel):
    resume_text: str = ""
    job_description: str = ""
    role: str = DEFAULT_ROLE


class AnswerRequest(BaseModel):
    session_id: str
    question: str
    answer: str


class FinishRequest(BaseModel):
    session_id: str


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    text = transcribe_audio(audio_bytes, filename=file.filename or "audio.webm")
    return {"text": text}


@app.get("/sessions")
def list_sessions():
    """
    Powers the dashboard — real session history from Neon, most recent
    first. This is the endpoint the frontend's Score Trends, Practice
    Calendar, and Session Records widgets will all read from.
    """
    return get_all_sessions()


@app.post("/session/start")
def start_session(req: StartRequest):
    session_id = str(uuid.uuid4())
    role = req.role or DEFAULT_ROLE
    questions = QUESTION_BANKS.get(role, QUESTION_BANKS[DEFAULT_ROLE])
    sessions[session_id] = {
        "index": 0,
        "followup_count": 0,
        "history": [],
        "questions": questions,
        "role": role,
    }
    return {"session_id": session_id, "first_question": questions[0]}


@app.post("/session/answer")
@observe(name="submit-answer")
def submit_answer(req: AnswerRequest):
    session = sessions[req.session_id]
    session["history"].append({"question": req.question, "answer": req.answer})

    context = retrieve(f"{req.question} {req.answer}", k=2)
    remaining = session["questions"][session["index"] + 1:]

    result = rehearsal_graph.invoke({
        "question": req.question,
        "answer": req.answer,
        "persona": "behavioral",
        "remaining_questions": remaining,
        "context": context,
        "strength": "",
        "next_question": "",
        "is_followup": False,
    })
    next_q = result["next_question"]
    is_followup = result["is_followup"]
    strength = result["strength"]

    reached_cap = session["followup_count"] >= MAX_FOLLOWUPS_PER_QUESTION

    if is_followup and not reached_cap:
        session["followup_count"] += 1
        return {
            "feedback": "That's fairly vague — try to be more specific.",
            "next_question": next_q,
            "is_followup": True,
            "session_complete": False,
        }

    session["index"] += 1
    session["followup_count"] = 0
    done = session["index"] >= len(session["questions"])

    feedback = (
        "Good, that had real specifics in it." if strength == "strong"
        else "Still fairly general, but let's move on."
    )

    return {
        "feedback": feedback,
        "next_question": None if done else session["questions"][session["index"]],
        "is_followup": False,
        "session_complete": done,
    }


@app.post("/session/finish")
@observe(name="finish-session")
def finish_session(req: FinishRequest):
    session = sessions.pop(req.session_id, None)
    history = session["history"] if session else []
    role = session["role"] if session else DEFAULT_ROLE
    report = generate_session_report(history)

    save_session(req.session_id, role, report["score"], report["summary"])

    return {
        "summary": report["summary"],
        "score": report["score"],
    }