from rocketry import Rocketry  # type: ignore
from rocketry.conds import cron as _cron  # type: ignore

scheduler = Rocketry(execution="async")


# wrap the Rocketry cron to satisfy mypy
def cron(expr: str):
    """Evaluate a cron expression as a Rocketry task"""
    return _cron(expr)
