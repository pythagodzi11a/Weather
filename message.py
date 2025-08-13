import textwrap
from datetime import datetime

from ncatbot.core import MessageChain, Text, Image


class Message:

    @staticmethod
    def weather_today_message(location: str, weather_data: dict) -> MessageChain:
        """

        :param location: 地区名称，用于在信息中显示具体查询的地点。
        :type location: str
        :param weather_data: 由request_content_sync方法获取的天气数据字典。
        :type weather_data: dict
        :rtype: MessageChain
        :return: 🌤️嗨嗨～你的小天气播报员上线啦！

                下面是xxx的天气情况！
                现在的时间是：xxxx/xx/xx xx:xx:xx
                数据更新时间是：xxxxxxxx
                天气是：xx
                气温是：xx°C，体感温度是：xx°C
                风是来自xx，风速 xx 公里/小时，风力等级 x
                空气湿度是 xx%，气压是 xxx hPa
                能见度大约是 xx 公里哟～
                过去一小时降水量是 xx mm

                天气服务由和风天气驱动！
        """
        message = MessageChain(
            Text(
                textwrap.dedent(
                    f"""
                🌤️嗨嗨～你的小天气播报员上线啦！
    
                下面是{location}的天气情况！
                现在的时间是：{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}
                数据更新时间是：{weather_data['obsTime']}
                天气是：{weather_data['text']}
                气温是：{weather_data['temp']}°C，体感温度是：{weather_data['feelsLike']}°C
                风是来自{weather_data['windDir']}，风速 {weather_data['windSpeed']} 公里/小时，风力等级 {weather_data['windScale']}
                空气湿度是 {weather_data['humidity']}%，气压是 {weather_data['pressure']} hPa
                能见度大约是 {weather_data['vis']} 公里哟～
                过去一小时降水量是 {weather_data['precip']} mm
    
                天气服务由和风天气驱动！
                """
                )
            )
        )

        return message

    @staticmethod
    def weather_today_message_location_not_found(location: str) -> MessageChain:
        """
        当用户查询的地点不存在时，返回的消息。
        :param location: 输入的地点名称。用于返回查询不到的地点。
        :type location: str
        :rtype: MessageChain
        :return: 哈？你在找哪里啊？你要找的{location}找不到啊……
                这是地球上的地方嘛？
        """
        message = MessageChain(
            Text(
                textwrap.dedent(
                    f"""
                哈？你在找哪里啊？你要找的{location}找不到啊……
                这是地球上的地方嘛？
                """
                )
            )
        )

        return message

    @staticmethod
    def weather_today_message_no_location() -> MessageChain:
        """
        当用户没有提供地点信息时，返回的消息。
        :rtype: MessageChain
        :return: 哈？你要查哪里的天气啊？你没说啊！
                你可以直接输入“xxx今日天气”来查询你想知道的地方的天气哦～
        """
        message = MessageChain(
            Text(
                textwrap.dedent(
                    """
                哈？你要查哪里的天气啊？你没说啊！
                你可以直接输入“xxx今日天气”来查询你想知道的地方的天气哦～
                """
                )
            )
        )

        return message

    @staticmethod
    def satellite_image_message(image_url: str, status: bool) -> MessageChain:
        """
        返回风云二号卫星云图的信息。其中包括图片和更新状态。图片的显示使用Image类。并且传入的是图片的url，而不是图片的二进制数据。
        :param image_url: 云图图片的URL地址。
        :type image_url: str
        :param status: 云图是否更新的状态。
        :type status: bool
        :rtype: MessageChain
        :return: 云图以/未更新，最新云图：{图片}
        """
        message = MessageChain(
            [
                Text(f"云图{'已' if status else '未'}更新"),
                Text("最新云图："),
                Image(image_url)
            ]
        )

        return message
