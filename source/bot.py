import sys
import json
import logging
import traceback
import argparse

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from lib.amqp_client import ClientAMQP, AMQPClientException
from lib.config_log import config_logger


class Bot:
    """
    Создаёт бота
    Args:
        token - токен дотупа к боту
    """
    def __init__(self, args):
        self.app = Application.builder().token(args.token).build()
        self.app.add_handler(MessageHandler(filters.TEXT, self.send_msg))

        self.amqp_client = ClientAMQP(
            args.amqp_url,
            args.exchange,
            args.route_key
        )

        self.logger = config_logger()

    def start(self):
        self.app.run_polling()

    async def send_msg(
        self,
        update: Update,
        context: ContextTypes
    ):
        try:
            body = json.dumps(update.message.text).encode()
            await self.amqp_client.send(body)
        except AMQPClientException as e:
            self.logger.error(f"Ошибка AMQP: {e}")


def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--amqp-url",
        help="URL для rabbitmq сервера, формат amqp://login:pass@server:port",
        required=True
    )

    parser.add_argument(
        "--exchange",
        required=True
    )

    parser.add_argument(
        "--route-key",
        default=""
    )

    parser.add_argument(
        "--token",
        help="Токен доступа для телеграм бота",
        default="5677540474:AAEAXcSXYuyPXldGMwzufsSDZ5fQBd9cOLo",
        required=True
    )

    return parser


if __name__ == '__main__':
    args = args_parser().parse_args()

    bot = Bot(args=args)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("Получен сигнал остановки")
        # Пока не понятно как это останавливать
    except Exception:
        print("Произошла критическая ошибка")
        tb = traceback.format_exc()
        logging.critical(tb)
        sys.exit(1)
