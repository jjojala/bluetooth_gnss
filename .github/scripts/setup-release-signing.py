import base64
import binascii
import os
from pathlib import Path


names = (
    "ANDROID_KEYSTORE_BASE64",
    "ANDROID_KEYSTORE_PASSWORD",
    "ANDROID_KEY_ALIAS",
    "ANDROID_KEY_PASSWORD",
)
missing = [name for name in names if not os.environ.get(name)]
if missing:
    raise SystemExit("Missing required Android signing secrets: " + ", ".join(missing))

try:
    keystore = base64.b64decode(
        "".join(os.environ["ANDROID_KEYSTORE_BASE64"].split()), validate=True
    )
except (ValueError, binascii.Error):
    raise SystemExit("ANDROID_KEYSTORE_BASE64 is not valid base64") from None
if not keystore:
    raise SystemExit("ANDROID_KEYSTORE_BASE64 contains an empty keystore")

os.umask(0o077)
keystore_path = Path(os.environ["RUNNER_TEMP"]) / "android-release.p12"
keystore_path.write_bytes(keystore)


def property_value(value):
    encoded = value.encode("utf-16-be")
    return "".join(
        f"\\u{int.from_bytes(encoded[i:i + 2], 'big'):04x}"
        for i in range(0, len(encoded), 2)
    )


properties = {
    "storeFile": str(keystore_path),
    "storeType": "PKCS12",
    "storePassword": os.environ["ANDROID_KEYSTORE_PASSWORD"],
    "keyAlias": os.environ["ANDROID_KEY_ALIAS"],
    "keyPassword": os.environ["ANDROID_KEY_PASSWORD"],
}
properties_path = Path(os.environ["GITHUB_WORKSPACE"]).parent / "key.properties"
properties_path.write_text(
    "".join(f"{key}={property_value(value)}\n" for key, value in properties.items()),
    encoding="ascii",
)
