import json
import urllib.error
import urllib.parse
import urllib.request


def tba(path: str, api_key: str) -> dict:
    try:
        return json.loads(
            urllib.request.urlopen(
                urllib.request.Request(
                    url=f"https://www.thebluealliance.com/api/v3{path}",
                    headers={
                        "x-tba-auth-key": api_key,
                        "user-agent": "FRC/8230"
                    }
                )
            ).read()
        )
    except urllib.error.HTTPError:
        pass
    raise ValueError
