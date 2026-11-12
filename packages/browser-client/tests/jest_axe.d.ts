/* Minimal declarations for jest-axe and the matcher it installs; @types/jest-axe
   is not on the project's approved dependency list. */
import "vitest";

declare module "jest-axe" {
  export interface AxeResults {
    violations: readonly {
      id: string;
      impact: string | null;
      description: string;
    }[];
    passes: readonly unknown[];
    incompletes: readonly unknown[];
    inapplicable: readonly unknown[];
  }

  export function axe(html: Element): Promise<AxeResults>;
  export function axe(html: string): Promise<AxeResults>;
  export const toHaveNoViolations: object;
}

declare module "vitest" {
  interface Assertion {
    toHaveNoViolations(): void;
  }
  interface AsymmetricAssertions {
    toHaveNoViolations(): void;
  }
}
