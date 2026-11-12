"""Tick-loop behaviour the steering tests depend on.

A turn is queued and applied to the next tick only, and the round ends when
the head runs into the snake's own body. The engine is imported by Node the
same way the swipe tests drive it.
"""

from browser_driver import run_driver


def test_a_turn_is_queued_and_applied_to_the_next_tick_only():
    report = run_driver(
        """
        const { SnakeGame } = await import(`DOMAIN_ROOT_PLACEHOLDER/snake.ts`);
        const game = new SnakeGame(24, 18);
        const initialHeading = game.heading();
        const initialHead = game.body()[0];
        const beforeTick = game.body()[0];
        game.turn("down");
        const headingWhileQueued = game.heading();
        const status = game.tick();
        const afterFirstTick = game.body()[0];
        game.turn("left");
        game.tick();
        const afterSecondTick = game.body()[0];
        console.log(JSON.stringify({
            initialHeading, initialHead, beforeTick,
            headingWhileQueued, status, afterFirstTick, afterSecondTick,
            headingAfterFirstTick: game.heading()
        }));
        """
    )

    assert report["initialHeading"] == "right"
    assert report["headingWhileQueued"] == "right"
    assert report["afterFirstTick"]["y"] == report["beforeTick"]["y"] + 1
    assert report["afterFirstTick"]["x"] == report["beforeTick"]["x"]
    assert report["headingAfterFirstTick"] == "down"
    assert report["afterSecondTick"]["x"] == report["afterFirstTick"]["x"] - 1
    assert report["afterSecondTick"]["y"] == report["afterFirstTick"]["y"]
    assert report["status"] == "playing"


def test_self_collision_ends_the_round():
    report = run_driver(
        """
        const { SnakeGame } = await import(`DOMAIN_ROOT_PLACEHOLDER/snake.ts`);
        const snake = [
            { x: 10, y: 6 }, { x: 9, y: 6 }, { x: 8, y: 6 }, { x: 7, y: 6 },
            { x: 6, y: 6 }, { x: 5, y: 6 }, { x: 4, y: 6 }
        ];
        const game = new SnakeGame(24, 18, { snake: snake, heading: "right" });
        game.turn("down");
        const first = game.tick();
        game.turn("left");
        game.tick();
        game.turn("up");
        const finalStatus = game.tick();
        console.log(JSON.stringify({ first: first, finalStatus: finalStatus }));
        """
    )

    assert report["first"] == "playing"
    assert report["finalStatus"] == "over"
