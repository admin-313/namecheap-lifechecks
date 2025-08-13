import asyncio
from dataclasses import dataclass
import os


@dataclass(slots=True, frozen=True)
class EnvConfig:
    environment: str


@dataclass(slots=True)
class Config:
    link: str


def load_env_config() -> EnvConfig:
    environment = os.getenv("NAMECHEAP_LIFECHECKS_ENVIRONMENT")
    if environment is None:
        raise ValueError("Set NAMECHEAP_LIFECHECKS_ENVIRONMENT")

    return EnvConfig(environment=environment)


def load_config() -> Config:
    environment_config = load_env_config()
    if environment_config == "PROD":
        link = "https://api.namecheap.com/xml.response"
    if environment_config == "DEV":
        link = "https://api.sandbox.namecheap.com/xml.response"

    return Config(link=link)


async def main() -> None:
    pass


if __name__ == "__main__":
    asyncio.run(main())
