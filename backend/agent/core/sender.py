import json
from urllib.request import Request, urlopen

from agent.core.collector import collect_system_info


def send_system_info(url: str):
    data = collect_system_info()

    request = Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))