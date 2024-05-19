from dataclasses import dataclass


@dataclass
class BotConfig:
    channel_embeds_id: int
    channel_top_id: int
    forum_feedback_id: int
    guild_id: int
    guildmaster_id: int
    task_update_minute: int
    top_update_hours: int
    number_day_update_top: int
    placing_top_count: int
    required_reaction_count: int
    bot_token: str
    server_invite_code: str
    debug: bool
