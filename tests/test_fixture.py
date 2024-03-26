import pytest

from sniffs.fixture import FixtureProvider, Fixture, inject_fixtures
from sniffs.router import route, Router

fixture_one = Fixture("One")
fixture_two = Fixture("Two")


# Fixture setup
@pytest.fixture
def fixture_provider():
    provider = FixtureProvider()
    provider.register_fixture("fixture_one", Fixture("One"))
    provider.register_fixture("fixture_two", Fixture("Two"))
    return provider


@pytest.fixture
def router():
    router = Router()
    router.reset()
    return router


# Mocking the application context for testing
class MockAppContext:
    def __init__(self, fixture_provider):
        self.fixture_provider = fixture_provider


# Mocking the app object with the required methods for testing
class MockApp:
    def __init__(self, fixture_provider):
        self.app_context = MockAppContext(fixture_provider)

    def route(self, path):
        def decorator(func):
            return inject_fixtures(func)

        return decorator


# Tests for route decorator
def test_route_decorator(fixture_provider):
    # Creating a mock app object
    mocked_app = MockApp(fixture_provider)

    # Defining a function decorated with @route
    @mocked_app.route("test")
    def test_function(fixture_one, fixture_two):
        return (fixture_one, fixture_two)

    # Calling the function
    output = test_function()

    # Checking the output
    assert tuple(_output.__repr__() for _output in output) == (
        "<Fixture One>",
        "<Fixture Two>",
    )


# Tests for route decorator
def test_real_route_decorator(router):
    # Defining a function decorated with @route
    @route("home/<testing>:{foo,bar}/temperature")
    def test_function(testing):
        return testing

    result = Router().route("home/foo/temperature", "a message")
    assert result == "foo"
