import { recognizeSwipe, type Point } from "../domain/gesture.ts";
import type { Direction } from "../domain/direction.ts";

/**
 * Pointer events feed the swipe recognizer; one recognized gesture fires one
 * turn. `touch-action: none` on the surface keeps the browser's own scroll
 * and pull-to-refresh gestures from eating the swipe on a phone.
 */
export function attachSwipeSteering(
  surface: HTMLElement,
  onSwipe: (direction: Direction) => void,
): () => void {
  surface.style.touchAction = "none";
  let strokeStart: Point | null = null;

  const beginStroke = (event: PointerEvent) => {
    strokeStart = { x: event.clientX, y: event.clientY };
  };

  const trackStroke = (event: PointerEvent) => {
    if (strokeStart === null) {
      return;
    }
    const recognized = recognizeSwipe([
      strokeStart,
      { x: event.clientX, y: event.clientY },
    ]);
    if (recognized !== null) {
      strokeStart = { x: event.clientX, y: event.clientY };
      onSwipe(recognized);
    }
  };

  const endStroke = () => {
    strokeStart = null;
  };

  surface.addEventListener("pointerdown", beginStroke);
  surface.addEventListener("pointermove", trackStroke);
  surface.addEventListener("pointerup", endStroke);
  surface.addEventListener("pointercancel", endStroke);
  return () => {
    surface.removeEventListener("pointerdown", beginStroke);
    surface.removeEventListener("pointermove", trackStroke);
    surface.removeEventListener("pointerup", endStroke);
    surface.removeEventListener("pointercancel", endStroke);
  };
}
