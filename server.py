import asyncio
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

TASKS_FILE = Path("tasks.json")

app = FastAPI()

app.mount("/public", StaticFiles(directory="public"), name="public")

class Tasks(BaseModel):
    tasks: list[str]

model_ready = False

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

model_ready = True

async def rewrite_task(task: str) -> str:
    inputs = tokenizer.encode(task, return_tensors="pt", max_length=512, truncation=True).to(device)
    outputs = model.generate(inputs, max_length=50, num_beams=4, early_stopping=True)
    rewritten = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rewritten

@app.get("/health")
async def health_check():
    if model_ready:
        return JSONResponse(content={"status": "ready"})
    return JSONResponse(content={"status": "loading"}, status_code=503)

@app.get("/")
async def root():
    return FileResponse("public/index.html")

@app.get("/tasks")
async def get_tasks():
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    else:
        tasks = []
    return tasks

@app.post("/save_tasks")
async def save_tasks(tasks: Tasks):
    rewritten_tasks = await asyncio.gather(*(rewrite_task(t) for t in tasks.tasks))
    TASKS_FILE.write_text(json.dumps(rewritten_tasks, indent=2))
    return {"status": "ok", "rewritten": rewritten_tasks}
