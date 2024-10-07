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
# {'id': 6862969, 'pageURL': 'https://pixabay.com/photos/northern-lights-norway-nature-6862969/', 'type': 'photo', 'tags': 'northern lights, norway, nature', 'previewURL': 'https://cdn.pixabay.com/photo/2021/12/11/15/06/northern-lights-6862969_150.jpg', 'previewWidth': 150, 'previewHeight': 84, 'webformatURL': 'https://pixabay.com/get/g3676fb586828d463e835d962ff8c647fcf2f2edaa990da89d2cb5fbd04c484d8f17ad25c4f8816c73be2563dba04ce362a81044204f98303ea35461aea8b3287_640.jpg', 'webformatWidth': 640, 'webformatHeight': 360, 'largeImageURL': 'https://pixabay.com/get/g73f272a221c7954a6387d87f1b08749552171e259af961d8b8f4264eedb391684587fd9217c58551444e68f8571e865630275f8283c39600f43a07baf0a33a6d_1280.jpg', 'imageWidth': 6000, 'imageHeight': 3374, 'imageSize': 4349372, 'views': 665357, 'downloads': 622905, 'collections': 9441, 'likes': 339, 'comments': 45, 'user_id': 7444623, 'user': 'Photo-View', 'userImageURL': 'https://cdn.pixabay.com/user/2018/11/20/18-14-40-20_250x250.jpg'}