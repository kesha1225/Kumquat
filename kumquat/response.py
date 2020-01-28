"""
response schema
"""
import json
import typing

import jinja2
from aiofile import AIOFile

from kumquat.types import Scope, Receive, Send
from kumquat.context import env_var

try:
    import ujson
except ImportError:
    ujson = None

JSON = json if ujson is None else ujson


class SimpleResponse:
    """
    base kumquat response
    """

    charset = "utf-8"
    content_type = "text/plain"

    def __init__(
        self,
        body: typing.Any,
        headers: typing.List[typing.Dict[str, str]] = None,
        status_code: int = 200,
    ):
        self.body = body
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
        await send({"type": "http.response.body", "body": self.parse_body()})

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
            [b"content-length", str(len(self.parse_body())).encode(self.charset)],
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

    def parse_body(self) -> bytes:
        """
        encode response body to bytes
        :return:
        """
        if isinstance(self.body, bytes):
            return self.body
        if isinstance(self.body, dict):
            return JSON.dumps(self.body).encode(self.charset)

        return self.body.encode(self.charset)


class TextResponse(SimpleResponse):
    content_type = "text/plain"


class HTMLResponse(SimpleResponse):
    content_type = "text/html"


class JsonResponse(SimpleResponse):
    content_type = "application/json"


class TemplateResponse(SimpleResponse):
    """
    response for rendering templates
    """
    content_type = "text/html"

    def __init__(self, template: str, **kwargs):
        super().__init__(b"")
        self.template = template
        self.template_data = kwargs

    async def _render_template(self) -> str:
        if env_var.get() == "/":
            env_var.set("")
        async with AIOFile(
            f"{env_var.get()}{self.template}", "r", encoding="utf-8"
        ) as file:
            template = jinja2.Template(await file.read())
        return template.render(self.template_data)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.body = await self._render_template()
        await super().__call__(scope, receive, send)
