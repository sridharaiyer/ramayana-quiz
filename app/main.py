import json
import random
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# My quizes app
app = FastAPI()

# Constants for paths
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"
QUESTIONS_PATH = Path(__file__).parent / "questions.json"

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Set up templates directory
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Load questions from JSON file
with open(QUESTIONS_PATH, "r") as f:
    questions = json.load(f)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/quiz", response_class=HTMLResponse)
async def start_quiz(request: Request):
    quiz_questions = random.sample(questions, 20)
    user_answers = {}
    return templates.TemplateResponse(
        "quiz.html",
        {"request": request, "questions": quiz_questions, "user_answers": user_answers},
    )

@app.post("/submit_quiz", response_class=HTMLResponse)
async def submit_quiz(request: Request):
    form_data = await request.form()
    answers = dict(form_data)
    question_ids = [int(key.split("_")[1]) for key in answers if key.startswith("question_")]
    submitted_questions = [q for q in questions if q["id"] in question_ids]

    score = 0
    user_answers = {}
    for question in submitted_questions:
        answer_key = f"question_{question['id']}"
        user_answer = answers.get(answer_key)
        if user_answer == question["correct_answer"]:
            score += 1
        user_answers[answer_key] = user_answer

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "score": score,
            "total_questions": len(submitted_questions),
            "submitted_questions": submitted_questions,
            "user_answers": user_answers,
        },
    )
