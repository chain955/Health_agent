"""Deterministic seed generator for 4 demo personas (spec section 6)."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from app.data.db import dispose_engine, session_scope
from app.data.dto import DailyMetricsDTO, UserDTO, WorkoutDTO
from app.data.repositories import DailyMetricsRepo, UserRepo, WorkoutRepo
from app.generators.personas import PERSONAS, PersonaSpec

logger = logging.getLogger(__name__)

DEFAULT_DAYS = 30
GLOBAL_SEED = 20260428  # any change here invalidates all generated data


def _persona_seed(persona: PersonaSpec) -> int:
    return GLOBAL_SEED ^ (int(persona.user_id) & 0xFFFFFFFF)


def _deterministic_uuid(rng: random.Random) -> uuid.UUID:
    """UUID v4-ish but driven by the supplied RNG so the run stays deterministic."""

    return uuid.UUID(int=rng.getrandbits(128), version=4)


def build_user_dto(persona: PersonaSpec) -> UserDTO:
    return UserDTO(
        id=persona.user_id,
        first_name=persona.first_name,
        last_name=persona.last_name,
        bio=persona.bio,
        role="athlete",
        age=persona.age,
        gender=persona.gender,
        sports=list(persona.sports),
        height_cm=persona.height_cm,
        language="ru",
        weight_kg=Decimal(str(persona.weight_kg)),
        activities=list(persona.activities),
        unit_system="metric",
    )


def build_daily_metrics(
    persona: PersonaSpec, rng: random.Random, today: date, days: int
) -> list[DailyMetricsDTO]:
    out: list[DailyMetricsDTO] = []
    for offset in range(days):
        day = today - timedelta(days=days - 1 - offset)
        steps = rng.randint(*persona.steps_range)
        calories = int(steps * rng.uniform(0.04, 0.05))

        hr_avg = rng.randint(*persona.avg_hr_range)
        hr_max = hr_avg + rng.randint(20, 45)
        resting = rng.randint(*persona.resting_hr_range)
        hrv = round(rng.uniform(*persona.hrv_range), 4)
        recovery = rng.randint(*persona.recovery_range)

        sleep_total_min = rng.randint(*persona.sleep_total_minutes_range)
        sleep_total_milli = sleep_total_min * 60 * 1000
        sleep_start = datetime.combine(day, datetime.min.time(), tzinfo=UTC) - timedelta(
            hours=2, minutes=rng.randint(0, 90)
        )
        sleep_end = sleep_start + timedelta(minutes=sleep_total_min)

        rem = int(sleep_total_milli * rng.uniform(0.18, 0.24))
        slow_wave = int(sleep_total_milli * rng.uniform(0.16, 0.22))
        light = sleep_total_milli - rem - slow_wave - int(sleep_total_milli * 0.05)
        awake = int(sleep_total_milli * rng.uniform(0.02, 0.07))

        sources_obj = {
            "caloriesKcal": "activities",
            "hrAvgBpm": "activities",
            "hrMaxBpm": "activities",
            "recoveryScore": "whoop_recovery_api",
            "restingHeartRate": "whoop_recovery_api",
            "hrvRmssdMilli": "whoop_recovery_api",
            "spo2Percentage": "whoop_recovery_api",
            "skinTempCelsius": "whoop_recovery_api",
            "sleepTotalInBedTimeMilli": "whoop_sleep_api",
            "steps": "apple_health",
        }

        out.append(
            DailyMetricsDTO(
                id=_deterministic_uuid(rng),
                user_id=persona.user_id,
                iso_date=day,
                steps=steps,
                calories_kcal=calories,
                water_liters=Decimal(str(round(rng.uniform(1.2, 2.8), 2))),
                hr_avg_bpm=hr_avg,
                hr_max_bpm=hr_max,
                recovery_score=recovery,
                resting_heart_rate=resting,
                hrv_rmssd_milli=Decimal(str(hrv)),
                spo2_percentage=Decimal(str(round(rng.uniform(94.0, 98.5), 2))),
                skin_temp_celsius=Decimal(str(round(rng.uniform(33.5, 35.0), 2))),
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                timezone_offset=10800,  # +3:00 ru-RU
                nap=False,
                sleep_score_state="ok",
                sleep_total_in_bed_time_milli=sleep_total_milli + awake,
                sleep_total_awake_time_milli=awake,
                sleep_total_no_data_time_milli=0,
                sleep_total_light_sleep_time_milli=light,
                sleep_total_slow_wave_sleep_time_milli=slow_wave,
                sleep_total_rem_sleep_time_milli=rem,
                sleep_cycle_count=rng.randint(3, 6),
                sleep_disturbance_count=rng.randint(0, 4),
                sources_json=json.dumps(sources_obj),
                version=4,
            )
        )
    return out


_SPORT_TITLES = {
    "running": ("Утренняя пробежка", "Темповый бег", "Длинная пробежка", "Интервалы"),
    "cycling": ("Велозаезд", "Шоссейный велоцикл", "Гонка на велосипеде"),
    "swimming": ("Плавание в бассейне", "Открытая вода"),
    "strength": ("Силовая тренировка", "Жим/тяга", "Кроссфит"),
    "walking": ("Прогулка", "Длинная прогулка"),
    "yoga": ("Йога", "Растяжка"),
}


def build_workouts(
    persona: PersonaSpec, rng: random.Random, today: date, days: int
) -> list[WorkoutDTO]:
    out: list[WorkoutDTO] = []
    for offset in range(days):
        day = today - timedelta(days=days - 1 - offset)
        # Bernoulli-ish — probability of any workout on this day
        prob = max(0.0, min(1.0, persona.workouts_per_week_mean / 7.0))
        # Add a small random kick so we don't always pick exactly one
        if rng.random() > prob:
            continue
        # Some advanced/overtrained days have two workouts
        n = 1
        if rng.random() < max(0.0, (persona.workouts_per_week_mean - 5.0) / 10.0):
            n = 2
        for slot in range(n):
            sport = rng.choice(persona.sports)
            title = rng.choice(_SPORT_TITLES.get(sport, ("Тренировка",)))
            duration_min = rng.randint(*persona.workout_duration_min)
            distance_m: int | None
            if persona.workout_distance_m_min is not None and sport in {
                "running",
                "cycling",
                "swimming",
                "walking",
            }:
                distance_m = rng.randint(*persona.workout_distance_m_min)
            else:
                distance_m = None
            avg_hr = rng.randint(*persona.avg_hr_range)
            max_hr = avg_hr + rng.randint(15, 35)
            calories = int(duration_min * rng.uniform(7, 12))
            speed = (distance_m / max(1, duration_min * 60)) * 3.6 if distance_m else None
            start = datetime.combine(day, datetime.min.time(), tzinfo=UTC) + timedelta(
                hours=7 + slot * 6, minutes=rng.randint(0, 50)
            )
            end = start + timedelta(minutes=duration_min)
            out.append(
                WorkoutDTO(
                    id=_deterministic_uuid(rng),
                    user_id=persona.user_id,
                    title=title,
                    sport_type=sport,
                    distance_meters=distance_m,
                    duration_seconds=duration_min * 60,
                    start_time=start,
                    end_time=end,
                    avg_speed=Decimal(str(round(speed, 2))) if speed is not None else None,
                    max_speed=Decimal(str(round((speed or 0) * 1.2, 2)))
                    if speed is not None
                    else None,
                    elevation_meters=rng.randint(0, 250)
                    if sport in {"running", "cycling"}
                    else None,
                    calories=calories,
                    avg_heart_rate=avg_hr,
                    max_heart_rate=max_hr,
                    source_platform=rng.choice(("garmin", "apple_health", "whoop")),
                    raw_title=title,
                )
            )
    return out


def build_dataset(
    days: int = DEFAULT_DAYS, today: date | None = None
) -> tuple[list[UserDTO], list[WorkoutDTO], list[DailyMetricsDTO]]:
    """Build a deterministic dataset for all 4 personas.

    Same args → same UUIDs and same metric values, every time.
    """
    today = today or date(2026, 4, 28)
    users: list[UserDTO] = []
    workouts: list[WorkoutDTO] = []
    metrics: list[DailyMetricsDTO] = []
    for persona in PERSONAS:
        rng = random.Random(_persona_seed(persona))
        users.append(build_user_dto(persona))
        metrics.extend(build_daily_metrics(persona, rng, today, days))
        workouts.extend(build_workouts(persona, rng, today, days))
    return users, workouts, metrics


async def run_seed(days: int = DEFAULT_DAYS, reset: bool = False) -> dict[str, int]:
    """Seed the database with the deterministic demo dataset."""

    users, workouts, metrics = build_dataset(days=days)

    async with session_scope() as session:
        user_repo = UserRepo(session)
        workout_repo = WorkoutRepo(session)
        metrics_repo = DailyMetricsRepo(session)

        if reset:
            for u in users:
                await workout_repo.delete_by_user(u.id)
                await metrics_repo.delete_by_user(u.id)

        await user_repo.upsert_many(users)
        await workout_repo.upsert_many(workouts)
        await metrics_repo.upsert_many(metrics)

    return {"users": len(users), "workouts": len(workouts), "daily_metrics": len(metrics)}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed demo dataset (4 personas).")
    parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS, help="History window per persona (days)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing workouts/daily_metrics for the demo personas before reseeding.",
    )
    return parser.parse_args()


async def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = _parse_args()
    counts = await run_seed(days=args.days, reset=args.reset)
    logger.info("seed-demo done: %s", counts)
    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(_main())
