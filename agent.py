from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

from tools import web_search
from prompts import SEARCH_PROMPT
from config import GROQ_API_KEY, MODEL_NAME
from schemas import ResearchReport


def create_agent():
    # Базовая модель
    base_model = ChatGroq(
        model=MODEL_NAME,
        temperature=0.2,
        groq_api_key=GROQ_API_KEY
    )

    # структурированный вывод
    model = base_model.with_structured_output(ResearchReport)

    def run(question: str) -> ResearchReport:
        search_results = web_search.invoke(question)

        prompt = SEARCH_PROMPT.format(
            question=question,
            search_results=search_results
        )

        # Возвращается строго ResearchReport
        report: ResearchReport = model.invoke(
            [HumanMessage(content=prompt)]
        )

        return report

    return RunnableLambda(run)
