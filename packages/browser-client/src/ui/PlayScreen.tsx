import { useEffect, useRef, useState } from "react";
import type { Direction } from "../domain/direction.ts";
import { SnakeGame } from "../domain/snake.ts";
import { SteeringAuthority } from "../domain/steering.ts";
import { attachKeyboardSteering } from "../adapters/keyboard_input.ts";
import { attachSwipeSteering } from "../adapters/touch_input.ts";
import { paletteFrom, renderBoard } from "../adapters/board_render.ts";

const BOARD_COLUMNS = 24;
const BOARD_ROWS = 18;
const CANVAS_WIDTH = 480;
const CANVAS_HEIGHT = 360;
const TICK_MS = 140;

interface Snapshot {
  score: number;
  status: string;
}

const initialGame = () => new SnakeGame(BOARD_COLUMNS, BOARD_ROWS);

const readSnapshot = (game: SnakeGame): Snapshot => ({
  score: game.score(),
  status: game.status(),
});

export function PlayScreen() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const gameRef = useRef<SnakeGame | null>(null);
  const [snapshot, setSnapshot] = useState<Snapshot>(() =>
    readSnapshot(gameRef.current ?? initialGame()),
  );

  useEffect(() => {
    gameRef.current = initialGame();
    const canvas = canvasRef.current;
    if (canvas === null) {
      return;
    }

    const steer = (direction: Direction) => {
      const game = gameRef.current;
      if (game === null) {
        return;
      }
      const authority = new SteeringAuthority(game.heading());
      if (authority.accept(direction)) {
        game.turn(authority.queued() as Direction);
      }
    };

    const detachSwipe = attachSwipeSteering(canvas, steer);
    const detachKeys = attachKeyboardSteering(window, steer);
    const ticker = window.setInterval(() => {
      const game = gameRef.current;
      if (game === null) {
        return;
      }
      game.tick();
      renderBoard(canvas, game, paletteFrom(canvas));
      setSnapshot(readSnapshot(game));
    }, TICK_MS);

    return () => {
      detachSwipe();
      detachKeys();
      window.clearInterval(ticker);
    };
  }, []);

  const restart = () => {
    gameRef.current = initialGame();
    setSnapshot(readSnapshot(gameRef.current));
  };

  return (
    <main className="flex min-h-screen flex-col items-center gap-4 p-4">
      <h1 className="text-2xl font-bold">Snake</h1>
      <p className="play-score text-lg" aria-live="polite">
        Score: {snapshot.score}
      </p>
      {snapshot.status === "over" && (
        <p className="play-score font-semibold" role="status">
          Round over — restart to play again.
        </p>
      )}
      <canvas
        ref={canvasRef}
        className="play-board"
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
        aria-label="Snake play board — swipe or use arrow keys to steer"
      />
      <button
        type="button"
        className="play-restart"
        onClick={restart}
      >
        Restart
      </button>
    </main>
  );
}
