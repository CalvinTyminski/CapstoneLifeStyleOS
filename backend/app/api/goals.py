
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.goal import Goal, GoalCompletion
from app.schemas.goals import (
    GoalCreate,
    GoalResponse,
    GoalCompletionResponse,
)
from app.services.goal_service import (
    GoalError,
    complete_goal,
    get_goal_reward,
)


router = APIRouter(
    prefix="/api/goals",
    tags=["Goals"],
)


@router.post(
    "",
    response_model=GoalResponse,
    status_code=201,
)
def create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        reward = get_goal_reward(data.type)
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    goal = Goal(
        user_id=current_user.id,
        name=data.name,
        type=data.type.upper(),
        start_date=data.start_date,
        end_date=data.end_date,
        reward_amount=reward,
    )

    try:
        db.add(goal)
        db.commit()
        db.refresh(goal)
    except Exception:
        db.rollback()
        raise

    return GoalResponse(
        id=goal.id,
        name=goal.name,
        type=goal.type,
        start_date=goal.start_date,
        end_date=goal.end_date,
        reward_amount=goal.reward_amount,
        completed=False,
    )


@router.get(
    "",
    response_model=list[GoalResponse],
)
def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Goal, GoalCompletion.id)
        .outerjoin(
            GoalCompletion,
            GoalCompletion.goal_id == Goal.id,
        )
        .where(Goal.user_id == current_user.id)
        .order_by(Goal.id.desc())
    ).all()

    return [
        GoalResponse(
            id=goal.id,
            name=goal.name,
            type=goal.type,
            start_date=goal.start_date,
            end_date=goal.end_date,
            reward_amount=goal.reward_amount,
            completed=completion_id is not None,
        )
        for goal, completion_id in rows
    ]


@router.post(
    "/{goal_id}/complete",
    response_model=GoalCompletionResponse,
)
def complete_user_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return complete_goal(
            db=db,
            user_id=current_user.id,
            goal_id=goal_id,
        )
    except GoalError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        )
