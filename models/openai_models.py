from langchain_openai import ChatOpenAI
from utils.helper_functions import load_config
import os

config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
load_config(config_path)


BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")


def get_open_ai(temperature: float = 0, model: str = "gpt-3.5-turbo"):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=BASE_URL,
    )
    return llm


def get_open_ai_structured(
    response_model, temperature: float = 0, model: str = "gpt-3.5-turbo"
):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        base_url=BASE_URL,
    ).with_structured_output(response_model)
    return llm
