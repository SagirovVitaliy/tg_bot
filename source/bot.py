import sys
import json
import logging
import traceback

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from lib.amqp_client import ClientAMQP
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
        body = json.dumps(update.message.text).encode()
        await self.amqp_client.send(body)

def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--amqp-url",
        help="URL для rabbitmq сервера, формат amqp://login:pass@server:port",
        required=True
    )
    parser.add_argument(
        "--amqp-queue",
        required=True
    )

    parser.add_argument(
        "--token",
        help="Токен доступа для телеграм бота",
        required=True
    )

    parser.add_argument(
        "--url",
        required=True
    )

    parser.add_argument(
        "--path",
        required=True
    )

    return parser

if __name__ == '__main__':
    b = Bot('5677540474:AAEAXcSXYuyPXldGMwzufsSDZ5fQBd9cOLo')
    b.start()

    args = args_parser().parse_args()

    bot = Bot(args=args)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("Получен сигнал остановки")
        bot.stop()
    except Exception:
        print("Произошла критическая ошибка")
        tb = traceback.format_exc()
        logging.critical(tb)
        sys.exit(1)
