"""Built-in tools — auto-register on import."""

from app.tools.builtin.get_daily_metrics import GetDailyMetricsTool
from app.tools.builtin.get_metrics_range import GetMetricsRangeTool
from app.tools.builtin.get_period_summary import GetPeriodSummaryTool
from app.tools.builtin.get_recent_workouts import GetRecentWorkoutsTool
from app.tools.builtin.get_user_profile import GetUserProfileTool
from app.tools.builtin.get_workout import GetWorkoutTool

__all__ = [
    "GetDailyMetricsTool",
    "GetMetricsRangeTool",
    "GetPeriodSummaryTool",
    "GetRecentWorkoutsTool",
    "GetUserProfileTool",
    "GetWorkoutTool",
]
