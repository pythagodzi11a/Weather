import asyncio
import time
from pathlib import Path

import aiohttp
import jwt
import requests
import toml
from bs4 import BeautifulSoup
from geopy import Nominatim


class Config:
    def __init__(self):
        config_path = Path(__file__).parent / "config.toml"
        with open(config_path, "r", encoding="utf-8") as config_file:
            raw_info = toml.load(config_file)

        private_config = raw_info.get("private", {})
        group_config = raw_info.get("group", {})
        he_feng_api = raw_info.get("HeFengAPI", {})

        self.private_enabled = private_config["enable"]
        self.group_enabled = group_config["enable"]

        self.group_mode = group_config["mode"]
        self.private_mode = private_config["mode"]
        self.private_black_lists = private_config["blacklist"]
        self.group_black_lists = group_config["blacklist"]
        self.private_white_lists = private_config["whitelist"]
        self.group_white_lists = group_config["whitelist"]

        self.private_key = he_feng_api.get("HEFENG_PRIVATE_KEY")
        self.key_id = he_feng_api.get("HEFENG_KEY_ID")
        self.project_id = he_feng_api.get("HEFENG_PROJECT_ID")
        self.api_host = he_feng_api.get("HEFENG_API_HOST")

    def should_process_group(self, group_id: str) -> bool:
        """

        :param group_id:
        :return:
        """
        if self.group_enabled:
            if self.group_mode == "blacklist":
                return False if group_id in self.group_black_lists else True
            else:
                return True if group_id in self.group_white_lists else False
        else:
            return False

    def should_process_private(self, user_id: str) -> bool:
        """

        :param user_id:
        :return:
        """
        if self.private_enabled:
            if self.private_mode == "blacklist":
                return False if user_id in self.private_black_lists else True
            else:
                return True if user_id in self.private_white_lists else False
        else:
            return False


config = Config()


class WeatherGet:
    def __init__(self):
        self.past_time = 0
        self.latest_url = ""
        self.geolocator = Nominatim(user_agent="geoapp")

    def get_china_satellite_weather_image(self) -> tuple[str, bool]:

        fy_2_url = "https://www.nmc.cn/publish/satellite/fy2.htm"
        web_meta_data = requests.get(fy_2_url).content

        soup = BeautifulSoup(web_meta_data, "lxml")

        image = str(soup.find("img", attrs={"id": "imgpath"}))
        latest_time = soup.find("div", attrs={"class": "col-xs-12 time"}).get_text()

        if latest_time != self.past_time:

            divided_parts = image.split()
            for part in divided_parts:

                if part.startswith("src="):
                    self.latest_url = part.split("=")[1]

                    # image = requests.get(self.latest_url[1:-1]).content
                    #
                    # with open(f"test.jpg", "wb") as f:
                    #     f.write(image)

                    self.past_time = latest_time
            status = True
        else:
            status = False

        return self.latest_url[1:-1], status

    @staticmethod
    def gen_jwt() -> str:

        private_key = config.private_key
        project_id = config.project_id
        key_id = config.key_id

        payload = {
            "iat": int(time.time()) - 30,
            "exp": int(time.time()) + 900,
            "sub": project_id,
        }
        headers = {"kid": key_id}

        # Generate JWT
        encoded_jwt = jwt.encode(
            payload, private_key, algorithm="EdDSA", headers=headers
        )

        return encoded_jwt

    async def request_content_sync(self, location: str) -> dict | None:
        # location_transform = self.geolocator.geocode(location)
        loop = asyncio.get_running_loop()
        location_transform = await loop.run_in_executor(
            None, self.geolocator.geocode, location
        )

        if location_transform is None:
            return None
        else:
            latitude, longitude = ("%.2f" % location_transform.latitude), ("%.2f" % location_transform.longitude)
            url = f"https://{config.api_host}/v7/weather/now?location={str(longitude)},{str(latitude)}"
            encoded_jwt = self.gen_jwt()
            header = {
                "Authorization": f"Bearer {encoded_jwt}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=header) as response:
                    if response.status != 200:
                        return None
                    else:
                        data = await response.json()
                        return data["now"]
