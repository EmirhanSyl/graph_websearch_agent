from openai.resources.containers.files import content
from termcolor import colored
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from models.openai_models import get_open_ai, get_open_ai_structured
from models.agent_schemas import (
    PlannerResponse,
    SelectorResponse,
    ReviewerResponse,
    RouterResponse,
)
from prompts.prompts import (
    planner_prompt_template,
    selector_prompt_template,
    reporter_prompt_template,
    reviewer_prompt_template,
    router_prompt_template,
)
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState


class Agent:
    def __init__(self, state: AgentGraphState, model="qwen3:4b", temperature=0):
        self.state = state
        self.model = model
        self.temperature = temperature

    def get_llm(self, json_model=True, model_class=None):
        if json_model and model_class is not None:
            return get_open_ai_structured(
                response_model=model_class,
                model=self.model,
                temperature=self.temperature,
            )
        return get_open_ai(model=self.model, temperature=self.temperature)

    def update_state(self, key, value):
        """Append the value to the list stored under ``key`` in ``self.state``."""
        current = self.state.get(key, [])
        if not isinstance(current, list):
            current = [current]
        current.append(value)
        self.state = {**self.state, key: current}

    def _patch(self, key):
        return {key: self.state[key]}


class PlannerAgent(Agent):
    def invoke(self, research_question, prompt=planner_prompt_template, feedback=None):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        planner_prompt = prompt.format(
            feedback=feedback_value, datetime=get_current_utc_datetime()
        )

        messages = [
            SystemMessage(content=planner_prompt),
            HumanMessage(content=f"research question: {research_question}"),
        ]
        print(messages)
        llm = self.get_llm(model_class=PlannerResponse)
        ai_msg = llm.invoke(messages)
        print(ai_msg)
        response = AIMessage(content=f"{ai_msg}")

        self.update_state("planner_response", response)
        print(colored(f"Planner 👩🏿‍💻: {response}", "cyan"))
        return self.state


class SelectorAgent(Agent):
    def invoke(
        self,
        research_question,
        prompt=selector_prompt_template,
        feedback=None,
        previous_selections=None,
        serp=None,
    ):
        feedback_value = feedback() if callable(feedback) else feedback
        previous_selections_value = (
            previous_selections()
            if callable(previous_selections)
            else previous_selections
        )

        feedback_value = check_for_content(feedback_value)
        previous_selections_value = check_for_content(previous_selections_value)

        selector_prompt = prompt.format(
            feedback=feedback_value,
            previous_selections=previous_selections_value,
            serp=serp().content,
            datetime=get_current_utc_datetime(),
        )

        messages = [
            {"role": "system", "content": selector_prompt},
            {"role": "user", "content": f"research question: {research_question}"},
        ]

        llm = self.get_llm(model_class=SelectorResponse)
        ai_msg = llm.invoke(messages)
        response = AIMessage(content=f"{ai_msg}")

        print(colored(f"selector 🧑🏼‍💻: {response}", "green"))
        self.update_state("selector_response", response)
        return self.state


class ReporterAgent(Agent):
    def invoke(
        self,
        research_question,
        prompt=reporter_prompt_template,
        feedback=None,
        previous_reports=None,
        research=None,
    ):
        feedback_value = feedback() if callable(feedback) else feedback
        previous_reports_value = (
            previous_reports() if callable(previous_reports) else previous_reports
        )
        research_value = research() if callable(research) else research

        feedback_value = check_for_content(feedback_value)
        previous_reports_value = check_for_content(previous_reports_value)
        research_value = check_for_content(research_value)

        reporter_prompt = prompt.format(
            feedback=feedback_value,
            previous_reports=previous_reports_value,
            datetime=get_current_utc_datetime(),
            research=research_value,
        )

        messages = [
            {"role": "system", "content": reporter_prompt},
            {"role": "user", "content": f"research question: {research_question}"},
        ]

        llm = self.get_llm(json_model=False)
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        print(colored(f"Reporter 👨‍💻: {response}", "yellow"))
        self.update_state("reporter_response", HumanMessage(content=response))
        return self.state


class ReviewerAgent(Agent):
    def invoke(
        self,
        research_question,
        prompt=reviewer_prompt_template,
        reporter=None,
        feedback=None,
    ):
        reporter_value = reporter() if callable(reporter) else reporter
        feedback_value = feedback() if callable(feedback) else feedback

        reporter_value = check_for_content(reporter_value)
        feedback_value = check_for_content(feedback_value)

        reviewer_prompt = prompt.format(
            reporter=reporter_value,
            state=self.state,
            feedback=feedback_value,
            datetime=get_current_utc_datetime(),
        )

        messages = [
            {"role": "system", "content": reviewer_prompt},
            {"role": "user", "content": f"research question: {research_question}"},
        ]

        llm = self.get_llm(model_class=ReviewerResponse)
        ai_msg = llm.invoke(messages)
        response = AIMessage(content=f"{ai_msg}")

        print(colored(f"Reviewer 👩🏽‍⚖️: {response}", "magenta"))
        self.update_state("reviewer_response", response)
        return self.state


class RouterAgent(Agent):
    def invoke(
        self, feedback=None, research_question=None, prompt=router_prompt_template
    ):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        router_prompt = prompt.format(feedback=feedback_value)

        messages = [
            {"role": "system", "content": router_prompt},
            {"role": "user", "content": f"research question: {research_question}"},
        ]

        llm = self.get_llm(model_class=RouterResponse)
        ai_msg = llm.invoke(messages)
        response = AIMessage(content=f"{ai_msg}")

        print(colored(f"Router 🧭: {response}", "blue"))
        self.update_state("router_response", response)
        return self.state


class FinalReportAgent(Agent):
    def invoke(self, final_response=None):
        final_response_value = (
            final_response() if callable(final_response) else final_response
        )
        response = final_response_value.content

        print(colored(f"Final Report 📝: {response}", "blue"))
        self.update_state("final_reports", response)
        return self.state


class EndNodeAgent(Agent):
    def invoke(self):
        self.update_state("end_chain", "end_chain")
        return self.state
