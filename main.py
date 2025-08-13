from ncatbot.core import GroupMessage, PrivateMessage
from ncatbot.plugin import BasePlugin, CompatibleEnrollment

from .message import Message
from .utils import WeatherGet, Config

config = Config()
bot = CompatibleEnrollment  # 兼容回调函数注册器
Utils = WeatherGet()
_message = Message


class Weather(BasePlugin):
    name = "Weather"  # 插件名称
    version = "0.1.1"  # 插件版本
    author = "pythagodzilla"  # 插件作者
    info = "今天天气怎么样？"  # 插件描述

    dependencies = {}  # 插件依赖，格式: {"插件名": "版本要求"}

    @bot.private_event()
    async def on_get_china_satellite_weather_private_event(self, msg: PrivateMessage):
        if config.should_process_private(user_id=msg.user_id):
            if msg.message[0]["type"] == "text":
                if msg.message[0]["data"]["text"] == "今日云图":
                    image_url, status = Utils.get_china_satellite_weather_image()

                    await self.api.post_private_msg(
                        user_id=msg.user_id,
                        rtf=_message.satellite_image_message(
                            image_url=image_url, status=status
                        )
                    )

    @bot.group_event()
    async def on_get_china_satellite_weather_group_event(self, msg: GroupMessage):
        if config.should_process_group(group_id=msg.group_id):
            if msg.message[0]["type"] == "text":
                if msg.message[0]["data"]["text"] == "今日云图":
                    image_url, status = Utils.get_china_satellite_weather_image()

                    await self.api.post_group_msg(
                        group_id=msg.group_id,
                        rtf=_message.satellite_image_message(
                            image_url=image_url, status=status
                        )
                    )

    @bot.private_event()
    async def on_get_weather_private_event(self, msg: PrivateMessage):
        if config.should_process_private(user_id=msg.user_id):
            if msg.message[0]["type"] == "text":
                if str(msg.raw_message).endswith("今日天气"):
                    location = str(msg.raw_message)[0:-4]

                    if not location:
                        await self.api.post_private_msg(
                            user_id=msg.user_id, rtf=_message.weather_today_message_no_location()
                        )
                    else:
                        weather_data = await Utils.request_content_sync(
                            location=location
                        )

                        if weather_data is None:

                            await self.api.post_private_msg(
                                user_id=msg.user_id,
                                rtf=_message.weather_today_message_location_not_found(location=location)
                            )

                        else:

                            await self.api.post_private_msg(
                                user_id=msg.user_id,
                                rtf=_message.weather_today_message(location=location, weather_data=weather_data)
                            )

    @bot.group_event()
    async def on_get_weather_group_event(self, msg: GroupMessage):
        if config.should_process_group(group_id=msg.group_id):
            if msg.message[0]["type"] == "text":
                if str(msg.raw_message).endswith("今日天气"):
                    location = str(msg.raw_message)[0:-4]

                    if not location:
                        await self.api.post_group_msg(
                            group_id=msg.group_id, rtf=_message.weather_today_message_no_location()
                        )
                    else:
                        weather_data = await Utils.request_content_sync(
                            location=location
                        )

                        if weather_data is None:

                            await self.api.post_group_msg(
                                group_id=msg.group_id,
                                rtf=_message.weather_today_message_location_not_found(location=location)

                            )

                        else:

                            await self.api.post_group_msg(
                                group_id=msg.group_id,
                                rtf=_message.weather_today_message(location=location, weather_data=weather_data)
                            )
