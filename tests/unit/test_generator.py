"""Unit tests for the deterministic seed generator."""

from datetime import date

from app.generators.personas import PERSONAS
from app.generators.seed_demo import build_dataset


def test_build_dataset_returns_four_personas() -> None:
    users, _, _ = build_dataset(days=30, today=date(2026, 4, 28))
    assert len(users) == 4
    assert {u.id for u in users} == {p.user_id for p in PERSONAS}


def test_build_dataset_is_deterministic() -> None:
    a = build_dataset(days=30, today=date(2026, 4, 28))
    b = build_dataset(days=30, today=date(2026, 4, 28))

    assert [u.model_dump() for u in a[0]] == [u.model_dump() for u in b[0]]
    assert [w.model_dump(mode="json") for w in a[1]] == [w.model_dump(mode="json") for w in b[1]]
    assert [m.model_dump(mode="json") for m in a[2]] == [m.model_dump(mode="json") for m in b[2]]


def test_build_dataset_metric_count_matches_days() -> None:
    days = 14
    _, _, metrics = build_dataset(days=days, today=date(2026, 4, 28))
    # Each persona has exactly `days` daily_metrics
    per_user: dict = {}
    for m in metrics:
        per_user[m.user_id] = per_user.get(m.user_id, 0) + 1
    assert all(count == days for count in per_user.values())
    assert len(per_user) == 4


def test_overtrained_has_lower_recovery_than_novice() -> None:
    _, _, metrics = build_dataset(days=30, today=date(2026, 4, 28))
    overtrained = [m for m in metrics if str(m.user_id).startswith("44444444")]
    novice = [m for m in metrics if str(m.user_id).startswith("11111111")]
    assert overtrained and novice
    avg_overtrained = sum(m.recovery_score or 0 for m in overtrained) / len(overtrained)
    avg_novice = sum(m.recovery_score or 0 for m in novice) / len(novice)
    assert avg_overtrained < avg_novice


def test_advanced_has_more_workouts_than_novice() -> None:
    _, workouts, _ = build_dataset(days=30, today=date(2026, 4, 28))
    advanced = [w for w in workouts if str(w.user_id).startswith("22222222")]
    novice = [w for w in workouts if str(w.user_id).startswith("11111111")]
    assert len(advanced) > len(novice)


def test_oversleeper_has_more_sleep_than_overtrained() -> None:
    _, _, metrics = build_dataset(days=30, today=date(2026, 4, 28))
    oversleeper = [m for m in metrics if str(m.user_id).startswith("33333333")]
    overtrained = [m for m in metrics if str(m.user_id).startswith("44444444")]
    avg_o = sum(m.sleep_total_in_bed_time_milli or 0 for m in oversleeper) / len(oversleeper)
    avg_t = sum(m.sleep_total_in_bed_time_milli or 0 for m in overtrained) / len(overtrained)
    assert avg_o > avg_t
