import asyncio
from dataclasses import dataclass, asdict
import os
from pathlib import Path

from parse_hosts.get_csv_hosts import GetUrlsFromCSV


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
    
if __name__ == "__main__":
    asyncio.run(main())
