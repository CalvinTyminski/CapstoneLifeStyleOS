from datetime import date
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import ConfigDict
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
    
    
class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    start_date: date
    end_date: date | None
    reward_amount: Decimal
    completed: bool


class GoalCompletionResponse(BaseModel):
    goal_id: int
    transaction_id: UUID
    reward_amount: Decimal
    balance: Decimal
    already_completed: bool

