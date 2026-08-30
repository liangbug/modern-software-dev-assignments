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
      jsonResponse({ items: [{ id: 1, description: "Ship it", completed: false }], total: 1 })
    );

    render(<ActionItemsSection />);

    expect(await screen.findByText(/Ship it \[open\]/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Complete" })).toBeInTheDocument();
    expect(screen.getByText(/共 1 筆結果，第 1 \/ 1 頁/)).toBeInTheDocument();
  });

  it("marks an action item as complete", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse({ items: [{ id: 1, description: "Ship it", completed: false }], total: 1 })
      )
      .mockImplementationOnce(() =>
        jsonResponse({ id: 1, description: "Ship it", completed: true })
      )
      .mockImplementationOnce(() =>
        jsonResponse({ items: [{ id: 1, description: "Ship it", completed: true }], total: 1 })
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
        jsonResponse({
          items: [
            { id: 1, description: "Ship it", completed: false },
            { id: 2, description: "Done thing", completed: true },
          ],
          total: 2,
        })
      )
      .mockImplementationOnce(() =>
        jsonResponse({ items: [{ id: 2, description: "Done thing", completed: true }], total: 1 })
      );

    render(<ActionItemsSection />);
    await screen.findByText(/Ship it \[open\]/);

    await user.click(screen.getByRole("button", { name: "已完成" }));

    await waitFor(() => {
      expect(screen.queryByText(/Ship it/)).not.toBeInTheDocument();
    });
    expect(await screen.findByText(/Done thing \[done\]/)).toBeInTheDocument();

    const lastCallUrl = global.fetch.mock.calls[1][0];
    expect(lastCallUrl).toBe("/action-items/?completed=true&page=1&page_size=10");
  });

  it("bulk-completes selected action items", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse({
          items: [
            { id: 1, description: "Ship it", completed: false },
            { id: 2, description: "Write docs", completed: false },
          ],
          total: 2,
        })
      )
      .mockImplementationOnce(() =>
        jsonResponse([
          { id: 1, description: "Ship it", completed: true },
          { id: 2, description: "Write docs", completed: true },
        ])
      )
      .mockImplementationOnce(() =>
        jsonResponse({
          items: [
            { id: 1, description: "Ship it", completed: true },
            { id: 2, description: "Write docs", completed: true },
          ],
          total: 2,
        })
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
        jsonResponse({ items: [{ id: 1, description: "Ship it", completed: false }], total: 1 })
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

  it("paginates action items with prev/next controls", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse({
          items: Array.from({ length: 10 }, (_, i) => ({
            id: i + 1,
            description: `Task ${i + 1}`,
            completed: false,
          })),
          total: 15,
        })
      )
      .mockImplementationOnce(() =>
        jsonResponse({
          items: Array.from({ length: 5 }, (_, i) => ({
            id: i + 11,
            description: `Task ${i + 11}`,
            completed: false,
          })),
          total: 15,
        })
      );

    render(<ActionItemsSection />);
    await screen.findByText(/Task 1 \[open\]/);
    expect(screen.getByText(/共 15 筆結果，第 1 \/ 2 頁/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "上一頁" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "下一頁" })).not.toBeDisabled();

    await user.click(screen.getByRole("button", { name: "下一頁" }));

    expect(await screen.findByText(/Task 11 \[open\]/)).toBeInTheDocument();
    expect(screen.getByText(/共 15 筆結果，第 2 \/ 2 頁/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "下一頁" })).toBeDisabled();

    const lastCallUrl = global.fetch.mock.calls[1][0];
    expect(lastCallUrl).toBe("/action-items/?page=2&page_size=10");
  });
});
