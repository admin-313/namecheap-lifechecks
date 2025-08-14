import logging
import aiohttp


logger = logging.getLogger(__name__)


class NotifyTelegram:
    def __init__(
        self,
        http_session: aiohttp.ClientSession,
        bot_token: str,
        chat_id: str,
        message_thread_id: str,
    ) -> None:
        self._http_session = http_session
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._message_thread_id = message_thread_id

    def _parse_api_user_from_link(self, link: str) -> str:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        api_user = params.get("ApiUser", [None])[0]
        if api_user is not None:
            return api_user

        logger.info("Could not parse ApiUser from the %s", link)
        raise ValueError("The ApiUser wasn't parsed")

    async def _notify(self, banned_hosts: list[str]) -> None:
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        message = "The following hosts have been banned:\n".join(
            f"{host}\n" for host in banned_hosts
        )
        data = {
            "chat_id": self._chat_id,
            "text": message,
            "message_thread_id": self._message_thread_id,
        }
        await self._http_session.post(url=url, data=data)

    async def notify_if_any_banned(self, pairs: dict[str, list[str]]) -> None:
        banned = pairs.get("banned") or []
        if not banned:
            logger.debug("No accounts were banned")
            return

        logger.info("Banned accounts: %s", str(banned))
        await self._notify(banned_hosts=banned)
