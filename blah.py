import logging

import requests

try:
    print(
        "Public IP address - "
        + requests.get("https://checkip.amazonaws.com").text.strip()
    )
except:
    print("Unable to get public IP address")
print("Connecting to SFTP server")
