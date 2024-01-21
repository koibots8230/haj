import json
import urllib.request
import urllib.error


def tba(path: str, api_key: str) -> dict:
    try:
        return json.loads(urllib.request.urlopen(urllib.request.Request(
            f"https://www.thebluealliance.com/api/v3{path}",
            headers={
                "x-tba-auth-key": api_key,
                "user-agent": "FRC/8230"
            })).read())
    except urllib.error.HTTPError:
        raise ValueError
