import type { Direction } from "./direction.ts";

export interface Point {
  x: number;
  y: number;
}

/** Pinned above the 44px touch-target comfort floor (AC2). */
export const SWIPE_MIN_DISTANCE = 48;

export function recognizeSwipe(points: readonly Point[]): Direction | null {
  const start = points[0];
  const end = points[points.length - 1];
  if (start === undefined || end === undefined) {
    return null;
  }

  const deltaX = end.x - start.x;
  const deltaY = end.y - start.y;
  if (Math.abs(deltaX) === Math.abs(deltaY)) {
    return null;
  }
  const dominant = Math.max(Math.abs(deltaX), Math.abs(deltaY));
  if (dominant < SWIPE_MIN_DISTANCE) {
    return null;
  }
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    return deltaX > 0 ? "right" : "left";
  }
  return deltaY > 0 ? "down" : "up";
}
