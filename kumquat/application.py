"""
kumquat application
"""
import typing
import logging
import inspect

import uvicorn

from kumquat.context import env_var
from kumquat.response import (
    TextResponse,
    JsonResponse,
    SimpleResponse,
    TemplateResponse,
    HTMLResponse,
)
from kumquat.route import Route, Router
from kumquat.request import Request
from kumquat.exceptions import KumquatException
from kumquat._types import Method, Scope, Receive, Send
from kumquat.utils import BackgroundTask

try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None

logger = logging.getLogger(__name__)

RouteFunc = typing.Callable[[Request, SimpleResponse], typing.Any]


def _dispatch_simple_response(
    data: SimpleResponse, status_code: int, response: SimpleResponse
) -> SimpleResponse:
    data.custom_headers = response.custom_headers
    data.status_code = status_code
    return data


def _dispatch_factory(
    data: typing.Any,
    status_code: int,
    response: SimpleResponse,
    response_class: typing.Type[SimpleResponse],
) -> typing.Callable:
    return response_class(
        data, headers=response.custom_headers, status_code=status_code
    )


def _dispatch_lambda_factory(
    response_class: typing.Type[SimpleResponse],
) -> typing.Callable:
    return lambda *args: _dispatch_factory(*args, response_class=response_class)


_DISPATCH_TYPES = {
    SimpleResponse: _dispatch_simple_response,
    HTMLResponse: _dispatch_simple_response,
    TemplateResponse: _dispatch_simple_response,
    str: _dispatch_lambda_factory(TextResponse),
    dict: _dispatch_lambda_factory(JsonResponse),
}


def _process_route_result(
    route_result: typing.Any, response: SimpleResponse
) -> typing.Union[
    SimpleResponse, TextResponse, JsonResponse, TemplateResponse, HTMLResponse,
]:
    status_code = response.status_code

    if isinstance(route_result, tuple):
        data = route_result[0]
        status_code = route_result[1]
    else:
        data = route_result
    result: typing.Optional[typing.Callable] = _DISPATCH_TYPES.get(type(data))
    if result is not None:
        return result(data, status_code, response)

    return TextResponse(
        str(data), status_code=status_code, headers=response.custom_headers,
    )


class Kumquat:
    """
    kumquat web application
    """

    def __init__(self, templates_path: str = "templates/"):
        self.router = Router()
        self.middleware_stack: typing.List[
            typing.Callable[[Request, SimpleResponse], typing.Any]
        ] = []
        env_var.set(templates_path)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)
        _response = SimpleResponse(b"")
        path_dict, current_route = self.router.get_route(request.path, request.method)
        request.path_dict = path_dict

        response = await self._prepare_response(request, _response, current_route)
        await self._call_middleware_stack(request, response)
        await response(scope, receive, send)

    @staticmethod
    async def _prepare_response(
        request: Request,
        response: SimpleResponse,
        current_route: typing.Optional[Route],
    ) -> SimpleResponse:
        if current_route is None:
            return TextResponse("Not Found", status_code=404)

        if request.method not in current_route.methods:
            return TextResponse("Method Not Allowed", status_code=405)

        route_result: typing.Any = await current_route.func(request, response)
        return _process_route_result(route_result, response)

    async def _call_middleware_stack(
        self, request: Request, response: SimpleResponse
    ) -> None:
        for middleware_func in self.middleware_stack:
            if inspect.iscoroutinefunction(middleware_func):
                await middleware_func(request, response)
            elif inspect.isfunction(middleware_func):
                await (BackgroundTask(middleware_func, request, response))()

    def create_route(
        self, path: str, func: RouteFunc, methods: typing.Tuple[Method],
    ) -> typing.Optional[typing.NoReturn]:
        """
        create any method route for app
        :param path:
        :param func:
        :param methods:
        :return:
        """
        route = Route(path, func, methods=methods)

        route_func_arg_count = route.func.__code__.co_argcount

        if route_func_arg_count != 2:
            raise KumquatException(
                f"function <<{func.__name__}>> must take strictly 2 args"
            )
        self.router.add_route(route)
        return None

    def create_middleware(self, func: RouteFunc) -> None:
        self.middleware_stack.append(func)

    def middleware(self) -> typing.Callable:
        """
        decorator for creating middleware
        :return:
        """

        def decorator(func: RouteFunc) -> typing.Callable:
            self.create_middleware(func)
            return func

        return decorator

    def get(self, path: str):
        """
        decorator for creating get route
        :param path:
        :return:
        """

        def decorator(func: RouteFunc) -> typing.Callable:
            self.create_route(path, func, methods=(Method("GET"),))
            return func

        return decorator

    def post(self, path: str):
        """
        decorator for creating post route
        :param path:
        :return:
        """

        def decorator(func: RouteFunc) -> typing.Callable:
            self.create_route(path, func, methods=(Method("POST"),))
            return func

        return decorator

    def route(self, path: str, methods: typing.Tuple[Method]):
        """
        decorator for creating any method route
        :param path:
        :param methods:
        :return:
        """

        def decorator(func: RouteFunc) -> typing.Callable:
            self.create_route(path, func, methods=methods)
            return func

        return decorator

    def index(self):
        """
        decorator for creating index route (path = '/')
        :return:
        """

        def decorator(func: RouteFunc) -> typing.Callable:
            self.create_route("/", func, methods=(Method("GET"),))
            return func

        return decorator

    def run(self, host: str = "127.0.0.1", port: int = 8000, log_level: str = "info"):
        """
        start application with uvicorn
        :param host:
        :param port:
        :param log_level:
        :return:
        """
        uvicorn.run(self, host=host, port=port, log_level=log_level)

    def ngrok_run(self, port: int = 8000):
        if ngrok is None:
            raise ImportError(
                "For this method you have to install pyngrok - pip install pyngrok"
            )
        public_url = ngrok.connect(port=port)
        print(f"Server started on {public_url}")
        self.run(port=port)
