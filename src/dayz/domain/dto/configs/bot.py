from dataclasses import dataclass


@dataclass
class BotConfig:
    pvp_channel_embeds_id: int
    pve_channel_embeds_id: int
    pvp_channel_top_id: int
    pve_channel_top_id: int
    pvp_forum_feedback_id: int
    pve_forum_feedback_id: int
    guild_id: int
    guildmaster_id: int
    task_update_minute: int
    top_update_hours: int
    number_day_update_top: int
    placing_top_count: int
    pvp_required_reaction_count: int
    pve_required_reaction_count: int
    bot_token: str
    server_invite_code: str
    debug: bool
