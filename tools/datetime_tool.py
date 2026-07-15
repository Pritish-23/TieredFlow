import logging
import zoneinfo
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DateTimeTool:

    def get_current_datetime(self, timezone_str: str = "UTC") -> str:
        logger.info(f"[DateTime] Getting datetime for timezone: {timezone_str}")

        try:
            tz = zoneinfo.ZoneInfo(timezone_str)
            now = datetime.now(tz)

            return (
                f"Current Date & Time\n"
                f"Timezone:  {timezone_str}\n"
                f"Date:      {now.strftime('%A, %B %d, %Y')}\n"
                f"Time:      {now.strftime('%I:%M %p')}\n"
                f"Day:       {now.strftime('%A')}\n"
                f"Week:      Week {now.strftime('%W')} of {now.year}"
            )

        except Exception as e:
            logger.error(f"[DateTime] Failed: {e}")
            # Fallback to UTC
            now = datetime.now(timezone.utc)
            return (
                f"Current Date & Time (UTC)\n"
                f"Date: {now.strftime('%A, %B %d, %Y')}\n"
                f"Time: {now.strftime('%I:%M %p')}"
            )

    def extract_timezone(self, query: str) -> str:
        """
        Extract timezone from query string.
        Defaults to Asia/Kolkata for Indian users, UTC otherwise.
        """
        query_lower = query.lower()

        timezone_map = {
            "india": "Asia/Kolkata",
            "mumbai": "Asia/Kolkata",
            "delhi": "Asia/Kolkata",
            "new york": "America/New_York",
            "london": "Europe/London",
            "tokyo": "Asia/Tokyo",
            "sydney": "Australia/Sydney",
            "dubai": "Asia/Dubai",
            "paris": "Europe/Paris",
            "singapore": "Asia/Singapore",
        }

        for keyword, tz in timezone_map.items():
            if keyword in query_lower:
                return tz

        return "Asia/Kolkata"  # Default for you


# Singleton
_datetime_instance = None


def get_datetime_tool() -> DateTimeTool:
    global _datetime_instance
    if _datetime_instance is None:
        _datetime_instance = DateTimeTool()
    return _datetime_instance
