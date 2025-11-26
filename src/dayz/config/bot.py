from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    pvp_channel_embeds_id: int = 1163130507098333184
    pve_channel_embeds_id: int = 1275532171213541516
    pvp_channel_top_id: int = 1156704671939956796
    pve_channel_top_id: int = 1275532060202635315
    pvp_forum_feedback_id: int = 1237137663547543563
    pve_forum_feedback_id: int = 1275552618353004575
    guild_id: int = 416292549884641282
    guildmaster_id: int = 289031678490312715
    task_update_minute: int = 10
    top_update_hours: int = 24
    number_day_update_top: int = 1
    placing_top_count: int = 5
    pvp_required_reaction_count: int = 40
    pve_required_reaction_count: int = 20
    bot_token: str
    server_invite_code: str = "QEMtdw8RJX"
    debug: bool = False
