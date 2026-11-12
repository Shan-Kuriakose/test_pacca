import { OPPOSITE, stepFor, type Direction } from "./direction.ts";

export interface Cell {
  x: number;
  y: number;
}

export type RoundStatus = "playing" | "over";

export interface SnakeGameOptions {
  snake?: readonly Cell[];
  heading?: Direction;
  food?: Cell | null;
}

const DEFAULT_COLUMNS = 24;
const DEFAULT_ROWS = 18;

export class SnakeGame {
  readonly columns: number;
  readonly rows: number;
  private segments: Cell[];
  private facing: Direction;
  private queuedTurn: Direction | null = null;
  private foodCell: Cell | null;
  private points = 0;
  private roundStatus: RoundStatus = "playing";

  constructor(
    columns: number = DEFAULT_COLUMNS,
    rows: number = DEFAULT_ROWS,
    options: SnakeGameOptions = {},
  ) {
    this.columns = columns;
    this.rows = rows;
    this.segments = [...(options.snake ?? defaultSnake())];
    this.facing = options.heading ?? "right";
    this.foodCell = options.food === undefined ? this.nextFoodCell() : options.food;
  }

  heading(): Direction {
    return this.facing;
  }

  body(): Cell[] {
    return [...this.segments];
  }

  score(): number {
    return this.points;
  }

  status(): RoundStatus {
    return this.roundStatus;
  }

  food(): Cell | null {
    return this.foodCell === null ? null : { ...this.foodCell };
  }

  turn(direction: Direction): void {
    if (this.roundStatus !== "playing") {
      return;
    }
    const effective = this.queuedTurn ?? this.facing;
    if (direction === OPPOSITE[effective]) {
      return;
    }
    this.queuedTurn = direction;
  }

  tick(): RoundStatus {
    if (this.roundStatus !== "playing") {
      return this.roundStatus;
    }
    if (this.queuedTurn !== null) {
      this.facing = this.queuedTurn;
      this.queuedTurn = null;
    }

    const head = this.segments[0];
    const step = stepFor(this.facing);
    const next: Cell = { x: head.x + step.x, y: head.y + step.y };
    const grows = this.foodCell !== null && sameCell(next, this.foodCell);

    if (this.isOutOfBounds(next) || this.hitsBody(next, grows)) {
      this.roundStatus = "over";
      return this.roundStatus;
    }

    this.segments.unshift(next);
    if (grows && this.foodCell !== null) {
      this.points += 1;
      this.foodCell = this.nextFoodCell();
    } else {
      this.segments.pop();
    }
    return this.roundStatus;
  }

  private isOutOfBounds(cell: Cell): boolean {
    return (
      cell.x < 0 || cell.y < 0 || cell.x >= this.columns || cell.y >= this.rows
    );
  }

  private hitsBody(cell: Cell, grows: boolean): boolean {
    const occupied = grows ? this.segments : this.segments.slice(0, -1);
    return occupied.some((part) => sameCell(cell, part));
  }

  private nextFoodCell(): Cell | null {
    const occupied = new Set(this.segments.map((cell) => `${cell.x},${cell.y}`));
    for (let y = 0; y < this.rows; y += 1) {
      for (let x = 0; x < this.columns; x += 1) {
        if (!occupied.has(`${x},${y}`)) {
          return { x, y };
        }
      }
    }
    return null;
  }
}

function defaultSnake(): Cell[] {
  const y = (DEFAULT_ROWS / 2) | 0;
  return [
    { x: 12, y },
    { x: 11, y },
    { x: 10, y },
  ];
}


function sameCell(left: Cell, right: Cell): boolean {
  return left.x === right.x && left.y === right.y;
}
