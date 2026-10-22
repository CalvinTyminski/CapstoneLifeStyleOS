
from datetime import date

from pydantic import BaseModel, Field, model_validator


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=50)
    start_date: date = Field(default_factory=date.today)
    end_date: date | None = None


    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        return self
