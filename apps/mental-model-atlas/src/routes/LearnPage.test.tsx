import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import LearnPage from "./LearnPage";

afterEach(cleanup);

describe("unavailable learning route", () => {
  it("sets an honest visitor boundary without exposing internal project gates", () => {
    render(<LearnPage />);
    expect(screen.getByRole("heading", { name: /guided learning is being prepared/i })).toBeTruthy();
    expect(screen.queryByText(/truth gate/i)).toBeNull();
    expect(screen.queryByText(/phase 1/i)).toBeNull();
    expect(screen.queryByText(/projection/i)).toBeNull();
  });
});
