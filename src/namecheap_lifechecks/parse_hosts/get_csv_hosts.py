import csv
from io import StringIO
from pathlib import Path
from urllib.parse import quote_plus


class GetUrlsFromCSV:
    def __init__(self, csv_path: Path, link: str, gateway_ip: str) -> None:
        self._csv_path = csv_path
        self._link = link
        self._gateway_ip = gateway_ip

    def get_urls(self) -> list[str]:
        csv_content = self._read_namecheap_csv()
        return self._build_namecheap_urls(csv_content=csv_content)

    def _read_namecheap_csv(self) -> str:
        csv_content = self._csv_path.read_text(encoding="utf-8")
        return csv_content

    def _build_namecheap_urls(self, csv_content: str) -> list[str]:
        """
        Parse CSV content and build Namecheap 'getBalances' URLs for each row.

        Expected headers: ApiUser, ApiKey, UserName
        """
        required = {"ApiUser", "ApiKey", "UserName"}
        urls: list[str] = []

        reader = csv.DictReader(StringIO(csv_content))
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing required column(s): {', '.join(sorted(missing))}"
            )

        for row in reader:
            api_user = quote_plus(row["ApiUser"])
            api_key = quote_plus(row["ApiKey"])
            user_name = quote_plus(row["UserName"])

            url = (
                f"{self._link}"
                f"ApiUser={api_user}"
                f"&ApiKey={api_key}"
                f"&Command=namecheap.users.getBalances"
                f"&ClientIp={self._gateway_ip}"
                f"&UserName={user_name}"
            )
            urls.append(url)

        return urls
