import unittest

from lib.aio_client import Client, AioClientException

from aioresponses import aioresponses


class TestBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.obj = Client(
            url="https://api.telegram.org",
            path="/bot123/"
        )

    async def asyncTearDown(self):
        await self.obj.close()

    @aioresponses()
    async def test_request(self, m):
        with self.subTest("success-get"):
            aioresponses.add(
                m,
                url="http://test.ru",
                method="GET",
            )

            await self.obj._request("GET", "http://test.ru", {})

        with self.subTest("success-post"):
            aioresponses.add(
                m,
                url="http://test.ru",
                method="POST",
            )

            await self.obj._request("POST", "http://test.ru", {})

        with self.subTest("error"):
            with self.assertRaises(AioClientException):
                aioresponses.add(
                    m,
                    url="http://test.ru",
                    method="GET",
                    status=404
                )

                await self.obj._request("GET", "http://test.ru", {})

        with self.subTest("error_timeout"):
            with self.assertRaises(AioClientException):
                aioresponses.add(
                    m,
                    url="http://test.ru",
                    method="GET",
                    timeout=True
                )

                await self.obj._request("GET", "http://test.ru", {})

    @aioresponses()
    async def test_send_message(self, m):
        aioresponses.add(
            m,
            url="https://api.telegram.org/bot123/sendMessage?text=kek&chat_id=1", # noqa
            method="GET"
        )

        await self.obj.send_message({"text": "kek", "chat_id": 1})
