import unittest

from bot import Bot, args_parser
from unittest.mock import AsyncMock


class TestBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        args = args_parser().parse_args()
        self.obj = Bot(args)

    async def test_send_msg(self):
        class Message:
            text = "kek"
            id = 1

        class Update:
            message = Message()
            effective_chat = Message()

        self.obj.amqp_client.send = AsyncMock()

        await self.obj.send_msg(Update(), "")
