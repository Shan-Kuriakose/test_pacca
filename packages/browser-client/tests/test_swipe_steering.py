"""AC1 acceptance tests: a swipe on the play surface steers the snake.

The pipeline under test is the one the touch adapter builds at runtime:
a pointer sequence goes into the swipe recognizer, the recognized direction
goes into the steering seam, and the queued turn is applied on the tick that
follows. Node imports the production TypeScript sources directly; the tests
assert on the observed movement.
"""

from browser_driver import run_driver


def steer_by_swipe(start: dict, end: dict) -> dict:
    """Runs one recognized swipe through the steering seam and the next tick."""
    source = f"""
    const {{ recognizeSwipe }} = await import(`DOMAIN_ROOT_PLACEHOLDER/gesture.ts`);
    const {{ SteeringAuthority }} = await import(`DOMAIN_ROOT_PLACEHOLDER/steering.ts`);
    const {{ SnakeGame }} = await import(`DOMAIN_ROOT_PLACEHOLDER/snake.ts`);

    const game = new SnakeGame(24, 18);
    const recognized = recognizeSwipe([{{ x: {start["x"]}, y: {start["y"]} }},
                                       {{ x: {end["x"]}, y: {end["y"]} }}]);
    let accepted = null;
    if (recognized !== null) {{
        const authority = new SteeringAuthority(game.heading());
        accepted = authority.accept(recognized);
        if (accepted) {{
            game.turn(authority.queued());
        }}
    }}
    const before = game.body()[0];
    const status = game.tick();
    const after = game.body()[0];
    console.log(JSON.stringify({{
        recognized, accepted, before, after,
        status, heading: game.heading()
    }}));
    """
    return run_driver(source)


def test_swipe_past_the_recognition_distance_turns_the_snake_in_the_swiped_direction_on_the_next_tick():
    report = steer_by_swipe({"x": 10, "y": 50}, {"x": 10, "y": 110})

    assert report["recognized"] == "down"
    assert report["accepted"] is True
    assert report["after"]["y"] == report["before"]["y"] + 1
    assert report["after"]["x"] == report["before"]["x"]
    assert report["status"] == "playing"
    assert report["heading"] == "down"


def test_a_swipe_back_into_the_snakes_own_length_is_refused():
    report = steer_by_swipe({"x": 200, "y": 200}, {"x": 120, "y": 200})

    assert report["recognized"] == "left"
    assert report["accepted"] is False
    assert report["after"]["x"] == report["before"]["x"] + 1
    assert report["after"]["y"] == report["before"]["y"]
    assert report["status"] == "playing"
    assert report["heading"] == "right"


def test_a_swipe_shorter_than_the_recognition_distance_is_ignored():
    report = steer_by_swipe({"x": 100, "y": 100}, {"x": 110, "y": 100})

    assert report["recognized"] is None
    assert report["accepted"] is None
    assert report["after"]["x"] == report["before"]["x"] + 1
    assert report["after"]["y"] == report["before"]["y"]


def test_the_dominant_axis_maps_screen_space_swipe_directions():
    report = run_driver(
        """
        const { recognizeSwipe } = await import(`DOMAIN_ROOT_PLACEHOLDER/gesture.ts`);
        console.log(JSON.stringify({
            down: recognizeSwipe([{ x: 50, y: 10 }, { x: 50, y: 80 }]),
            up: recognizeSwipe([{ x: 50, y: 80 }, { x: 50, y: 10 }]),
            left: recognizeSwipe([{ x: 90, y: 10 }, { x: 10, y: 10 }]),
            right: recognizeSwipe([{ x: 10, y: 10 }, { x: 90, y: 10 }]),
            diagonalDominatedByOneAxis: recognizeSwipe([{ x: 0, y: 0 }, { x: 60, y: 20 }]),
            ambiguous: recognizeSwipe([{ x: 0, y: 0 }, { x: 44, y: 44 }])
        }));
        """
    )

    assert report["down"] == "down"
    assert report["up"] == "up"
    assert report["left"] == "left"
    assert report["right"] == "right"
    assert report["diagonalDominatedByOneAxis"] == "right"
    assert report["ambiguous"] is None


def test_the_recognition_distance_never_drops_below_the_44px_comfort_floor():
    report = run_driver(
        """
        const { SWIPE_MIN_DISTANCE } = await import(`DOMAIN_ROOT_PLACEHOLDER/gesture.ts`);
        console.log(JSON.stringify({ distance: SWIPE_MIN_DISTANCE }));
        """
    )

    assert report["distance"] >= 44
