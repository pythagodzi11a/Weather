import asyncio
import time
from pathlib import Path

import aiohttp
import jwt
import requests
import toml
from bs4 import BeautifulSoup
from geopy import Nominatim
from ncatbot.utils import get_log

_log = get_log()


class Config:
    def __init__(self):
        """
        读取配置文件，初始化配置参数。
        """
        # 读取配置文件
        # 配置文件路径为插件本体目录下的config.toml
        # 这部分可能会重写，因为我想要把他放到workspace目录下的config.toml中。但是config的载入需要提前，想使用懒加载等等，但是加载的模式很混乱，暂且按下不提。
        config_path = Path(__file__).parent / "config.toml"
        with open(config_path, "r", encoding="utf-8") as config_file:
            raw_info = toml.load(config_file)

        # 读取配置文件中的各个部分
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

    def should_process_group(self, group_id: int) -> bool:
        """
        处理聊天消息是否应该处理。

        :param group_id: 群号，用于进行黑/白名单的判断
        :type group_id: int
        :return: True 表示可以进行回复; False 表示不进行后续回复
        :rtype: bool
        """
        if self.group_enabled:
            if self.group_mode == "blacklist":
                return False if group_id in self.group_black_lists else True
            else:
                return True if group_id in self.group_white_lists else False
        else:
            return False

    def should_process_private(self, user_id: int) -> bool:
        """
        处理私聊消息是否应该处理。
        :param user_id: 用户的QQ号，用msg.user_id获取
        :type user_id: int
        :return: True 表示可以进行回复; False 表示不进行后续回复
        :rtype: bool
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
        """
        获取风云二号卫星的最新云图，以及更新状态。
        :rtype: tuple[str, bool]
        :rtype: tuple[str, bool]
        :return: 最新云图的URL, bool 是否更新
        """

        fy_2_url = "https://www.nmc.cn/publish/satellite/fy2.htm"
        web_meta_data = requests.get(fy_2_url).content

        soup = BeautifulSoup(web_meta_data, "lxml")

        image = str(soup.find("img", attrs={"id": "imgpath"}))
        time_element = soup.find("div", attrs={"class": "col-xs-12 time"})

        if time_element is None:
            return self.latest_url[1:-1] if self.latest_url else "", False

        latest_time = time_element.get_text()

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
        """
        生成JWT令牌，用于和风天气API的身份验证。
        :rtype: str
        :return: 生成的JWT令牌
        """

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
        """
        异步请求和风天气API获取指定位置的天气数据。
        :param location: 直接传入地名字符串，精度任意（理论上），后续会通过geopy库进行地理编码转换得到经纬度。
        :type location: str
        :return: 返回天气数据字典，如果请求失败或位置未找到则返回None。
        :rtype: dict | None
        """

        # 下面是进行地理位置解析的部分。解析成功后会得到Location对象location_transform。其中有经纬度信息。
        try:
            loop = asyncio.get_running_loop()
            location_transform = await loop.run_in_executor(
                None, self.geolocator.geocode, location
            )
        except TimeoutError as e:
            _log.error(f"Geocoding request timed out: {e}")
            return None

        if location_transform is None:  # 如果地理位置解析失败，则返回None
            return None
        else:
            # 下面的部分进行了和风天气的信息请求，使用了上面得到的经纬度信息。具体请求方法看和风api开发文档。
            latitude, longitude = ("%.2f" % location_transform.latitude), (  # type: ignore
                    "%.2f" % location_transform.longitude  # type: ignore
            )
            url = f"https://{config.api_host}/v7/weather/now?location={str(longitude)},{str(latitude)}"
            encoded_jwt = self.gen_jwt()  # 生成JWT令牌
            header = {
                "Authorization": f"Bearer {encoded_jwt}",
                "Content-Type": "application/json",
            }

            # 下面是进行异步HTTP请求的部分。使用aiohttp库进行GET请求。如果请求成功，则返回天气数据字典，否则返回None。
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=header) as response:
                    if response.status != 200:
                        return None
                    else:
                        data = await response.json()
                        return data["now"]
