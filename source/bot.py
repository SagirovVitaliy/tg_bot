import sys
import json
import logging
import traceback
import argparse

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler
)

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
        self.app.add_handler(CommandHandler('start', self.start))
        self.app.add_handler(MessageHandler(filters.TEXT, self.send_msg))

        self.amqp_client = ClientAMQP(
            args.amqp_url,
            args.exchange,
            args.route_key
        )

        self.logger = config_logger()

    def start_bot(self) -> None:
        self.app.run_polling()

    async def start(self, update: Update, context: ContextTypes):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm a bot, please talk to me!"
        )

    async def send_msg(
        self,
        update: Update,
        context: ContextTypes
    ) -> None:
        try:
            body = {
                "text": update.message.text,
                "chat_id": update.effective_chat.id
            }
            await self.amqp_client.send(json.dumps(body).encode())
            self.logger.info(f"Отправили сообщение: {body}")
        except AMQPClientException as e:
            self.logger.error(f"Ошибка AMQP: {e}")


def args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--amqp-url",
        help="URL для rabbitmq сервера, формат amqp://login:pass@server:port",
        default="amqp://guest:guest@localhost/"
    )

    parser.add_argument(
        "--exchange",
        default="tg_bot"
    )

    parser.add_argument(
        "--route-key",
        default=""
    )

    parser.add_argument(
        "--token",
        help="Токен доступа для телеграм бота",
        default="5677540474:AAEAXcSXYuyPXldGMwzufsSDZ5fQBd9cOLo"
    )

    return parser


if __name__ == '__main__':
    args = args_parser().parse_args()

    bot = Bot(args=args)

    try:
        bot.start_bot()
    except KeyboardInterrupt:
        print("Получен сигнал остановки")
    except Exception:
        print("Произошла критическая ошибка")
        tb = traceback.format_exc()
        logging.critical(tb)
        sys.exit(1)
