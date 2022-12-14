import json
import asyncio

import aiohttp


class AioClientException(Exception):
    """Универсальное исключение"""


class Client:
    def __init__(self, url: str, path: str):
        self.base_url = f"{url}{path}"
        self.session = None
        self.timeout = 20

    async def _create_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

    async def close(self):
        if self.session is None:
            return
        await self.session.close()
        self.session = None

    async def _request(
        self,
        method: str,
        url: str,
        params: dict
    ) -> str:
        """
        Создаёт запрос

        Args:
            payload - словарь с данными для отправки
            url - на который отправляется запрос
            method - метод отправки
        """
        try:
            await self._create_session()
            kwargs = {
                "method": method,
                "url": url,
                "params": params,
                "timeout": self.timeout
            }
            async with self.session.request(**kwargs) as resp:
                return await resp.json()
        except aiohttp.ClientResponseError as e:
            raise AioClientException(f"Неверный статус ответа: {e}")
        except aiohttp.ClientError as e:
            raise AioClientException(f"Ошибка при запросе: {e}")
        except asyncio.TimeoutError:
            raise AioClientException("Таймаут при запросе в tinkoff")
        except json.decoder.JSONDecodeError as e:
            raise AioClientException(f"Ошибка декодирования json: {e}")

    def _get_url(self, path: str) -> str:
        """Создаёт полную ссылку"""
        return f"{self.base_url}{path}"

    async def send_message(self, message: dict) -> None:
        """
        Отправляет сообщение в телеграм бота
        Args:
            message - сообщение
        """
        await self._request(
            method="GET",
            url=self._get_url("sendMessage"),
            params=message
        )
