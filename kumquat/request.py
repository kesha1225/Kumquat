"""
request schema
"""
import typing
import urllib.parse
from collections import namedtuple

from kumquat.types import Scope, Receive

_server = namedtuple("server", ["host", "port"])
_client = namedtuple("client", ["host", "port"])


class Request:
    """
    request data class
    """

    charset = "utf-8"

    def __init__(self, scope: Scope, receive: Receive):
        self._receive = receive
        self._body: typing.Dict[str, str] = {}

        self._type = scope.get("type")
        self.http_version = scope.get("http_version")
        self.server = _server(scope["server"][0], scope["server"][1])
        self.client = _client(scope["client"][0], scope["client"][1])
        self.scheme = scope.get("scheme")
        self.method = scope.get("method")
        self.root_path = scope.get("root_path")
        self.path = scope["path"].rstrip("/") if scope["path"] != "/" else scope["path"]
        self._path_dict: typing.Dict[str, str] = {}
        self.raw_path = scope.get("raw_path")
        self.query_string = scope.get("query_string")
        self.query: typing.Dict[str, str] = {}
        if self.query_string:
            self.query_string = self.query_string.decode(self.charset)
            self.query = dict(
                urllib.parse.parse_qsl(self.query_string, encoding=self.charset)
            )

        self.headers = dict(scope["headers"])
        self._stream_consumed = False
        self._is_disconnected = False

    async def _stream(self) -> typing.AsyncGenerator[bytes, None]:
        if self._stream_consumed:
            raise RuntimeError("Stream consumed")

        self._stream_consumed = True
        while True:
            message = await self._receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    yield body
                if not message.get("more_body", False):
                    break
            elif message["type"] == "http.disconnect":
                self._is_disconnected = True
                raise RuntimeError("Client disconnected")
        yield b""

    async def body(self):
        if not self._body:
            async for part in self._stream():
                self._body.update(
                    dict(
                        urllib.parse.parse_qsl(
                            part.decode(self.charset), encoding=self.charset
                        )
                    )
                )
        return self._body

    @property
    def path_dict(self) -> dict:
        """
        dict of path params if it looks like /<param>
        :return:
        """
        return self._path_dict

    @path_dict.setter
    def path_dict(self, value) -> None:
        self._path_dict = value
