import { OPPOSITE, type Direction } from "./direction.ts";

/**
 * The single steering seam both input adapters feed (AC3). Within one tick
 * it queues at most one turn, the last accepted input wins, and a refusal
 * — a 180-degree reversal of the current heading — consumes nothing.
 */
export class SteeringAuthority {
  private readonly heading: Direction;
  private pendingTurn: Direction | null = null;

  constructor(heading: Direction) {
    this.heading = heading;
  }

  accept(direction: Direction | null): boolean {
    if (direction === null) {
      return false;
    }
    if (direction === OPPOSITE[this.heading]) {
      return false;
    }
    this.pendingTurn = direction;
    return true;
  }

  queued(): Direction | null {
    return this.pendingTurn;
  }
}
