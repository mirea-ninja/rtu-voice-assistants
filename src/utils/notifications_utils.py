import logging

from aiohttp import ClientSession
from pydantic import Json

from ..core.config import DISCORD_WEBHOOK_URL

logger = logging.getLogger(__name__)


class DiscordLoggerUtils:

    _color = 15548997
    _title = "Incomprehensible intent"
    _author = "MIREA NINJA | DISCORD NOTIFICATIONS"
    _author_icon = "https://cdn.discordapp.com/attachments/903611347370127360/946040378010779678/logo.png"
    _author_url = "https://mirea.ninja/"
    _footer = "© MIREA NINJA 2022"
    _footer_icon = "https://cdn.discordapp.com/attachments/903611347370127360/946040378010779678/logo.png"

    @staticmethod
    async def send_notification(session: ClientSession, intent: str) -> None:
        headers = {
            'accept': '*/*',
            'content-type': 'application/json'
        }

        notification_data = {
            "embeds": [
                {
                    "author": {
                        "name": f"{DiscordLoggerUtils._author}",
                        "icon_url": f"{DiscordLoggerUtils._author_icon}",
                        "url": f"{DiscordLoggerUtils._author_url}"
                    },
                    "color": DiscordLoggerUtils._color,
                    "title": f"{DiscordLoggerUtils._title}",
                    "footer": {
                        "text": f"{DiscordLoggerUtils._footer}",
                        "icon_url": f"{DiscordLoggerUtils._footer_icon}"
                    },
                    "fields": [
                        {
                            "name": "original_utterance",
                            "value": f"{intent}",
                            "inline": False
                        }
                    ]   
                }
            ]
        }
        async with session.post(url=f'{DISCORD_WEBHOOK_URL}', data=notification_data, headers=headers) as request:
            logger.info(await request.read())
            # response = await request.json()
            # if request.status == 400:
            #     logger.error(
            #         f"400 bad request(Discord notifications). Result - {response}")
