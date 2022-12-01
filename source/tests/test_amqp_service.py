import json
import unittest

from amqp_service import ServiceAMQP, args_parser
from unittest.mock import AsyncMock, MagicMock


class TestBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        args = args_parser().parse_args()
        self.obj = ServiceAMQP(args)

    async def test_on_message(self):
        class Message:
            body = json.dumps({"kek": "chebureck"}).encode()
            delivery = MagicMock()

        self.obj.channel = MagicMock()
        self.obj.channel.basic_ack = AsyncMock()
        self.obj.client.send_message = AsyncMock()

        await self.obj.on_message(Message())
