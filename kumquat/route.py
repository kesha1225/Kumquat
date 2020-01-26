import typing
from vbml import Patcher, PatchedValidators
from vbml import Pattern


class Route:
    def __init__(self, path: str, func: typing.Callable, methods: typing.List[str]):
        self.methods = methods
        self.path = path
        self.func = func


class Validators(PatchedValidators):
    def route(self, value):
        if "/" not in value:
            return value


class Router:
    def __init__(self):
        self.patcher = Patcher(validators=Validators, default_validators=["route"])
        self.pattern = self.patcher.pattern
        self.routes: typing.Dict[Pattern, Route] = {}

    def add_route(self, route: Route):
        self.routes[self.pattern(route.path)] = route

    def get_route(
        self, path
    ) -> typing.Tuple[typing.Dict[str, str], typing.Optional[Route]]:
        # FIXME: simplification for getting index page route
        if path == "/":
            for route_pattern in self.routes.keys():
                if route_pattern.text == "/":
                    return {}, self.routes.get(route_pattern)

        for route_pattern in self.routes.keys():
            if self.patcher.check(path, route_pattern):
                return (
                    self.patcher.check(path, route_pattern),
                    self.routes.get(route_pattern),
                )
            if path == route_pattern.text:
                return {}, self.routes.get(route_pattern)

        return {}, None
