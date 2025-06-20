import json
from nonebot import on_command
from nonebot.adapters import Message, Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import CommandArg
import httpx
from nonebot.plugin import PluginMetadata
from nonebot import get_plugin_config
from .config import Config
from nonebot import require
from nonebot import logger

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import (
    get_new_page
)

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-fursuitpic",
    description="接入 FurryHub X 追夜网络 的毛图API",
    usage="/来只毛[指定ID或不填写以随机获取]",
    type="application",
    homepage="https://github.com/mofan0423/nonebot-plugin-fursuitpic",
    config=Config,
    supported_adapters={"~onebot.v11"},
)
fursuitpic = on_command(
    "来只毛", 
    aliases={"fursuitpic"}, 
    priority=10, 
    block=True
)

config = get_plugin_config(Config)
name = ""
desc = ""
furryid = ""
img = ""

@fursuitpic.handle()
async def handle_function(args: Message = CommandArg()):
    location = args.extract_plain_text().strip()
    if not location:
        url = 'https://furryhub.api.open.zhuiyenet.com/furry?apikey=FURRYHUBAPIKEY'
        params = {
            'apikey': config.furryhub_apikey
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10000)
                response.raise_for_status()
                logger.success(response.text)
                data2 = response.json()
                furry_id = data2.get("furry_id")
                name = data2.get("name")
                introduce = data2.get("furry_intro")
                img_url = data2.get("avatar_name")
                await _html2pic(img_url, name, introduce, furry_id)
            except httpx.HTTPError as e:
                await fursuitpic.finish(f"网络请求失败: {str(e)}")
            except json.JSONDecodeError:
                await fursuitpic.finish("API响应无法解析为JSON，请检查服务器返回内容。")

async def _html2pic(img: int, name: int, desc: int, furryid: str):
    from pathlib import Path

    async with get_new_page(viewport={"width": 500, "height": 800}) as page:
        await page.goto(
            "file://" + (str(Path(__file__).parent / f"template.html?furryid={furryid}&desc={desc}&name={name}&img={img}")),
            wait_until="networkidle",
        )
        pic = await page.screenshot(full_page=True, path="./pic.png")

    await fursuitpic.finish(MessageSegment.image(pic))
