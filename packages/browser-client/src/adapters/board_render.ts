import type { Cell } from "../domain/snake.ts";

export interface BoardView {
  readonly columns: number;
  readonly rows: number;
  body(): Cell[];
  food(): Cell | null;
}

export interface BoardPalette {
  background: string;
  stroke: string;
  snake: string;
  food: string;
}

/** Reads the tokens the styles file declares so render and CSS stay one source. */
export function paletteFrom(element: HTMLElement): BoardPalette {
  const style = getComputedStyle(element);
  return {
    background: style.getPropertyValue("--bg-board").trim(),
    stroke: style.getPropertyValue("--stroke-board").trim(),
    snake: style.getPropertyValue("--fg-board").trim(),
    food: style.getPropertyValue("--fg-food").trim(),
  };
}

export function renderBoard(
  canvas: HTMLCanvasElement,
  board: BoardView,
  palette: BoardPalette,
): void {
  const context = canvas.getContext("2d");
  if (context === null) {
    return;
  }
  const cellSize = canvas.width / board.columns;

  context.fillStyle = palette.background;
  context.fillRect(0, 0, canvas.width, canvas.height);
  drawGrid(canvas, board, cellSize, context, palette.stroke);
  drawCell(board.food(), cellSize, context, palette.food);
  for (const part of board.body()) {
    drawCell(part, cellSize, context, palette.snake);
  }
}

function drawGrid(
  canvas: HTMLCanvasElement,
  board: BoardView,
  cellSize: number,
  context: CanvasRenderingContext2D,
  color: string,
): void {
  context.strokeStyle = color;
  context.lineWidth = 1;
  context.beginPath();
  for (let x = 0; x <= board.columns; x += 1) {
    context.moveTo(x * cellSize, 0);
    context.lineTo(x * cellSize, canvas.height);
  }
  for (let y = 0; y <= board.rows; y += 1) {
    context.moveTo(0, y * cellSize);
    context.lineTo(canvas.width, y * cellSize);
  }
  context.stroke();
}

function drawCell(
  cell: Cell | null,
  cellSize: number,
  context: CanvasRenderingContext2D,
  color: string,
): void {
  if (cell === null) {
    return;
  }
  context.fillStyle = color;
  context.fillRect(cell.x * cellSize, cell.y * cellSize, cellSize, cellSize);
}
