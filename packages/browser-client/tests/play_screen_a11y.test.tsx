import { afterEach, describe, expect, it } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
import "@testing-library/jest-dom/vitest";
import { PlayScreen } from "../src/ui/PlayScreen.tsx";

expect.extend(toHaveNoViolations);

describe("the play screen", () => {
  afterEach(cleanup);

  it("passes the automated accessibility check with zero violations", async () => {
    const { container } = render(<PlayScreen />);

    const results = await axe(container);

    expect(results).toHaveNoViolations();
  });

  it("exposes a named board and a live score region", () => {
    render(<PlayScreen />);

    const board = screen.getByLabelText(/Snake play board/);
    expect(board.tagName).toBe("CANVAS");
    expect(screen.getByText(/Score:/)).toHaveAttribute("aria-live");
  });
});
