import pytest
from sniffs.router import Router


@pytest.fixture
def router():
    return Router()


def test_add_route(router):
    def handler(topic, message, groups):
        pass

    router.add_route("home/+/temperature", handler)
    assert len(router.routes) == 1
    assert router.routes[0]["topic_pattern"].pattern == r"home/([^/]*)/temperature"


def test_add_route_two_replacements(router):
    def handler(topic, message, groups):
        pass

    router.add_route("home/+/+", handler)
    assert len(router.routes) == 1
    assert router.routes[0]["topic_pattern"].pattern == r"home/([^/]*)/([^/]*)"


def test_add_route_named_replacement(router):
    def handler(topic, message, groups):
        pass

    router.add_route("home/{living_room,kitchen}/temperature", handler)
    assert len(router.routes) == 1
    assert (
        router.routes[0]["topic_pattern"].pattern
        == r"home/(living_room|kitchen)/temperature"
    )


def test_add_route_two_named_replacements(router):
    def handler(topic, message, groups):
        pass

    router.add_route("home/{living_room,kitchen}/{sensor1,sensor2}", handler)
    assert len(router.routes) == 1
    assert (
        router.routes[0]["topic_pattern"].pattern
        == r"home/(living_room|kitchen)/(sensor1|sensor2)"
    )


def test_route(router):
    def handler(topic, message, groups):
        assert topic == "home/kitchen/temperature"
        assert message == "20"
        assert groups == ("kitchen",)

    router.add_route("home/+/temperature", handler)
    router.route("home/kitchen/temperature", "20")


def test_route_multiple_groups(router):
    def handler(topic, message, groups):
        assert topic == "home/kitchen/temperature"
        assert message == "20"
        assert groups == ("kitchen", "temperature")

    router.add_route("home/{kitchen,living_room}/{sensor2,temperature}", handler)
    router.route("home/kitchen/temperature", "20")


def test_parse_topic_pattern(router):
    pattern = router._parse_topic_pattern("home/+/temperature")
    assert pattern.match("home/kitchen/temperature") is not None
    assert pattern.match("home/kitchen/humidity") is None
