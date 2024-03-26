import pytest
from sniffs import Router, Sniffs


@pytest.fixture
def sniffs():
    app = Sniffs()
    return app


@pytest.fixture
def router():
    router = Router()
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
    def handler(any_variable, topic, message):
        assert topic == "home/kitchen/temperature"
        assert message == "20"
        assert any_variable == "kitchen"

    router.add_route("home/<any_variable>/temperature", handler)
    router.route("home/kitchen/temperature", "20")


def test_route_multiple_groups(router):
    def handler(topic, message, room, sensor):
        assert topic == "home/kitchen/temperature"
        assert message == "20"
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


def test_route_decorator(sniffs):
    @sniffs.route("home/<one>/<two>")
    def test_function(one, two):
        return (one, two)

    output = sniffs.router.route("home/anything/really", "some message")

    assert ("anything", "really") in output


def test_real_route_decorator(sniffs):
    @sniffs.route("home/<testing>:{foo,bar}/temperature")
    def test_function(testing):
        return testing

    output = sniffs.router.route("home/foo/temperature", "a message")
    assert "foo" in output


def test_topic_is_accessible(sniffs):
    @sniffs.route("home/<testing>:{foo,bar}/temperature")
    def test_function(topic):
        assert topic == "home/foo/temperature"

    sniffs.router.route("home/foo/temperature", "a message")


def test_message_is_accessible(sniffs):
    @sniffs.route("home/<testing>:{foo,bar}/temperature")
    def test_function(message):
        assert message == "a message"

    sniffs.router.route("home/foo/temperature", "a message")


@pytest.mark.parametrize(
    "template_paths, expected_topics",
    [
        (
            [
                "home/<testing>:{foo,bar}/temperature",
                "home/<room>:{living_room,kitchen}/<sensor>:{sensor1,sensor2}",
                "home/<any_variable>/temperature",
                "home/<replace_1>/<replace_2>",
            ],
            [
                "home/foo/temperature",
                "home/bar/temperature",
                "home/living_room/sensor1",
                "home/living_room/sensor2",
                "home/kitchen/sensor1",
                "home/kitchen/sensor2",
                "home/+/temperature",
                "home/+/+",
            ],
        ),
        (
            ["home/<testing>:{foo,bar}/temperature"],
            ["home/foo/temperature", "home/bar/temperature"],
        ),
        (
            [
                "home/<room>:{living_room,kitchen}/<sensor>:{sensor1,sensor2}",
                "home/<replace_1>/<replace_2>",
            ],
            [
                "home/living_room/sensor1",
                "home/living_room/sensor2",
                "home/kitchen/sensor1",
                "home/kitchen/sensor2",
                "home/+/+",
            ],
        ),
        (["home/no/variables/here"], ["home/no/variables/here"]),
    ],
)
def test_generate_subscription_topics(router, template_paths, expected_topics):
    actual_topics = router._generate_subscription_topic_paths(template_paths)
    assert actual_topics == expected_topics
