"""Configuration management for SMZDM Bot.

Configuration is loaded from environment variables using Pydantic Settings.

Environment Variables:
    SMZDM_COOKIE: Cookie string (single user mode)
    SMZDM_SK: Optional security key
    SMZDM_USERS: JSON array for multi-user mode
        Example: '[{"cookie": "...", "sk": "..."}, {"cookie": "..."}]'

    Notification:
    SMZDM_PUSH_PLUS_TOKEN: PushPlus token
    SMZDM_SC_KEY: ServerChan key
    SMZDM_WECOM_WEBHOOK: WeCom bot webhook URL
    SMZDM_TG_BOT_TOKEN: Telegram bot token
    SMZDM_TG_USER_ID: Telegram user/chat ID
    SMZDM_TG_API_BASE: Custom Telegram API base URL

    Scheduler:
    SMZDM_SCH_HOUR: Hour to run (0-23)
    SMZDM_SCH_MINUTE: Minute to run (0-59)
    SMZDM_TIMEZONE: Timezone (default: Asia/Shanghai)
"""

import json
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from smzdm_bot.exceptions import ConfigurationError


def _find_dotenv() -> Path | None:
    """Find .env file by searching up from cwd or using package location."""
    # Try current directory first
    cwd = Path.cwd()
    if (cwd / ".env").exists():
        return cwd / ".env"

    # Try package directory (for installed package)
    pkg_dir = Path(__file__).parent.parent.parent.parent  # src/smzdm_bot/config -> root
    if (pkg_dir / ".env").exists():
        return pkg_dir / ".env"

    return None


class UserConfig(BaseModel):
    """Configuration for a single user account.

    Attributes:
        cookie: SMZDM cookie string.
        sk: Optional security key from app.
        name: Optional user identifier for logging.
    """

    cookie: str
    sk: str = ""
    name: str = ""

    @field_validator("cookie")
    @classmethod
    def validate_cookie(cls, v: str) -> str:
        """Ensure cookie is not empty."""
        if not v or not v.strip():
            raise ValueError("Cookie cannot be empty")
        return v.strip()


class NotifyConfig(BaseModel):
    """Notification service configuration.

    All fields are optional. Leave empty to disable a provider.
    """

    push_plus_token: str = ""
    sc_key: str = ""
    wecom_webhook: str = ""
    tg_bot_token: str = ""
    tg_user_id: str = ""
    tg_api_base: str = ""

    @property
    def has_any_provider(self) -> bool:
        """Check if at least one notification provider is configured."""
        return any(
            [
                self.push_plus_token,
                self.sc_key,
                self.wecom_webhook,
                self.tg_bot_token and self.tg_user_id,
            ]
        )


class SchedulerConfig(BaseModel):
    """Scheduler configuration."""

    hour: int | None = None
    minute: int | None = None
    timezone: str = "Asia/Shanghai"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses SMZDM_ prefix for all environment variables.

    Example:
        export SMZDM_COOKIE="your_cookie_here"
        export SMZDM_PUSH_PLUS_TOKEN="your_token"
    """

    # Single user mode
    cookie: str = "r_sort_type=score; __ckguid=I9XyO3YUubPIvb2KQopSlx7; device_id=2130706433175102503834316721deffa8ad4a410a3c30e15d22f059da; homepage_sug=b; smzdm_user_source=3114A7551FFED5B39ED9F8082BDC30B4; footer_floating_layer=0; ss_ab=ss48; ssmx_ab=mxss70; s_his=M1%20Max%20Macbook%20Pro%2Cmac; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%222372836556%22%2C%22first_id%22%3A%221876fe688b1def-077e61a815d6a1-26031851-3686400-1876fe688b2f96%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fsearch.smzdm.com%2F%3Fc%3Dhome%26s%3Dmac%26v%3Db%26mx_v%3Db%22%7D%2C%22%24device_id%22%3A%221876fe688b1def-077e61a815d6a1-26031851-3686400-1876fe688b2f96%22%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkxMTJmNzI5ZDgxNjVlLTAwZWQ1NWU1MmJjMTVhMS0yNjAwMWU1MS0zNjg2NDAwLTE5MTEyZjcyOWQ5ZjU4IiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMjM3MjgzNjU1NiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%222372836556%22%7D%7D; Hm_lvt_9b7ac3d38f30fe89ff0b8a0546904e58=1771431621,1771578480,1771697921; HMACCOUNT=9D50F3DBC7D2229D; ad_date=22; bannerCounter=%5B%7B%22number%22%3A0%2C%22surplus%22%3A1%7D%2C%7B%22number%22%3A0%2C%22surplus%22%3A1%7D%2C%7B%22number%22%3A0%2C%22surplus%22%3A1%7D%2C%7B%22number%22%3A0%2C%22surplus%22%3A1%7D%2C%7B%22number%22%3A0%2C%22surplus%22%3A1%7D%5D; ad_json_feed=%7B%7D; sess=BA-gKnSD36MFBag0QLH02e0H5SBcZ3sVRih922X5md3SFgpgGay3vxjOIXcEKR7TOlDvXtoG%2Fx71EV81RqI9fOobzjWNbAbuRdNUNIQvx3VXLq3nfRpjwIk4ok9; user=user%3A2372836556%7C2372836556; smzdm_id=2372836556; Hm_lpvt_9b7ac3d38f30fe89ff0b8a0546904e58=1771698123; w_tsfp=ltvuV0MF2utBvS0Q7qvvnUOvEzkhcDA4h0wpEaR0f5thQLErU5mC0IBztsjxOH3e5sxnvd7DsZoyJTLYCJI3dwNFFsqWINsShAnFkYFwj91GAEZgGcrdCARLcu4k7TlCdXhCNxS00jA8eIUd379yilkMsyN1zap3TO14fstJ019E6KDQmI5uDW3HlFWQRzaLbjcMcuqPr6g18L5a5Tjc5VL/JV9yBOxLgk3D134bCi0i4RC5fbxePB2ld8+mSqA="
    sk: str = ""

    # Multi-user mode (JSON array)
    users: str = ""  # JSON string: '[{"cookie": "...", "sk": "..."}]'

    # Notification settings
    push_plus_token: str = ""
    sc_key: str = ""
    wecom_webhook: str = ""
    tg_bot_token: str = "8073394698:AAElVxdbqRzHFKfzdOmcAfH9EgGE1jcceI0"
    tg_user_id: str = ""
    tg_api_base: str = ""

    # Scheduler settings
    sch_hour: int | None = None
    sch_minute: int | None = None
    timezone: str = "Asia/Shanghai"

    # Debug mode
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="SMZDM_",
        env_file=_find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_users(self) -> list[UserConfig]:
        """Get list of user configurations.

        Returns:
            List of UserConfig objects.

        Raises:
            ConfigurationError: If no users are configured.
        """
        users: list[UserConfig] = []

        # Try multi-user mode first
        if self.users:
            try:
                users_data = json.loads(self.users)
                if isinstance(users_data, list):
                    for i, user_data in enumerate(users_data):
                        if isinstance(user_data, dict) and user_data.get("cookie"):
                            users.append(
                                UserConfig(
                                    cookie=user_data["cookie"],
                                    sk=user_data.get("sk", ""),
                                    name=user_data.get("name", f"User{i + 1}"),
                                )
                            )
            except json.JSONDecodeError as e:
                raise ConfigurationError(
                    f"Invalid SMZDM_USERS JSON format: {e}",
                    details={"users": self.users[:100]},
                ) from e

        # Fall back to single user mode
        if not users and self.cookie:
            users.append(
                UserConfig(
                    cookie=self.cookie,
                    sk=self.sk,
                    name="default",
                )
            )

        if not users:
            raise ConfigurationError(
                "No users configured. Set SMZDM_COOKIE or SMZDM_USERS environment variable.",
            )

        return users

    def get_notify_config(self) -> NotifyConfig:
        """Get notification configuration."""
        return NotifyConfig(
            push_plus_token=self.push_plus_token,
            sc_key=self.sc_key,
            wecom_webhook=self.wecom_webhook,
            tg_bot_token=self.tg_bot_token,
            tg_user_id=self.tg_user_id,
            tg_api_base=self.tg_api_base,
        )

    def get_scheduler_config(self) -> SchedulerConfig:
        """Get scheduler configuration."""
        return SchedulerConfig(
            hour=self.sch_hour,
            minute=self.sch_minute,
            timezone=self.timezone,
        )


# Global settings instance (lazy loaded)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings instance loaded from environment.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment.

    Useful for testing or when environment changes.

    Returns:
        Fresh Settings instance.
    """
    global _settings
    _settings = Settings()
    return _settings


__all__ = [
    "NotifyConfig",
    "SchedulerConfig",
    "Settings",
    "UserConfig",
    "get_settings",
    "reload_settings",
]
