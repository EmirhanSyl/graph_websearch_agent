from pydantic import BaseModel


class PlannerResponse(BaseModel):
    search_term: str
    overall_strategy: str
    additional_information: str


class SelectorResponse(BaseModel):
    selected_page_url: str
    description: str
    reason_for_selection: str


class ReviewerResponse(BaseModel):
    feedback: str
    pass_review: bool
    comprehensive: bool
    citations_provided: bool
    relevant_to_research_question: bool


class RouterResponse(BaseModel):
    next_agent: str
