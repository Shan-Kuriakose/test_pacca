"""AC3 acceptance tests: touch and keyboard feed one steering seam.

Both adapters accept into the same SteeringAuthority per tick, so a session
that mixes them yields exactly one turn, the last accepted input wins, and a
refusal of one source's turn leaves the other source's turn intact. The
keyboard adapter's key mapping is tested against the same production module
the touch adapter shares the seam with.
"""

from browser_driver import run_driver


def mix_a_rejected_swipe_with_a_key_turn() -> dict:
    source = """
    const { recognizeSwipe } = await import(`DOMAIN_ROOT_PLACEHOLDER/gesture.ts`);
    const { SteeringAuthority } = await import(`DOMAIN_ROOT_PLACEHOLDER/steering.ts`);
    const { keyToDirection } = await import(`ADAPTERS_ROOT_PLACEHOLDER/keyboard_input.ts`);
    const { SnakeGame } = await import(`DOMAIN_ROOT_PLACEHOLDER/snake.ts`);

    const game = new SnakeGame(24, 18);
    const authority = new SteeringAuthority(game.heading());
    const swiped = recognizeSwipe([{ x: 200, y: 100 }, { x: 120, y: 100 }]);
    const swipeAccepted = authority.accept(swiped);
    const keyed = keyToDirection("ArrowUp");
    const keyAccepted = authority.accept(keyed);
    if (keyAccepted) {
        game.turn(authority.queued());
    }
    const before = game.body()[0];
    const status = game.tick();
    const after = game.body()[0];
    console.log(JSON.stringify({
        swiped, swipeAccepted, keyed, keyAccepted,
        before, after, status, heading: game.heading()
    }));
    """
    return run_driver(source)


def test_a_swipe_refused_as_a_reversal_does_not_spoil_the_key_turn():
    report = mix_a_rejected_swipe_with_a_key_turn()

    assert report["swiped"] == "left"
    assert report["swipeAccepted"] is False
    assert report["keyed"] == "up"
    assert report["keyAccepted"] is True
    assert report["after"]["y"] == report["before"]["y"] - 1
    assert report["heading"] == "up"
    assert report["status"] == "playing"


def test_a_key_turn_and_a_swipe_in_the_same_tick_turn_the_snake_exactly_once_with_the_last_input_winning():
    report = run_driver(
        """
        const { SteeringAuthority } = await import(`DOMAIN_ROOT_PLACEHOLDER/steering.ts`);
        const { SnakeGame } = await import(`DOMAIN_ROOT_PLACEHOLDER/snake.ts`);

        const game = new SnakeGame(24, 18);
        const authority = new SteeringAuthority(game.heading());
        const keyTurnAccepted = authority.accept("up");
        const swipeTurnAccepted = authority.accept("down");
        const queued = authority.queued();
        game.turn(queued);
        const before = game.body()[0];
        const status = game.tick();
        const after = game.body()[0];
        console.log(JSON.stringify({
            keyTurnAccepted, swipeTurnAccepted, queued,
            before, after, status, heading: game.heading()
        }));
        """
    )

    assert report["keyTurnAccepted"] is True
    assert report["swipeTurnAccepted"] is True
    assert report["queued"] == "down"
    assert report["after"]["y"] == report["before"]["y"] + 1
    assert report["after"]["x"] == report["before"]["x"]
    assert report["heading"] == "down"
    assert report["status"] == "playing"


def test_keyboard_keys_map_to_directions():
    report = run_driver(
        """
        const { keyToDirection } = await import(`ADAPTERS_ROOT_PLACEHOLDER/keyboard_input.ts`);
        console.log(JSON.stringify({
            arrowUp: keyToDirection("ArrowUp"),
            arrowDown: keyToDirection("ArrowDown"),
            arrowLeft: keyToDirection("ArrowLeft"),
            arrowRight: keyToDirection("ArrowRight"),
            wasdUp: keyToDirection("w"),
            wasdDown: keyToDirection("s"),
            wasdLeft: keyToDirection("a"),
            wasdRight: keyToDirection("d"),
            unmapped: keyToDirection("q")
        }));
        """
    )

    assert report["arrowUp"] == "up"
    assert report["arrowDown"] == "down"
    assert report["arrowLeft"] == "left"
    assert report["arrowRight"] == "right"
    assert report["wasdUp"] == "up"
    assert report["wasdDown"] == "down"
    assert report["wasdLeft"] == "left"
    assert report["wasdRight"] == "right"
    assert report["unmapped"] is None
