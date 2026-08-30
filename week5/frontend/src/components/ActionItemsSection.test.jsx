import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ActionItemsSection from "./ActionItemsSection.jsx";

function jsonResponse(body, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  });
}

describe("ActionItemsSection", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders action items fetched from the API", async () => {
    global.fetch = vi.fn(() =>
      jsonResponse([{ id: 1, description: "Ship it", completed: false }])
    );

    render(<ActionItemsSection />);

    expect(await screen.findByText(/Ship it \[open\]/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Complete" })).toBeInTheDocument();
  });

  it("marks an action item as complete", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse([{ id: 1, description: "Ship it", completed: false }])
      )
      .mockImplementationOnce(() =>
        jsonResponse({ id: 1, description: "Ship it", completed: true })
      )
      .mockImplementationOnce(() =>
        jsonResponse([{ id: 1, description: "Ship it", completed: true }])
      );

    render(<ActionItemsSection />);
    await screen.findByText(/Ship it \[open\]/);

    await user.click(screen.getByRole("button", { name: "Complete" }));

    expect(await screen.findByText(/Ship it \[done\]/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Complete" })).not.toBeInTheDocument();
  });
});
