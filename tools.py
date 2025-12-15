import requests
from langchain_core.tools import tool
from config import SERPER_API_KEY


@tool
def web_search(query: str) -> str:
    """
    Поиск информации в интернете.
    """
    response = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        },
        json={"q": query}
    )

    if response.status_code != 200:
        return "Ошибка при поиске в интернете."

    data = response.json()
    results = []

    for item in data.get("organic", [])[:5]:
        results.append(
            f"{item.get('title')}\n{item.get('snippet')}"
        )

    return "\n\n".join(results) or "Ничего не найдено."
