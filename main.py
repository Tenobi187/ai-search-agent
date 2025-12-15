import json
import uvicorn

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from agent import create_agent
from schemas import ResearchReport

app = FastAPI()
agent = create_agent()

# Статика
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


def report_to_markdown(report: ResearchReport) -> str:
    md = f"# {report.topic}\n\n"

    md += f"## Введение\n{report.introduction}\n\n"

    md += "## Ключевые факты\n"
    for item in report.key_findings:
        md += f"- {item}\n"

    md += f"\n## Заключение\n{report.conclusion}\n\n"

    if report.sources:
        md += "## Источники\n"
        for src in report.sources:
            md += f"- {src}\n"

    return md


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            question = await ws.receive_text()

            report = agent.invoke(question)
            answer_md = report_to_markdown(report)

            await ws.send_text(json.dumps({
                "content": answer_md
            }))

    except:
        pass


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
