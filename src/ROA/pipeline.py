import os
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ROA.llm_language import detect_language_llm
from ROA.vectorstore_manager import get_retriever
from ROA.canvas_tools import canvas_tools

print("PIPELINE LOADED FROM:", __file__)


@tool
def search_documents(query: str) -> str:
    """
    Search for information within the uploaded academic documents.
    """
    retriever = get_retriever(k=8)
    docs = retriever.invoke(query)

    return "\n\n".join([
        f"Source: {d.metadata.get('source')}\nContent: {d.page_content}"
        for d in docs
    ])


def run_pipeline(
    question: str,
    retriever=None,
    language: str | None = None,
    history: list = None
):

    print("=========== PIPELINE START ===========")
    print("Pergunta:", question)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    )

    # Detect language
    if language is None:
        language = detect_language_llm(question, llm)

    print("Idioma detectado:", language)

    # Combine tools
    all_tools = [search_documents] + canvas_tools

    # System prompt (precisa ser STRING no LangChain 1.x)
    system_prompt = f"""
You are a strict academic AI assistant specialized in education and document analysis.
Your mission is to help students learn and understand academic materials and their Canvas courses.

YOU HAVE ACCESS TO TWO TYPES OF TOOLS:
1. search_documents → Search in uploaded PDFs/academic files.
2. Canvas Tools → Retrieve info from the student's Canvas (courses, assignments, etc.).

RESPONSE STRUCTURE:
[EXPLANATION]: Your clear academic explanation.
[DATA/CODE]: Retrieved data or code if needed.
[SOURCE]: Mention where the info came from (document or Canvas).

IMPORTANT: You MUST answer in {language}.
"""

    # Create agent
    agent = create_agent(
        model=llm,
        tools=all_tools,
        system_prompt=system_prompt
    )

    # Build messages
    messages = [SystemMessage(content=system_prompt)]

    # Add history if exists
    if history:
        for role, content in history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

    # Add current question
    messages.append(HumanMessage(content=question))

    print("=========== AGENT EXECUTION ===========")

    response = agent.invoke({
        "messages": messages
    })

    # LangChain 1.x returns messages
    answer = response["messages"][-1].content

    print("=========== AGENT RESPONSE ===========")
    print(answer)

    return answer