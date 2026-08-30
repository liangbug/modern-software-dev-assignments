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

  it("refetches with the completed filter when toggling filter buttons", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse([
          { id: 1, description: "Ship it", completed: false },
          { id: 2, description: "Done thing", completed: true },
        ])
      )
      .mockImplementationOnce(() =>
        jsonResponse([{ id: 2, description: "Done thing", completed: true }])
      );

    render(<ActionItemsSection />);
    await screen.findByText(/Ship it \[open\]/);

    await user.click(screen.getByRole("button", { name: "已完成" }));

    await waitFor(() => {
      expect(screen.queryByText(/Ship it/)).not.toBeInTheDocument();
    });
    expect(await screen.findByText(/Done thing \[done\]/)).toBeInTheDocument();

    const lastCallUrl = global.fetch.mock.calls[1][0];
    expect(lastCallUrl).toBe("/action-items/?completed=true");
  });

  it("bulk-completes selected action items", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse([
          { id: 1, description: "Ship it", completed: false },
          { id: 2, description: "Write docs", completed: false },
        ])
      )
      .mockImplementationOnce(() =>
        jsonResponse([
          { id: 1, description: "Ship it", completed: true },
          { id: 2, description: "Write docs", completed: true },
        ])
      )
      .mockImplementationOnce(() =>
        jsonResponse([
          { id: 1, description: "Ship it", completed: true },
          { id: 2, description: "Write docs", completed: true },
        ])
      );

    render(<ActionItemsSection />);
    await screen.findByText(/Ship it \[open\]/);

    await user.click(screen.getByRole("checkbox", { name: "Select Ship it" }));
    await user.click(screen.getByRole("checkbox", { name: "Select Write docs" }));
    await user.click(screen.getByRole("button", { name: "Complete Selected" }));

    expect(await screen.findByText(/Ship it \[done\]/)).toBeInTheDocument();
    expect(await screen.findByText(/Write docs \[done\]/)).toBeInTheDocument();

    const bulkCall = global.fetch.mock.calls[1];
    expect(bulkCall[0]).toBe("/action-items/bulk-complete");
    expect(JSON.parse(bulkCall[1].body)).toEqual({ ids: [1, 2] });
  });

  it("shows an error and does not clear selection when bulk-complete fails", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse([{ id: 1, description: "Ship it", completed: false }])
      )
      .mockImplementationOnce(() =>
        jsonResponse({ detail: "Action item(s) not found: [999]" }, 404)
      );

    render(<ActionItemsSection />);
    await screen.findByText(/Ship it \[open\]/);

    await user.click(screen.getByRole("checkbox", { name: "Select Ship it" }));
    await user.click(screen.getByRole("button", { name: "Complete Selected" }));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
