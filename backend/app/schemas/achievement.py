from pydantic import BaseModel, Field, model_validator

class AchievementCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    points: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_points(self):
        if self.points < 0:
            raise ValueError("Points cannot be negative")
        return self