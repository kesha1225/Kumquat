import uvicorn
import typing
from kumquat.response import TextResponse, JSONResponse, SimpleResponse
from kumquat.route import Route, Router
from kumquat.request import Request
import logging

logging.basicConfig(format="%(levelname)s:     %(message)s", level="DEBUG")


class Kumquat:
    def __init__(self):
        self.logger = logging.getLogger(__package__)
        self.router = Router()
        self._app_name = "KumquatApp"

    @property
    def app_name(self):
        return self._app_name

    @app_name.setter
    def app_name(self, name):
        self._app_name = name

    async def __call__(self, scope, receive, send) -> None:
        request = Request(scope)
        path_dict, current_route = self.router.get_route(request.path)
        request.path_dict = path_dict

        response: SimpleResponse = await self._prepare_response(request, current_route)
        await response(scope, receive, send)

    @staticmethod
    async def _prepare_response(request, current_route) -> SimpleResponse:
        if current_route is None:
            return TextResponse("Not Found", status_code=404)

        if request.method not in current_route.methods:
            return TextResponse("Method Not Allowed", status_code=405)

        route_result = await current_route.func(request)

        if isinstance(route_result, SimpleResponse):
            return route_result

        if isinstance(route_result, str):
            return TextResponse(route_result)

        if isinstance(route_result, dict):
            return JSONResponse(route_result)

        if isinstance(route_result, tuple):
            data, status_code = route_result
            if isinstance(data, str):
                return TextResponse(data, status_code=status_code)

            if isinstance(data, dict):
                return JSONResponse(data, status_code=status_code)

        return TextResponse(str(route_result))

    def get(self, path: str):
        def decorator(func: typing.Callable) -> typing.Callable:
            assert path.startswith("/")
            route = Route(path, func, methods=["GET"])
            self.router.add_route(route)
            return func

        return decorator

    def post(self, path: str):
        def decorator(func: typing.Callable) -> typing.Callable:
            assert path.startswith("/")
            route = Route(path, func, methods=["POST"])
            self.router.add_route(route)
            return func

        return decorator

    def route(self, path: str, methods: typing.List[str]):
        def decorator(func: typing.Callable) -> typing.Callable:
            assert path.startswith("/")
            route = Route(path, func, methods=methods)
            self.router.add_route(route)
            return func

        return decorator

    def index(self):
        def decorator(func: typing.Callable) -> typing.Callable:
            route = Route("/", func, methods=["GET"])
            self.router.add_route(route)
            return func

        return decorator

    def run(self):
        self.logger.info(f"Starting {self.app_name} app...")
        uvicorn.run(self)
