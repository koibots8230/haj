import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import cryptography.hazmat.primitives.asymmetric.rsa
import cryptography.hazmat.primitives.asymmetric.padding
import cryptography.hazmat.primitives.hashes
import cryptography.hazmat.primitives.serialization


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
        raise ValueError


class sheets:
    @classmethod
    def _get_token(cls, private_key):
        header = b'{"alg":"RS256","typ":"JWT","kit":"955f9071c99f211054ddfbfc3df1491ae88a2277"}'
        claim_set = bytes(
            '{'
            '"iss":"haj-0000@haj-8230.iam.gserviceaccount.com",'
            '"scope":"https://sheets.googleapis.com/auth/spreadsheets",'
            '"aud":"https://oauth2.googleapis.com/token",'
            f'"exp":{int(time.time() - 1)},'
            f'"int":{int(time.time() + 60)}'
            '}',
            "utf8"
        )
        print(cryptography.hazmat.primitives.serialization.load_pem_private_key(
            bytes(private_key, "utf8"),
            password=None
        ))
        signature = cryptography.hazmat.primitives.serialization.load_pem_private_key(
            bytes(private_key, "utf8"),
            password=None
        ).sign(
            base64.urlsafe_b64encode(header) + b'.' + base64.urlsafe_b64encode(claim_set),
            cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15(),
            cryptography.hazmat.primitives.hashes.SHA256()
        )
        jwt = (
            str(base64.urlsafe_b64encode(b'{"alg":"RS256","typ":"JWT"}')) + '.' +
            str(base64.urlsafe_b64encode(claim_set)) + '.' +
            str(base64.urlsafe_b64encode(signature))
        )
        response = json.loads(
            urllib.request.urlopen(
                urllib.request.Request(
                    url="https://oauth2.googleapis.com/token",
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    data=urllib.parse.urlencode(
                        {
                            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                            "assertion": jwt
                        }
                    ).encode(),
                    method="POST"
                )
            )
        )
        return response["access_token"]

    @classmethod
    def append(cls, private_key: str, spreadsheet_id: str, sheet_name: str, values: list[str]):
        if len(values) == 8:
            # try:
                return json.loads(
                    urllib.request.urlopen(
                        urllib.request.Request(
                            url=f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}"
                                f"!A1:I1:append?valueInputOption=USER_ENTERED",
                            data=urllib.parse.urlencode(
                                {
                                    "range": f"{sheet_name}!A1:I1",
                                    "majorDimension": "ROWS",
                                    "values": [
                                        values
                                    ]
                                }
                            ).encode(),
                            headers={
                                "authorization": "Bearer " + cls._get_token(private_key),
                                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                              "like Gecko) Chrome/120.0.0.0 Safari/537.36"
                            },
                            method="POST"
                        )
                    ).read()
                )
            # except urllib.error.HTTPError as HTTPError:
            #     print(str(HTTPError.read()))
            #     raise ValueError
        else:
            raise IndexError("Incorrect number of values provided")
