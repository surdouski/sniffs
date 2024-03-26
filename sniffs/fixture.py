from typing import Callable
from sniffs.util import singleton
from frozendict import frozendict

_RESERVED_FIXTURE_NAMES = frozenset(["topic", "message", "variables"])


@singleton
class FixtureProvider:
    _lock = False

    def __init__(self):
        self.fixtures = {}

    def lock(self):
        self._lock = True

    def register_fixture(self, name: str, fixture_func: Callable):
        if self._lock and name in _RESERVED_FIXTURE_NAMES:
            raise Exception(
                f"Can't register {name} for fixture because it is reserved."
            )
        if name and self.fixtures.get(name):
            raise Exception(f"{name} is already a registered fixture.")
        self.fixtures[name] = fixture_func

    def unregister_fixture(self, name: str):
        if name in _RESERVED_FIXTURE_NAMES:
            raise Exception(f"Can't unregister {name} because it is reserved.")
        print(name)
        print(self.fixtures)
        if name and self.fixtures.get(name):
            del self.fixtures[name]

    def get_fixture(self, arg_name: str) -> Callable:
        return self.fixtures.get(arg_name)


class Fixture:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Fixture {self.name}>"


FixtureProvider().register_fixture("topic", Fixture("topic"))
FixtureProvider().register_fixture("message", Fixture("message"))
FixtureProvider().register_fixture("variables", Fixture("variables"))
FixtureProvider().lock()


# Decorator to inject fixtures based on argument names
def inject_fixtures(func):
    def wrapper(*args, **kwargs):
        fixture_args = []
        for arg in func.__code__.co_varnames:
            fixture_args.append(FixtureProvider().get_fixture(arg))
        return func(*fixture_args)

    return wrapper


_RESERVED_FIXTURE_DICT = frozendict(
    {
        "topic": Fixture("topic"),
        "message": Fixture("message"),
        "variables": Fixture("variables"),
    }
)
