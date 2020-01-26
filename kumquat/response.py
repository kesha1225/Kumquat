from kumquat.types import Scope, Receive, Send
import json
import typing


class SimpleResponse:
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
        self.status_code = status_code
        self.raw_headers = headers
        self.headers = self.create_headers()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.headers,
            }
        )
        await send({"type": "http.response.body", "body": self.body})

    def create_headers(self) -> typing.List[typing.List[bytes]]:
        _headers = [
            [b"content-length", str(len(self.body)).encode(self.charset)],
            [
                b"content-type",
                f"{self.content_type}; charset={self.charset}".encode(self.charset),
            ],
        ]

        if self.raw_headers is not None:
            _header = []
            for header in self.raw_headers:
                for k, v in header.items():
                    _header.extend([k.encode(self.charset), v.encode(self.charset)])
                _headers.append(_header)

        return _headers

    def parse_data(self) -> bytes:
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
        return json.dumps(self.data).encode(self.charset)
