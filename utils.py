import os
import time

import aiohttp
import jwt
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from geopy import Nominatim
from pathlib import Path


class WeatherGet:
    def __init__(self):
        self.past_time = 0
        self.latest_url = ""
        self.geolocator = Nominatim(user_agent="geoapp")

    def get_china_statellite_weather_image(self) -> tuple[str, bool]:

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

        env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path)
        # Open PEM
        private_key = os.getenv("HEFENG_PRIVATE_KEY")
        key_id = os.getenv("HEFENG_KEY_ID")
        project_id = os.getenv("HEFENG_PROJECT_ID")
        #
        #         private_key = '''-----BEGIN PRIVATE KEY-----
        # MC4CAQAwBQYDK2VwBCIEIEqamr00vx8F4j+fX9O6MGBDaNS46OSJJVZNY2tR+R7B
        # -----END PRIVATE KEY-----'''
        #         key_id = "CHB3UNRPVG"
        #         project_id = "3BE3DAPYM2"

        payload = {
            'iat': int(time.time()) - 30,
            'exp': int(time.time()) + 900,
            'sub': project_id
        }
        headers = {
            'kid': key_id
        }

        # Generate JWT
        encoded_jwt = jwt.encode(payload, private_key, algorithm='EdDSA', headers=headers)

        return encoded_jwt

    # def get_weather_information(self, loacation: str) -> str | None:
    #     encoded_jwt = self.gen_jwt()
    #     url = f"https://mq4nmt56cn.re.qweatherapi.com/v7/weather/now?location={loacation}"
    #     headers_local = {
    #         'Authorization': f"Bearer {encoded_jwt}",
    #         "Content-Type": "application/json"
    #     }
    #
    #     response = requests.get(url, headers=headers_local)
    #
    #     if response.status_code != 200:
    #         return None
    #     else:
    #         print(response.content)
    #         return response.content

    async def request_content_sync(self, location: str) -> dict | None:
        location_transform = self.geolocator.geocode(location)
        latitude, longitude = ('%.2f' % location_transform.latitude), ('%.2f' % location_transform.longitude)
        url = f"https://mq4nmt56cn.re.qweatherapi.com/v7/weather/now?location={str(longitude)},{str(latitude)}"
        encoded_jwt = self.gen_jwt()
        header = {
            "Authorization": f"Bearer {encoded_jwt}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=header) as response:
                if response.status != 200:
                    return None
                else:
                    data = await response.json()
                    return data["now"]
