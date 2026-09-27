from google import genai

from .config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    DEMO_MODE
)


client = None

if GOOGLE_API_KEY and not DEMO_MODE:

    client = genai.Client(
        api_key=GOOGLE_API_KEY
    )


def demo_workout(
    name,
    age,
    weight,
    goal,
    intensity,
    experience
):

    return f"""
FITBUDDY - PERSONALIZED 7 DAY WORKOUT PLAN

Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}
Experience: {experience}


DAY 1 - FULL BODY

Warm-up:
5-10 minutes of walking and dynamic stretching.

Exercises:
1. Bodyweight Squats - 3 sets x 12 reps
2. Push-ups - 3 sets x 8 reps
3. Glute Bridges - 3 sets x 12 reps
4. Plank - 3 sets x 30 seconds

Cooldown:
5 minutes of gentle stretching.


DAY 2 - CARDIO

Warm-up:
5 minutes easy walking.

Exercises:
1. Brisk Walking - 20 minutes
2. Jumping Jacks - 3 x 30 seconds
3. Mountain Climbers - 3 x 20 seconds

Cooldown:
5 minutes stretching.


DAY 3 - UPPER BODY

Warm-up:
5-10 minutes mobility exercises.

Exercises:
1. Push-ups - 3 sets x 8 reps
2. Shoulder Taps - 3 sets x 12 reps
3. Wall Push-ups - 3 sets x 12 reps
4. Plank - 3 sets x 30 seconds

Cooldown:
5 minutes stretching.


DAY 4 - ACTIVE RECOVERY

1. Easy Walking - 20 minutes
2. Light Stretching - 10 minutes
3. Breathing Exercises - 5 minutes


DAY 5 - LOWER BODY

Warm-up:
5-10 minutes.

Exercises:
1. Squats - 3 sets x 12 reps
2. Lunges - 3 sets x 10 each leg
3. Glute Bridges - 3 sets x 15 reps
4. Calf Raises - 3 sets x 15 reps

Cooldown:
5 minutes stretching.


DAY 6 - CARDIO + CORE

Warm-up:
5 minutes.

Exercises:
1. Brisk Walking - 20 minutes
2. Crunches - 3 sets x 12 reps
3. Plank - 3 sets x 30 seconds
4. Bicycle Crunches - 3 sets x 10 reps

Cooldown:
5 minutes stretching.


DAY 7 - REST AND RECOVERY

Take a rest day.

Perform gentle stretching if comfortable.


GENERAL SAFETY

Start slowly and increase difficulty gradually.

Stop exercising if you experience pain,
dizziness, or unusual discomfort.
"""


def generate_workout_gemini(
    name,
    age,
    weight,
    goal,
    intensity,
    experience
):

    if DEMO_MODE or client is None:

        return demo_workout(
            name,
            age,
            weight,
            goal,
            intensity,
            experience
        )


    prompt = f"""
You are FitBuddy,
an AI fitness planning assistant.

Create a personalized 7-day workout plan.

USER DETAILS

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness Goal: {goal}
Workout Intensity: {intensity}
Experience Level: {experience}


REQUIREMENTS

1. Generate exactly 7 days.
2. Include a clear focus for every day.
3. Include warm-up.
4. Include exercises.
5. Include sets and repetitions or duration.
6. Include rest periods.
7. Include cooldown or recovery guidance.
8. Include appropriate rest or recovery days.
9. Make the plan practical for the selected intensity.
10. Do not diagnose or treat medical conditions.
11. Tell the user to stop if they experience
    pain, dizziness, or unusual symptoms.
12. Format the response clearly.

Return only the workout plan.
"""


    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


def generate_nutrition_tip_with_flash(goal):

    if DEMO_MODE or client is None:

        tips = {

            "Weight Loss":
                "Focus on balanced meals, vegetables, "
                "adequate protein, water, and reasonable portions.",

            "Muscle Gain":
                "Include a protein source in each meal "
                "and stay hydrated to support training and recovery.",

            "General Wellness":
                "Maintain balanced meals with vegetables, "
                "fruits, whole grains, protein, and adequate water.",

            "Flexibility":
                "Stay hydrated and include nutrient-rich "
                "foods that support overall recovery."

        }

        return tips.get(
            goal,
            "Eat balanced meals, stay hydrated, "
            "and maintain consistent healthy eating habits."
        )


    prompt = f"""
You are a fitness nutrition assistant.

User fitness goal:

{goal}

Give one concise nutrition or recovery tip
that supports this goal.

Do not prescribe medical treatment.

Do not provide extreme dieting advice.

Keep the response under 100 words.
"""


    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text


def update_workout_plan(
    original_plan,
    feedback,
    goal,
    intensity
):

    if DEMO_MODE or client is None:

        return f"""
UPDATED FITBUDDY WORKOUT PLAN

Original Goal: {goal}

Intensity: {intensity}

User Feedback:

{feedback}


PLAN UPDATE

The workout plan has been adjusted
according to the user's feedback.


DAY 1

Continue the existing workout.

Adjust the intensity if necessary.


DAY 2

Add moderate cardio according to
the user's preference.


DAY 3

Continue strength training with
appropriate rest.


DAY 4

Use as an active recovery or rest day.


DAY 5

Continue lower-body exercises
with controlled repetitions.


DAY 6

Include moderate cardio and
core exercises.


DAY 7

Rest and recovery.


IMPORTANT

Increase difficulty gradually.

Stop if you experience pain,
dizziness, or unusual discomfort.
"""


    prompt = f"""
You are FitBuddy,
an AI fitness planning assistant.


ORIGINAL WORKOUT PLAN:

{original_plan}


FITNESS GOAL:

{goal}


WORKOUT INTENSITY:

{intensity}


USER FEEDBACK:

{feedback}


Create an updated 7-day workout plan.

Requirements:

1. Keep the original fitness goal.
2. Apply the user's feedback.
3. Preserve a sensible weekly structure.
4. Include warm-up.
5. Include exercises.
6. Include sets/repetitions or duration.
7. Include rest.
8. Include cooldown/recovery.
9. Include rest days where appropriate.
10. Do not provide medical treatment.
11. Clearly present the revised plan.

Return only the updated workout plan.
"""


    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text