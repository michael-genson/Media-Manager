from pydantic import BaseSettings


class SchedulerSettings(BaseSettings):
    """Cron expressions for scheduled tasks"""

    expired_media: str = "0 0 * * Sun"
