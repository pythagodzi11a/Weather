# Weather 插件

## 简介

一个基于 ncatbot 的查询天气情况的插件！

天气服务由[和风天气](https://www.qweather.com)驱动

**重要提示**：目前，由于我使用了 geopy 来解析经纬度信息。所以需要访问 nominatim.openstreetmap.org。很可惜，这个服务可能由于某些原因，在国内无法访问。可能需要开启代理。

## 功能

- 想要知道现在的天气？使用 **（地点）今日天气** 来获取吧
- 想要知道最新的云图？使用 **今日云图** 来获取吧

## 使用方法

1. 在群聊或者私聊中发送 **（地点）今日天气** ，例如“ **北京今日天气** ”，“ **北京朝阳今日天气**”等来了解现在的天气。
2. 在群聊或者私聊中发送 **今日云图** 来获取当前最新的风云二号的卫星云图。

## 配置项

- 请前往[和风天气开发配置](https://dev.qweather.com/docs/configuration/)。按照里面的列表 **新建并获取** 你的 **项目 ID** ，
  **API Host**等数据。
- 将这些信息填写在本插件目录下面的 **.env.bak**文件中。并将其复制一份并命名为 **.env**。插件将会从这个 `.env`
  文件来读取你的信息用于请求和风天气的 api。

---

- 其中[项目和凭据](https://dev.qweather.com/docs/configuration/project-and-key/)，中有介绍本插件所需要使用的 key_id,
  project_id 等。
- 本项目使用其中的 **JWT 凭据** 所以请阅读上面这个导航。上传你制作的公钥。并将私钥填写在本插件的`.env` 文件里。
- [API HOST](https://dev.qweather.com/docs/configuration/api-host/)可以从这个链接进入和风天气文档。并查询你的 API HOST，并填入
  `.env`中。

## 其他说明

- 对于 python 我并没有很熟悉。所以可能有些地方写的不好，不够专业，请见谅。
- 目前打算开发群聊私聊的黑白名单等等。所以现在如果使用了插件。那么所有机器人加入的群都会启用插件
  _（也许？我也不知道有没有控制插件的插件。我刚切换到 ncatbot 框架不久）_ 。
- 开发本插件的缘由是因为想做云图的延时视频。所以顺道做的这个插件。等到基本功能稳定会逐渐开放例如：保存云图到本地，生成云图动图等功能。
- 由于本插件开发时间比较短，属于是一时兴起做的。所以很多地方处理的比较粗陋。比如如果你获取今日天气时没有加上地点。会报错。这个还没处理，可能在未来的一到两个版本修复。
- 如果你有任何建议或者想法。欢迎在[github 仓库](https://github.com/pythagodzi11a/Weather)中反映。也可以通过邮件 **planetarydefensecouncil@outlook.com** 来联系我。

## 依赖

- NcatBot
- geopy
- aiohttp
- dotenv
- beautifulsoup4
- pyjwt

## 作者

pythagodzilla

## 许可证

MIT
