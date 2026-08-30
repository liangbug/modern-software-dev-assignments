import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import NotesSection from "./NotesSection.jsx";

function jsonResponse(body, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  });
}

describe("NotesSection", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders notes fetched from the search API", async () => {
    global.fetch = vi.fn(() =>
      jsonResponse({
        items: [{ id: 1, title: "Hello", content: "World" }],
        total: 1,
        page: 1,
        page_size: 10,
      })
    );

    render(<NotesSection />);

    expect(await screen.findByText(/Hello: World/)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/notes/search/?page=1&page_size=10&sort=created_desc",
      undefined
    );
    expect(screen.getByText(/共 1 筆結果/)).toBeInTheDocument();
  });

  it("creates a new note and refreshes the list", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse({ items: [], total: 0, page: 1, page_size: 10 })
      )
      .mockImplementationOnce(() =>
        jsonResponse({ id: 2, title: "New", content: "Note" }, 201)
      )
      .mockImplementationOnce(() =>
        jsonResponse({
          items: [{ id: 2, title: "New", content: "Note" }],
          total: 1,
          page: 1,
          page_size: 10,
        })
      );

    render(<NotesSection />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));

    await user.type(screen.getByLabelText("Note title"), "New");
    await user.type(screen.getByLabelText("Note content"), "Note");
    await user.click(screen.getByRole("button", { name: "Add" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(3));
    expect(await screen.findByText(/New: Note/)).toBeInTheDocument();
  });

  it("searches notes by keyword and disables pagination at bounds", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() =>
        jsonResponse({ items: [], total: 0, page: 1, page_size: 10 })
      )
      .mockImplementationOnce(() =>
        jsonResponse({
          items: [{ id: 3, title: "Alpha", content: "Match" }],
          total: 1,
          page: 1,
          page_size: 10,
        })
      );

    render(<NotesSection />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));

    await user.type(screen.getByLabelText("Search notes"), "alpha");
    await user.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(fetch).toHaveBeenLastCalledWith(
      "/notes/search/?q=alpha&page=1&page_size=10&sort=created_desc",
      undefined
    );
    expect(await screen.findByText(/Alpha: Match/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "上一頁" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "下一頁" })).toBeDisabled();
  });
});
