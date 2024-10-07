from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
import tomllib

# Get the API key from config file

APIKEYS_PATH = Path(__file__).parent / "apikeys.toml"
with open(APIKEYS_PATH, "rb") as f:
    apikeys = tomllib.load(f)

response = requests.get("https://pixabay.com/api/", params={"key": apikeys["pixabay"], "q": "galaxy"})
response.raise_for_status()
search_results = response.json()

img_url: str = search_results["hits"][0]["webformatURL"]
print(img_url)

img_data = requests.get(img_url).content

with open(Path.home() / "Downloads" / unquote(Path(urlparse(img_url).path).name), mode='wb') as f:
  f.write(img_data)

print(search_results)