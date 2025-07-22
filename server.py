import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from agent_graph.graph import create_graph, compile_workflow

class WorkflowRunner:
    def __init__(self):
        self.workflow = None
        self.recursion_limit = 40

    def build_workflow(self, server="openai", model="qwen3:4b", model_endpoint=None, temperature=0, recursion_limit=40, stop=None):
        graph = create_graph(
            server=server,
            model=model,
            model_endpoint=model_endpoint,
            temperature=temperature,
            stop=stop,
        )
        self.workflow = compile_workflow(graph)
        self.recursion_limit = recursion_limit

    def run(self, message_content: str):
        if not self.workflow:
            return "Workflow has not been built yet."

        dict_inputs = {"research_question": message_content}
        limit = {"recursion_limit": self.recursion_limit}
        for event in self.workflow.stream(dict_inputs, limit):
            next_agent = ""
            if "router" in event.keys():
                state = event["router"]
                reviewer_state = state['router_response']
                if isinstance(reviewer_state, dict):
                    next_agent_value = reviewer_state.get("next_agent")
                elif hasattr(reviewer_state, "next_agent"):
                    next_agent_value = reviewer_state.next_agent
                else:
                    reviewer_state_dict = json.loads(reviewer_state)
                    next_agent_value = reviewer_state_dict["next_agent"]
                if isinstance(next_agent_value, list):
                    next_agent = next_agent_value[-1]
                else:
                    next_agent = next_agent_value

            if next_agent == "final_report":
                state = event["router"]
                reporter_state = state['reporter_response']
                if isinstance(reporter_state, list):
                    reporter_state = reporter_state[-1]
                return reporter_state.content if hasattr(reporter_state, "content") else reporter_state
        return "Workflow did not reach final report"

runner = WorkflowRunner()
runner.build_workflow()

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[Message]

@app.post("/chat")
def chat_endpoint(history: ChatHistory):
    if not history.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    last_user = next((m.content for m in reversed(history.messages) if m.role == "user"), None)
    if not last_user:
        raise HTTPException(status_code=400, detail="No user message found in history")
    response = runner.run(last_user)
    return {"response": response}