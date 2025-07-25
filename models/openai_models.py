from langchain_openai import ChatOpenAI

BASE_URL = "http://localhost:11434/v1"


def get_open_ai(temperature: float = 0, model: str = "qwen3:4b"):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key="dummy",
        base_url=BASE_URL,
    )
    return llm


def get_open_ai_structured(
    response_model, temperature: float = 0, model: str = "qwen3:4b"
):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key="dummy",
        base_url=BASE_URL,

    ).with_structured_output(schema=response_model, method="json_mode")
    return llm
