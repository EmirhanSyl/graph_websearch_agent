from pydantic import BaseModel, Field


class PlannerResponse(BaseModel):
    """Planner agent output describing the search strategy."""

    search_term: str = Field(
        ..., description="Final query string the planner recommends searching"
    )
    overall_strategy: str = Field(
        ..., description="High-level explanation of how to gather the information"
    )
    additional_information: str = Field(
        ..., description="Extra notes or context that may help later agents"
    )


class SelectorResponse(BaseModel):
    """Selection of the best web page from search results."""

    selected_page_url: str = Field(
        ..., description="URL of the page that most closely matches the intent"
    )
    description: str = Field(
        ..., description="One sentence summary of what the selected page contains"
    )
    reason_for_selection: str = Field(
        ..., description="Explanation of why this page was chosen over others"
    )


class ReviewerResponse(BaseModel):
    """Review of the final answer ensuring accuracy and completeness."""

    feedback: str = Field(
        ..., description="Detailed comments on the quality of the answer"
    )
    pass_review: bool = Field(
        ..., description="Whether the answer meets the reviewer's standards"
    )
    comprehensive: bool = Field(
        ..., description="Indicates if the answer fully covers the topic"
    )
    citations_provided: bool = Field(
        ..., description="True if all claims are backed with proper citations"
    )
    relevant_to_research_question: bool = Field(
        ..., description="True when the answer directly addresses the question"
    )


class RouterResponse(BaseModel):
    """Instruction on which agent should run next."""

    next_agent: str = Field(
        ..., description="Name of the subsequent agent to execute"
    )