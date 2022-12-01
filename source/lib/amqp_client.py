import aiormq
import uuid

from aiormq import AMQPError


class AMQPClientException(Exception):
    """Универсальное исключение"""


class ClientAMQP:
    def __init__(
        self,
        amqp_url: str,
        exchange: str,
        route_key: str,
    ):
        self.amqp_url = amqp_url
        self.exchange = exchange
        self.route_key = route_key
        self.channel = None
        self._connection = None

    async def _connect(self):
        self._connection = await aiormq.connect(self.amqp_url)
        self._channel = await self._connection.channel()

    async def send(self, body: bytes):
        """
        Отправляет сообщение
        Args:
            body - тело сообщение
        """
        try:
            await self._connect()

            correlation_id = str(uuid.uuid4())

            await self._channel.basic_publish(
                body=body,
                exchange=self.exchange,
                routing_key=self.route_key,
                properties=aiormq.spec.Basic.Properties(
                    delivery_mode=2,
                    content_type="text/plain",
                    correlation_id=correlation_id,
                )
            )

            await self._connection.close()

        except AMQPError as e:
            raise AMQPClientException(f"AMQP Error: {e}")
