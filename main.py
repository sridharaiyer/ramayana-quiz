import json
import random
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load questions from JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/quiz", response_class=HTMLResponse)
async def start_quiz(request: Request):
    # Select 20 random questions
    quiz_questions = random.sample(questions, 20)

    # Initialize score
    user_answers = {}
    return templates.TemplateResponse(
        "quiz.html",
        {"request": request, "questions": quiz_questions,
            "user_answers": user_answers},
    )


@app.post("/submit_quiz", response_class=HTMLResponse)
async def submit_quiz(request: Request):
    form_data = await request.form()
    # Get all question ids from the form and load the questions
    answers = dict(form_data)
    question_ids = [int(key.split("_")[1])
                    for key in answers if key.startswith("question_")]
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
        "result.html", {"request": request, "score": score, "total_questions": len(
            submitted_questions), "submitted_questions": submitted_questions, "user_answers": user_answers}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
