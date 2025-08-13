import asyncio
import logging
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import aiohttp
from lifechecks.namecheap import Namecheap, NamecheapLifecheckRequest
from parse_hosts.get_csv_hosts import GetUrlsFromCSV

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Config:
    link: str
    gateway_ip: str
    csv_path: Path


def load_env_config() -> Config:
    environment = os.getenv("NAMECHEAP_LIFECHECKS_ENVIRONMENT")
    gateway_ip = os.getenv("NAMECHEAP_LIFECHECKS_GATEWAY_IP")
    csv_path_str = os.getenv("NAMECHEAP_LIFECHECKS_CSV_PATH")

    if any(v is None for v in (environment, gateway_ip, csv_path_str)):
        raise ValueError("Set all required env vars first!!")

    if environment == "PROD":
        link = "https://api.namecheap.com/xml.response?"
    if environment == "DEV":
        link = "https://api.sandbox.namecheap.com/xml.response?"

    csv_path = Path(csv_path_str)  # type:ignore[arg-type]

    return Config(link=link, csv_path=csv_path, gateway_ip=gateway_ip)  # type:ignore[arg-type]


async def main() -> None:
    config = load_env_config()
    csv_parser = GetUrlsFromCSV(**asdict(config))
    urls = csv_parser.get_urls()
    pairs = {}
    request = NamecheapLifecheckRequest(hosts=urls)
    async with aiohttp.ClientSession() as session:
        life_checker = Namecheap(http_session=session)
        responce = await life_checker(data=request)
        pairs = responce.avaliable_banned_pair

    logger.debug("Parsed: %s", pairs)


if __name__ == "__main__":
    logger.info("The service has started")
    asyncio.run(main())
