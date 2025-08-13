import asyncio
import aiohttp
from dataclasses import dataclass
from lifechecks.lifecheck import Lifecheck


@dataclass(slots=True, frozen=True)
class NamecheapLifecheckRequest:
    hosts: list[str]


@dataclass(slots=True, frozen=True)
class NamecheapLifecheckResponce:
    avaliable_banned_pair: dict[str, list[str]]


class Namecheap(Lifecheck[NamecheapLifecheckRequest, NamecheapLifecheckResponce]):
    def __init__(self, http_session: aiohttp.ClientSession) -> None:
        self.http_session = http_session

    async def _fetch(self, url: str) -> tuple[str, int, bytes]:
        async with self.http_session.get(url) as resp:
            body = await resp.read()
            return url, resp.status, body

    def _result_filter(
        self, results: list[tuple[str, int, bytes]]
    ) -> dict[str, list[str]]:
        available = []
        banned = []

        for url, status, body in results:
            text = body.decode(errors="ignore")
            if "Response error: ApiUser has been blocked by administrator" in text:
                banned.append(url)
            elif status == 200:
                available.append(url)

        result = {"available": available}
        if banned:
            result["banned"] = banned
        return result

    async def __call__(
        self,
        data: NamecheapLifecheckRequest,
    ) -> NamecheapLifecheckResponce:
        tasks = [self._fetch(url) for url in data.hosts]
        results = await asyncio.gather(*tasks)
        avaliable_banned_pairs = self._result_filter(results=results)
        return NamecheapLifecheckResponce(avaliable_banned_pair=avaliable_banned_pairs)
