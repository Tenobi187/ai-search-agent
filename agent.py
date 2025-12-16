import re

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser

from tools import web_search
from prompts import SEARCH_PROMPT
from config import GROQ_API_KEY, MODEL_NAME
from schemas import ResearchReport


URL_RE = re.compile(r"https?://[^\s]+")


def extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("JSON not found")
    return text[start:end + 1]


def safe_parse(parser, text: str) -> ResearchReport:
    return parser.parse(extract_json(text))


def create_agent():
    model = ChatGroq(
        model=MODEL_NAME,
        temperature=0.2,
        groq_api_key=GROQ_API_KEY
    )

    parser = PydanticOutputParser(pydantic_object=ResearchReport)

    def run(input_data: dict) -> ResearchReport:
        question = input_data["question"]
        history = input_data.get("history", [])

        search_results = web_search.invoke(question)

        prompt = SEARCH_PROMPT.format(
            question=question,
            history=history,
            search_results=search_results,
            format_instructions=parser.get_format_instructions()
        )

        response = model.invoke([HumanMessage(content=prompt)])
        report = safe_parse(parser, response.content)

        
        clean_sources = []
        for s in report.sources:
            if URL_RE.match(s) and s not in clean_sources:
                clean_sources.append(s)

        if not clean_sources:
            clean_sources = URL_RE.findall(search_results)[:5]

        report.sources = clean_sources
        return report

    return RunnableLambda(run)
