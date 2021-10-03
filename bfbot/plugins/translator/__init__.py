import hashlib
import random
import string
import httpx

import nonebot
from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.typing import T_State

translate = on_command('translate')


def random_string_generator(length: int):
    return ''.join(random.choices(string.ascii_letters, k=length))

@translate.handle()
async def translate_handler(bot: Bot, event: Event, state: T_State):
    sender_id = event.get_user_id()
    args = str(event.get_message()).strip().split()
    rand_str = random_string_generator(30)
    hash_digest = hashlib.md5(
        str(nonebot.get_driver().config.BD_TRANSAPP_ID).encode('utf-8') +
        args[2].encode('utf-8') +
        rand_str.encode('utf-8') +
        str(nonebot.get_driver().config.BD_TRANSAPP_SECRET).encode('utf-8')
    ).hexdigest()
    async with httpx.AsyncClient() as client:
        try:
            await translate.send("稍等下，正在获取您请求的信息……")
            resp = await client.get(
                "https://fanyi-api.baidu.com/api/trans/vip/translate?q=" + args[2] +
                "&from=" + args[0] + "&to=" + args[1] + "&appid=" + str(nonebot.get_driver().config.BD_TRANSAPP_ID) +
                "&salt=" + rand_str + "&sign=" + hash_digest, timeout=10.0)
        except httpx.ReadTimeout:
            await translate.finish("太对不起了，请求超时了（悲")
        result = resp.json()['trans_result'][0]['dst']
        await translate.finish(
            Message(
                (MessageSegment.at(sender_id) if event.get_session_id().startswith('group') else '') +
                "[MunitionBot] 翻译结果：\n" + result
            )
        )