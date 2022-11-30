import sys
import logging
import traceback

from aiohttp import web


class API:
    def __init__(self, port: str, mongo_url: str):
        self.port = port

        self.error_message = "Ошибка, обратитесь в службу поддержки"

        self.app = web.Application()
        self.app.router.add_post("/send_message", self.send_message)
        self.app.router.add_get("/_health", self.health)

        self.logger = logging.getLogger("redirect")

    def start(self):
        web.run_app(self.app, port=self.port)

    async def health(self, request):
        return web.Response(text="OK")

    async def send_message(self, request):
        pass

if __name__ == "__main__":
    service = Web(
        port=args["--port"],
        mongo_url=args["--mongo-url"]
    )

    try:
        service.start()
    except KeyboardInterrupt:
        print("Получен сигнал остановки")
        service.stop()
    except Exception:
        print("Произошла критическая ошибка")
        tb = traceback.format_exc()
        logging.critical(tb)
        sys.exit(1)
