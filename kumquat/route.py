"""
route schema
"""
import typing
from vbml import Patcher, PatchedValidators
from vbml import Pattern
from kumquat.exceptions import KumquatException
from kumquat.types import Method


class Route:
    """
    app route with path and func
    """

    def __init__(self, path: str, func: typing.Callable, methods: typing.Tuple[Method]):
        if not path.startswith("/"):
            raise KumquatException("Path must startswith from '/'")
        self.methods = methods
        self.path = path
        self.func = func


class Validators(PatchedValidators):
    """
    validator for routes paths
    """

    def route(self, value):
        if "/" not in value:
            return value
        return None


class Router:
    """
    class for saving all app routes
    """

    def __init__(self):
        self.patcher = Patcher(validators=Validators, default_validators=["route"])
        self.pattern = self.patcher.pattern
        self.routes: typing.Dict[typing.Tuple[typing.Tuple[Method], Pattern], Route] = {}

    def add_route(self, route: Route) -> None:
        """
        add route with vbml pattern path to stack
        :param route:
        :return:
        """
        self.routes[(route.methods, self.pattern(route.path))] = route

    def get_route(
        self, path: str, method: str
    ) -> typing.Tuple[typing.Dict[str, str], typing.Optional[Route]]:
        """
        get route object from string path
        :param method:
        :param path:
        :return:
        """
        # FIXME: simplification for getting index page route
        if path == "/":
            for route_methods, route_pattern in self.routes:
                if route_pattern.text == "/" and method in route_methods:
                    return {}, self.routes.get((route_methods, route_pattern))

        for route_methods, route_pattern in self.routes:
            if self.patcher.check(path, route_pattern) and method in route_methods:
                return (
                    self.patcher.check(path, route_pattern),
                    self.routes.get((route_methods, route_pattern)),
                )
            if path == route_pattern.text and method in route_methods:
                return {}, self.routes.get((route_methods, route_pattern))

        return {}, None
