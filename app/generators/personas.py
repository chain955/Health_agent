"""Four fixed personas for deterministic seed generation (spec 6, MVP)."""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class PersonaSpec:
    """Static description of a persona used by the seed generator."""

    key: str  # "novice", "advanced", "oversleeper", "overtrained"
    user_id: uuid.UUID
    first_name: str
    last_name: str
    bio: str
    age: int
    gender: str
    sports: tuple[str, ...]
    height_cm: int
    weight_kg: float
    activities: tuple[str, ...]

    # Statistical profile
    workouts_per_week_mean: float
    workouts_per_week_std: float
    workout_duration_min: tuple[int, int]
    workout_distance_m_min: tuple[int, int] | None  # None when sport has no distance
    avg_hr_range: tuple[int, int]
    resting_hr_range: tuple[int, int]
    hrv_range: tuple[float, float]
    recovery_range: tuple[int, int]
    sleep_total_minutes_range: tuple[int, int]
    steps_range: tuple[int, int]


PERSONAS: tuple[PersonaSpec, ...] = (
    PersonaSpec(
        key="novice",
        user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        first_name="Анна",
        last_name="Новикова",
        bio="Начала бегать три месяца назад. Цель — пробежать 5 км без остановки.",
        age=29,
        gender="female",
        sports=("running",),
        height_cm=168,
        weight_kg=62.5,
        activities=("running", "walking"),
        workouts_per_week_mean=2.0,
        workouts_per_week_std=0.7,
        workout_duration_min=(20, 35),
        workout_distance_m_min=(2500, 4500),
        avg_hr_range=(145, 165),
        resting_hr_range=(64, 72),
        hrv_range=(35.0, 55.0),
        recovery_range=(55, 80),
        sleep_total_minutes_range=(420, 480),
        steps_range=(6000, 11000),
    ),
    PersonaSpec(
        key="advanced",
        user_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        first_name="Дмитрий",
        last_name="Кузнецов",
        bio="Триатлет-любитель. Готовится к Ironman 70.3.",
        age=34,
        gender="male",
        sports=("running", "cycling", "swimming"),
        height_cm=181,
        weight_kg=76.0,
        activities=("running", "cycling", "swimming", "strength"),
        workouts_per_week_mean=6.5,
        workouts_per_week_std=1.0,
        workout_duration_min=(45, 120),
        workout_distance_m_min=(8000, 80000),
        avg_hr_range=(135, 160),
        resting_hr_range=(48, 56),
        hrv_range=(70.0, 110.0),
        recovery_range=(60, 90),
        sleep_total_minutes_range=(420, 510),
        steps_range=(8000, 14000),
    ),
    PersonaSpec(
        key="oversleeper",
        user_id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        first_name="Мария",
        last_name="Соловьёва",
        bio="Работает удалённо, спит много, активность нерегулярная.",
        age=41,
        gender="female",
        sports=("walking", "yoga"),
        height_cm=164,
        weight_kg=70.0,
        activities=("walking", "yoga"),
        workouts_per_week_mean=1.5,
        workouts_per_week_std=0.6,
        workout_duration_min=(30, 60),
        workout_distance_m_min=None,  # yoga / walking — distance скорее null
        avg_hr_range=(95, 120),
        resting_hr_range=(58, 66),
        hrv_range=(55.0, 80.0),
        recovery_range=(70, 92),
        sleep_total_minutes_range=(540, 660),
        steps_range=(3000, 7500),
    ),
    PersonaSpec(
        key="overtrained",
        user_id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
        first_name="Игорь",
        last_name="Васильев",
        bio="Готовится к марафону, последние недели тренируется почти каждый день.",
        age=38,
        gender="male",
        sports=("running", "strength"),
        height_cm=178,
        weight_kg=72.0,
        activities=("running", "strength"),
        workouts_per_week_mean=8.0,
        workouts_per_week_std=0.8,
        workout_duration_min=(60, 110),
        workout_distance_m_min=(10000, 25000),
        avg_hr_range=(150, 175),
        resting_hr_range=(60, 72),  # повышен из-за переутомления
        hrv_range=(20.0, 38.0),  # упал
        recovery_range=(20, 45),  # низкий
        sleep_total_minutes_range=(330, 410),
        steps_range=(7000, 13000),
    ),
)


def get_persona(key: str) -> PersonaSpec:
    for p in PERSONAS:
        if p.key == key:
            return p
    raise KeyError(f"unknown persona: {key}")
