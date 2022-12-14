import sys
import json
import logging
import asyncio
import traceback

from typing import Union

import aiormq
import aiormq.abc
import argparse

from aiormq import AMQPError
from lib.config_log import config_logger
from lib.aio_client import Client, AioClientException


class ServiceFormatError(Exception):
    """Универсальное исключение"""


class ServiceAMQP:
    def __init__(self, args):
        self.amqp_url = args.amqp_url
        self.amqp_queue = args.amqp_queue
        self.channel = None
        self.client = Client(
            args.url,
            args.path.replace(
                "TOKEN",
                args.token
            )
        )
        self.logger = config_logger()
        self.connetion = None

    async def start(self):
        await self._connection()
        await self._start_consuming()

    async def on_message(self, message: aiormq.abc.DeliveredMessage):
        """
        Получает и обрабатывает AMQP пакет
        Args:
            message - AMQP пакет
        """
        try:
            body = self._format_body(message.body)
            await self.client.send_message(body)
            await self.client.close()

            self.logger.info(f"Отправили сообщение {body}")

            await self.channel.basic_ack(message.delivery.delivery_tag)

        except AioClientException as e:
            self.logger.error(f"Ошибка aiohttp клиента: {e}")
            await self.client.close()
            await self.channel.basic_ack(message.delivery.delivery_tag)
        except AMQPError as e:
            self.logger.error(f"Ошибка AMQP: {e}")
            await self.channel.basic_ack(message.delivery.delivery_tag)

    async def _connection(self) -> None:
        """Создаёт подключение и канал"""
        self.connection = await aiormq.connect(self.amqp_url)
        self.channel = await self.connection.channel()
        await self.channel.basic_qos(prefetch_count=1)

    async def _start_consuming(self) -> None:
        """Включает прослушивание"""
        await self.channel.basic_consume(self.amqp_queue, self.on_message)

    def _format_body(self, body: bytes) -> Union[str, dict]:
        """Форматирует AMQP пакет"""
        try:
            return json.loads(body.decode("utf-8"))
        except (json.decoder.JSONDecodeError, TypeError, ValueError):
            raise ServiceFormatError("Пакет не может быть преобразован в json")


def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--amqp-url",
        help="URL для rabbitmq сервера, формат amqp://login:pass@server:port",
        default="amqp://guest:guest@rabbitmq/"
    )
    parser.add_argument(
        "--amqp-queue",
        default="tg_msg"
    )

    parser.add_argument(
        "--token",
        help="Токен доступа для телеграм бота",
        default="5677540474:AAEAXcSXYuyPXldGMwzufsSDZ5fQBd9cOLo",
    )

    parser.add_argument(
        "--url",
        default="https://api.telegram.org"
    )

    parser.add_argument(
        "--path",
        default="/botTOKEN/"
    )

    return parser


if __name__ == "__main__":
    args = args_parser().parse_args()

    service = ServiceAMQP(args=args)

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(service.start())
        loop.run_forever()
    except KeyboardInterrupt:
        print("Получен сигнал остановки")
        loop.stop()
    except Exception:
        print("Произошла критическая ошибка")
        tb = traceback.format_exc()
        logging.critical(tb)
        sys.exit(1)
