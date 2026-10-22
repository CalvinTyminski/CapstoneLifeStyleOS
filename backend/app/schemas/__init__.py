#This is so its a package and has a clean import path.


from .goals import GoalCreate
from .achievement import AchievementCreate

__all__ = ["GoalCreate", "AchievementCreate"]
