from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import (
    get_db,
    save_user,
    save_plan,
    update_plan,
    get_user,
    get_latest_plan,
    get_all_users
)

from .schemas import UserInput, FeedbackRequest

from .ai import (
    generate_workout_gemini,
    generate_nutrition_tip_with_flash,
    update_workout_plan
)

from .config import ADMIN_TOKEN


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# HOME PAGE
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# =========================================================
# GENERATE WORKOUT PLAN
# =========================================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    user_id: str = Form(...),

    name: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    experience: str = Form("Beginner"),

    db: Session = Depends(get_db)

):

    user_data = UserInput(

        user_id=user_id,

        name=name,

        age=age,

        weight=weight,

        goal=goal,

        intensity=intensity,

        experience=experience

    )


    # Save user

    user = save_user(

        db=db,

        user_id=user_data.user_id,

        name=user_data.name,

        age=user_data.age,

        weight=user_data.weight,

        goal=user_data.goal,

        intensity=user_data.intensity,

        experience=user_data.experience

    )


    # Generate AI workout

    workout_plan = generate_workout_gemini(

        name=user_data.name,

        age=user_data.age,

        weight=user_data.weight,

        goal=user_data.goal,

        intensity=user_data.intensity,

        experience=user_data.experience

    )


    # Generate nutrition tip

    nutrition_tip = generate_nutrition_tip_with_flash(

        user_data.goal

    )


    # Save generated plan

    save_plan(

        db=db,

        user_id=user_data.user_id,

        original_plan=workout_plan,

        nutrition_tip=nutrition_tip

    )


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "user": user,

            "workout_plan": workout_plan,

            "nutrition_tip": nutrition_tip,

            "updated_plan": None,

            "message": None

        }

    )


# =========================================================
# SUBMIT FEEDBACK
# =========================================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)

):

    user = get_user(

        db,

        user_id

    )


    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"

        )


    plan = get_latest_plan(

        db,

        user_id

    )


    if not plan:

        raise HTTPException(

            status_code=404,

            detail="Workout plan not found"

        )


    # Generate updated plan using AI

    updated = update_workout_plan(

        original_plan=plan.original_plan,

        feedback=feedback,

        goal=user.goal,

        intensity=user.intensity

    )


    # Save updated plan

    update_plan(

        db=db,

        user_id=user_id,

        updated_plan=updated,

        feedback=feedback

    )


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "user": user,

            "workout_plan": plan.original_plan,

            "nutrition_tip": plan.nutrition_tip,

            "updated_plan": updated,

            "message": "Your workout plan has been updated successfully."

        }

    )


# =========================================================
# ADMIN - VIEW ALL USERS
# =========================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    token: str = "",

    db: Session = Depends(get_db)

):

    if token != ADMIN_TOKEN:

        raise HTTPException(

            status_code=403,

            detail="Invalid admin token"

        )


    users = get_all_users(db)


    user_records = []


    for user in users:

        plan = get_latest_plan(

            db,

            user.user_id

        )


        user_records.append(

            {

                "user": user,

                "plan": plan

            }

        )


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={

            "records": user_records

        }

    )


# =========================================================
# API - GENERATE WORKOUT
# =========================================================

@router.post(
    "/api/generate-workout"
)
def api_generate_workout(

    data: UserInput,

    db: Session = Depends(get_db)

):

    user = save_user(

        db=db,

        user_id=data.user_id,

        name=data.name,

        age=data.age,

        weight=data.weight,

        goal=data.goal,

        intensity=data.intensity,

        experience=data.experience

    )


    workout = generate_workout_gemini(

        name=data.name,

        age=data.age,

        weight=data.weight,

        goal=data.goal,

        intensity=data.intensity,

        experience=data.experience

    )


    nutrition = generate_nutrition_tip_with_flash(

        data.goal

    )


    plan = save_plan(

        db=db,

        user_id=data.user_id,

        original_plan=workout,

        nutrition_tip=nutrition

    )


    return {

        "success": True,

        "user_id": user.user_id,

        "plan_id": plan.id,

        "workout_plan": workout,

        "nutrition_tip": nutrition

    }


# =========================================================
# API - UPDATE WORKOUT USING FEEDBACK
# =========================================================

@router.post(
    "/api/submit-feedback"
)
def api_submit_feedback(

    data: FeedbackRequest,

    db: Session = Depends(get_db)

):

    user = get_user(

        db,

        data.user_id

    )


    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"

        )


    plan = get_latest_plan(

        db,

        data.user_id

    )


    if not plan:

        raise HTTPException(

            status_code=404,

            detail="Workout plan not found"

        )


    updated = update_workout_plan(

        original_plan=plan.original_plan,

        feedback=data.feedback,

        goal=user.goal,

        intensity=user.intensity

    )


    update_plan(

        db=db,

        user_id=data.user_id,

        updated_plan=updated,

        feedback=data.feedback

    )


    return {

        "success": True,

        "user_id": data.user_id,

        "updated_plan": updated

    }


# =========================================================
# API - GET USER
# =========================================================

@router.get(
    "/api/users/{user_id}"
)
def api_get_user(

    user_id: str,

    db: Session = Depends(get_db)

):

    user = get_user(

        db,

        user_id

    )


    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"

        )


    plan = get_latest_plan(

        db,

        user_id

    )


    return {

        "user": {

            "user_id": user.user_id,

            "name": user.name,

            "age": user.age,

            "weight": user.weight,

            "goal": user.goal,

            "intensity": user.intensity,

            "experience": user.experience

        },

        "plan": {

            "original_plan": (

                plan.original_plan

                if plan

                else None

            ),

            "updated_plan": (

                plan.updated_plan

                if plan

                else None

            ),

            "nutrition_tip": (

                plan.nutrition_tip

                if plan

                else None

            ),

            "feedback": (

                plan.feedback

                if plan

                else None

            )

        }

    }