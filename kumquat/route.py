"""
route schema
"""
import typing
from vbml import Patcher, PatchedValidators
from vbml import Pattern
from kumquat.exceptions import KumquatException
from kumquat._types import Method


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

    def __repr__(self):
        return f'Route("{self.path}", {self.func})'


class Validators(PatchedValidators):
    """
    validator for routes paths
    """

    def route(self, value):
        if "/" not in value:
            return value
        return None


class RoutePattern(Pattern):
    def __init__(
        self, text: str = None, pattern: str = "{}$", lazy: bool = True, **context
    ):
        super().__init__(text, pattern, lazy, **context)

    def __repr__(self):
        return f'RoutePattern("{self.text}")'


class RoutePatcher(Patcher):
    def __init__(
        self,
        disable_validators: bool = False,
        validators: typing.Type[PatchedValidators] = None,
        **pattern_inherit_context,
    ):
        super().__init__(disable_validators, validators, **pattern_inherit_context)

    def pattern(self, _pattern: typing.Union[str, Pattern], **context):
        context.update(self.pattern_context)
        if isinstance(_pattern, Pattern):
            return _pattern.context_copy(**context)
        return RoutePattern(_pattern, **context)


class Router:
    """
    class for saving all app routes
    """

    def __init__(self):
        self.patcher = RoutePatcher(validators=Validators, default_validators=["route"])
        self.pattern = self.patcher.pattern
        self.routes: typing.Dict[
            typing.Tuple[typing.Tuple[Method], Pattern], Route
        ] = {}

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
        for route_methods, route_pattern in self.routes:
            if path == route_pattern.text:
                return {}, self.routes.get((route_methods, route_pattern))

            if self.patcher.check(path, route_pattern):
                return (
                    self.patcher.check(path, route_pattern),
                    self.routes.get((route_methods, route_pattern)),
                )
        return {}, None
