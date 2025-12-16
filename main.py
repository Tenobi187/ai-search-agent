import json
import uvicorn

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from agent import create_agent
from schemas import ResearchReport

app = FastAPI()
agent = create_agent()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


def report_to_markdown(report: ResearchReport) -> str:
    md = "### Ответ\n\n"
    md += report.answer.strip() + "\n\n"

    if report.sources:
        md += "### Источники\n"
        for src in report.sources:
            md += f'- <a href="{src}" target="_blank" rel="noopener noreferrer">{src}</a>\n'

    return md



@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    chat_history = []

    try:
        while True:
            question = await ws.receive_text()

            report = agent.invoke({
                "question": question,
                "history": chat_history
            })

           
            chat_history.append({
                "question": question,
                "answer": report.answer
            })

            await ws.send_text(json.dumps({
                "content": report_to_markdown(report)
            }))

    except Exception as e:
        await ws.send_text(json.dumps({
            "content": f"Ошибка: {e}"
        }))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
