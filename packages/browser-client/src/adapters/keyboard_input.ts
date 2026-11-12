import type { Direction } from "../domain/direction.ts";

const KEY_DIRECTIONS: ReadonlyMap<string, Direction> = new Map([
  ["ArrowUp", "up"],
  ["ArrowDown", "down"],
  ["ArrowLeft", "left"],
  ["ArrowRight", "right"],
  ["w", "up"],
  ["s", "down"],
  ["a", "left"],
  ["d", "right"],
]);

export function keyToDirection(key: string): Direction | null {
  if (KEY_DIRECTIONS.has(key)) {
    return KEY_DIRECTIONS.get(key)!;
  }
  if (key.length === 1) {
    return KEY_DIRECTIONS.get(key.toLowerCase()) ?? null;
  }
  return null;
}

export function attachKeyboardSteering(
  target: HTMLElement | Window,
  onTurn: (direction: Direction) => void,
): () => void {
  const handleKey = (event: Event) => {
    const keyEvent = event as KeyboardEvent;
    const direction = keyToDirection(keyEvent.key);
    if (direction === null) {
      return;
    }
    keyEvent.preventDefault();
    onTurn(direction);
  };
  target.addEventListener("keydown", handleKey);
  return () => target.removeEventListener("keydown", handleKey);
}
