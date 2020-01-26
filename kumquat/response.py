"""
response schema
"""
import json
import typing
from kumquat.types import Scope, Receive, Send

try:
    import ujson
except ImportError:
    ujson = None

json_library = json if ujson is None else ujson


class SimpleResponse:
    """
    response data class
    """

    charset = "utf-8"
    content_type = "text/plain"

    def __init__(
        self,
        body: typing.Any,
        headers: typing.List[typing.Dict[str, str]] = None,
        status_code: int = 200,
    ):
        self.data = body
        self.body = self.parse_data()
        self._status_code = status_code
        self._custom_headers = headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self._create_headers(),
            }
        )
        await send({"type": "http.response.body", "body": self.body})

    @property
    def custom_headers(self):
        """
        headers property for response

        :return:
        """
        return self._custom_headers

    @custom_headers.setter
    def custom_headers(self, value):
        self._custom_headers = value

    @property
    def status_code(self):
        """
        status code property for response
        :return:
        """
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    def _create_headers(self) -> typing.List[typing.List[bytes]]:
        _headers = [
            [b"content-length", str(len(self.body)).encode(self.charset)],
            [
                b"content-type",
                f"{self.content_type}; charset={self.charset}".encode(self.charset),
            ],
        ]

        if self.custom_headers is not None:
            _header = []
            for header in self.custom_headers:
                for k, v in header.items():
                    _header.extend([k.encode(self.charset), v.encode(self.charset)])
                _headers.append(_header)
        return _headers

    def set_headers(self, headers: typing.Dict[str, str]):
        """
        set headers for response
        :param headers:
        :return:
        """
        if self.custom_headers is None:
            self.custom_headers = []
        self.custom_headers.append(headers)

    def parse_data(self) -> bytes:
        """
        encode response body to bytes
        :return:
        """
        if isinstance(self.data, bytes):
            return self.data
        return self.data.encode(self.charset)


class TextResponse(SimpleResponse):
    content_type = "text/plain"


class HTMLResponse(SimpleResponse):
    content_type = "text/html"


class JSONResponse(SimpleResponse):
    content_type = "application/json"

    def parse_data(self):
        return json_library.dumps(self.data).encode(self.charset)
