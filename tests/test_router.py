import pytest
from sniffs import Router


@pytest.fixture
def router():
    router = Router()
    router.reset()
    return router


def test_add_route_no_replacement(router):
    def handler():
        pass

    router.add_route("home/+/temperature", handler)
    assert len(router.routes) == 1
    assert router.routes[0]["topic_pattern"].pattern == r"home/+/temperature"


def test_add_route_one_replacement(router):
    def handler():
        pass

    router.add_route("home/<some_replacement>/temperature", handler)
    assert len(router.routes) == 1
    assert (
        router.routes[0]["topic_pattern"].pattern
        == r"home/(?P<some_replacement>[^/]+)/temperature"
    )


def test_add_route_two_replacements(router):
    def handler():
        pass

    router.add_route("home/<replace_1>/<replace_2>", handler)
    assert len(router.routes) == 1
    assert (
        router.routes[0]["topic_pattern"].pattern
        == r"home/(?P<replace_1>[^/]+)/(?P<replace_2>[^/]+)"
    )


def test_add_route_named_replacement(router):
    def handler():
        pass

    router.add_route("home/<room>:{living_room,kitchen}/temperature", handler)
    assert len(router.routes) == 1
    assert (
        router.routes[0]["topic_pattern"].pattern
        == r"home/(?P<room>living_room|kitchen)/temperature"
    )


def test_add_route_two_named_replacements(router):
    def handler():
        pass

    router.add_route(
        "home/<room>:{living_room,kitchen}/<sensor>:{sensor1,sensor2}", handler
    )
    assert len(router.routes) == 1
    assert (
        router.routes[0]["topic_pattern"].pattern
        == r"home/(?P<room>living_room|kitchen)/(?P<sensor>sensor1|sensor2)"
    )


def test_route(router):
    def handler(any_variable):
        # assert topic == "home/kitchen/temperature"
        # assert message == "20"
        assert any_variable == "kitchen"

    router.add_route("home/<any_variable>/temperature", handler)
    router.route("home/kitchen/temperature", "20")


def test_route_multiple_groups(router):
    def handler(topic, message, room, sensor):
        # assert topic == "home/kitchen/temperature"
        # assert message == "20"
        assert room == "kitchen"
        assert sensor == "temperature"

    router.add_route(
        "home/<room>:{kitchen,living_room}/<sensor>:{sensor2,temperature}", handler
    )
    router.route("home/kitchen/temperature", "20")


def test_parse_topic_pattern(router):
    pattern = router._parse_topic_pattern("home/<kitchen>/temperature")
    assert pattern.match("home/kitchen/temperature") is not None
    assert pattern.match("home/kitchen/humidity") is None
