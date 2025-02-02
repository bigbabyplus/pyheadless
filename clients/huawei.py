import asyncio
import os
from datetime import datetime, timezone, timedelta

from libs.base_huawei import BaseHuaWei


class HuaWei(BaseHuaWei):

    def __init__(self):
        super().__init__()

    async def handler(self, **kwargs):
        self.cancel = False

        self.logger.info(f'{self.username} start login.')
        if kwargs.get('iam'):
            await self.iam_login(self.username, self.password, kwargs.get('parent'))
        else:
            await self.login(self.username, self.password)

        url = self.page.url
        if 'login' in url:
            self.logger.error(f'{self.username} login fail.')
            return None

        await self.sign_task()

        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        h = int(utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%H'))
        self.logger.info(f'now hours: {h}')

        if h <= 12:
            await self.check_project()
            await self.start()

        if h > 12:
            await self.delete_project()
            await self.delete_function()
            await self.delete_api()
            await self.delete_api_group()

        # await self.init_account()

        return await self.get_credit()

    async def login(self, username, password):
        await self.page.waitForSelector('input[name="userAccount"]')
        await asyncio.sleep(1)
        await self.page.type('input[name="userAccount"]', username, {'delay': 10})
        await asyncio.sleep(0.5)
        await self.page.type('.hwid-input-pwd', password, {'delay': 10})
        await asyncio.sleep(2)
        items = await self.page.querySelectorAll('.hwid-list-row-active')

        if items and len(items):
            await items[0].click()
            await asyncio.sleep(1)

        await self.page.click('.normalBtn')
        await asyncio.sleep(5)


        # await self.page.click('.hwid-smsCode')
        #await asyncio.sleep(20)

        #await self.page.type('input[class="hwid-input"]','179840',{'delay': 10})
        #await asyncio.sleep(5)

        #await self.page.click('.dialog-btn.dialog-btn.btn-next.hwid-btn-primary')
        #await asyncio.sleep(5)
        #await self.page.click('.dialog-btn.dialog-btn.btn-next.hwid-btn-primary.hwid-btn-primary')
        #await asyncio.sleep(5)

    async def iam_login(self, username, password, parent):
        self.parent_user = os.environ.get('PARENT_USER', parent)

        try:
            await self.page.waitForSelector('#IAMLinkDiv')
            await asyncio.sleep(5)
            await self.page.click('#IAMLinkDiv')
            await asyncio.sleep(1)
            await self.page.type('#IAMAccountInputId', self.parent_user, {'delay': 10})
            await asyncio.sleep(0.5)
            await self.page.type('#IAMUsernameInputId', username, {'delay': 10})
            await asyncio.sleep(0.5)
            await self.page.type('#IAMPasswordInputId', password, {'delay': 10})
            await self.page.click('#loginBtn')
            await asyncio.sleep(5)
        except Exception as e:
            self.logger.exception(e)

    async def get_cookies(self):
        cookies = await self.page.cookies()
        new_cookies = {}
        for cookie in cookies:
            new_cookies[cookie['name']] = cookie['value']
        return new_cookies
