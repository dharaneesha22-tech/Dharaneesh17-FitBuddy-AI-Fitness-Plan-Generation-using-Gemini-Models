from pydantic import BaseModel, Field


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        lt=300
    )

    goal: str

    intensity: str

    experience: str = "Beginner"


class FeedbackRequest(BaseModel):

    user_id: str

    feedback: str = Field(
        min_length=3,
        max_length=1000
    )