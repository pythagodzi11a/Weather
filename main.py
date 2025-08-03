import datetime
import textwrap

from ncatbot.core import (MessageChain, Image, Text, GroupMessage, PrivateMessage, Face, Reply)
from ncatbot.plugin import BasePlugin, CompatibleEnrollment

from .utils import WeatherGet

bot = CompatibleEnrollment  # 兼容回调函数注册器
Utils = WeatherGet()


class Weather(BasePlugin):
    name = "Weather"  # 插件名称
    version = "0.0.2"  # 插件版本
    author = "pythagodzilla"  # 插件作者
    info = "今天天气怎么样？"  # 插件描述
    dependencies = {}  # 插件依赖，格式: {"插件名": "版本要求"}

    @bot.private_event()
    async def on_get_china_statellite_weather(self, msg: PrivateMessage):
        if msg.message[0]["type"] == "text":
            if msg.message[0]["data"]["text"] == "今日云图":
                image_url, status = Utils.get_china_statellite_weather_image()

                message_content = MessageChain(
                    [
                        Text(f"云图{"已" if status else "未"}更新\n"),
                        Text("最新云图："),
                        Image(image_url),
                        [
                            Face(123),
                            Image(image_url),
                            Reply(msg.message_id),
                        ]
                    ]
                )

                await self.api.post_private_msg(user_id=msg.user_id, rtf=message_content)

    @bot.group_event()
    async def on_get_china_statellite_weather(self, msg: GroupMessage):
        if msg.message[0]["type"] == "text":
            if msg.message[0]["data"]["text"] == "今日云图":
                image_url, status = Utils.get_china_statellite_weather_image()

                message_content = MessageChain(
                    [
                        Text(f"云图{"已" if status else "未"}更新"),
                        Text("最新云图："),
                        Image(image_url)
                    ]
                )

                await self.api.post_group_msg(group_id=msg.group_id, rtf=message_content)

    @bot.private_event()
    async def on_get_weather_private_event(self, msg: PrivateMessage):
        if msg.message[0]["type"] == "text":
            if str(msg.raw_message).endswith("今日天气"):
                location = str(msg.raw_message)[0:-4]
                weather_data = await Utils.request_content_sync(location=location)

                if weather_data is None:
                    message_local = MessageChain(
                        Text("哈？没请求到数据！")
                    )
                    await self.api.post_private_msg(user_id=msg.user_id, rtf=message_local)

                else:
                    # data = await Utils.request_content_sync("北京天安门")
                    message_local = MessageChain(
                        # Text(f"数据更新于{data["obsTime"]}\n"),
                        # Text(f"温度：{data["temp"]}，体感温度为：{data["feelsLike"]}\n"),
                        # Text(f"当前天气：{data["text"]}，{data["windDir"]}，风力：{data["windScale"]}\n"),
                        # Text(f"相对湿度：{data["humidity"]}\n"),
                        Text(textwrap.dedent(f"""
                            🌤️嗨嗨～你的小天气播报员上线啦！

                            下面是{location}的天气情况！
                            现在的时间是：{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
                            数据更新时间是：{weather_data['obsTime']}
                            天气是：{weather_data['text']}
                            气温是：{weather_data['temp']}°C，体感温度是：{weather_data['feelsLike']}°C
                            风是来自{weather_data['windDir']}，风速 {weather_data['windSpeed']} 公里/小时，风力等级 {weather_data['windScale']}
                            空气湿度是 {weather_data['humidity']}%，气压是 {weather_data['pressure']} hPa
                            能见度大约是 {weather_data['vis']} 公里哟～
                            过去一小时降水量是 {weather_data['precip']} mm

                            天气服务由和风天气驱动！
                            """))
                    )

                    await self.api.post_private_msg(user_id=msg.user_id, rtf=message_local)

    @bot.group_event()
    async def on_get_weather_group_event(self, msg: GroupMessage):
        if msg.message[0]["type"] == "text":
            if str(msg.raw_message).endswith("今日天气"):
                location = str(msg.raw_message)[0:-4]
                weather_data = await Utils.request_content_sync(location=location)

                if weather_data is None:
                    message_local = MessageChain(
                        Text("哈？没请求到数据！")
                    )
                    await self.api.post_group_msg(group_id=msg.group_id, rtf=message_local)

                else:
                    message_local = MessageChain(
                        # Text(f"数据更新于{data["obsTime"]}\n"),
                        # Text(f"温度：{data["temp"]}，体感温度为：{data["feelsLike"]}\n"),
                        # Text(f"当前天气：{data["text"]}，{data["windDir"]}，风力：{data["windScale"]}\n"),
                        # Text(f"相对湿度：{data["humidity"]}\n"),
                        Text(textwrap.dedent(f"""
                            🌤️嗨嗨～你的小天气播报员上线啦！

                            下面是{location}的天气情况！
                            现在的时间是：{datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
                            数据更新时间是：{weather_data['obsTime']}
                            天气是：{weather_data['text']}
                            气温是：{weather_data['temp']}°C，体感温度是：{weather_data['feelsLike']}°C
                            风是来自{weather_data['windDir']}，风速 {weather_data['windSpeed']} 公里/小时，风力等级 {weather_data['windScale']}
                            空气湿度是 {weather_data['humidity']}%，气压是 {weather_data['pressure']} hPa
                            能见度大约是 {weather_data['vis']} 公里哟～
                            过去一小时降水量是 {weather_data['precip']} mm

                            天气服务由和风天气驱动！
                            """))
                    )

                    await self.api.post_group_msg(group_id=msg.group_id, rtf=message_local)
