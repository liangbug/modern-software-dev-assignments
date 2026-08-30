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

// Builds a fetch mock that serves `/tags` requests from a fixed list (default
// empty) while dispatching every other request sequentially from `queue`.
function mockFetch(queue, tags = []) {
  return vi.fn((url) => {
    if (typeof url === "string" && url.startsWith("/tags")) {
      return jsonResponse(tags);
    }
    const next = queue.shift();
    return next ? next() : jsonResponse({ items: [], total: 0, page: 1, page_size: 10 });
  });
}

describe("NotesSection", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders notes fetched from the search API", async () => {
    global.fetch = mockFetch([
      () =>
        jsonResponse({
          items: [{ id: 1, title: "Hello", content: "World" }],
          total: 1,
          page: 1,
          page_size: 10,
        }),
    ]);

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
    global.fetch = mockFetch([
      () => jsonResponse({ items: [], total: 0, page: 1, page_size: 10 }),
      () => jsonResponse({ id: 2, title: "New", content: "Note", tags: [] }, 201),
      () =>
        jsonResponse({
          items: [{ id: 2, title: "New", content: "Note", tags: [] }],
          total: 1,
          page: 1,
          page_size: 10,
        }),
    ]);

    render(<NotesSection />);
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/notes/search/?page=1&page_size=10&sort=created_desc",
        undefined
      )
    );

    await user.type(screen.getByLabelText("Note title"), "New");
    await user.type(screen.getByLabelText("Note content"), "Note");
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByText(/New: Note/)).toBeInTheDocument();
  });

  it("searches notes by keyword and disables pagination at bounds", async () => {
    const user = userEvent.setup();
    global.fetch = mockFetch([
      () => jsonResponse({ items: [], total: 0, page: 1, page_size: 10 }),
      () =>
        jsonResponse({
          items: [{ id: 3, title: "Alpha", content: "Match" }],
          total: 1,
          page: 1,
          page_size: 10,
        }),
    ]);

    render(<NotesSection />);
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/notes/search/?page=1&page_size=10&sort=created_desc",
        undefined
      )
    );

    await user.type(screen.getByLabelText("Search notes"), "alpha");
    await user.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/notes/search/?q=alpha&page=1&page_size=10&sort=created_desc",
        undefined
      )
    );
    expect(await screen.findByText(/Alpha: Match/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "上一頁" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "下一頁" })).toBeDisabled();
  });

  it("filters notes by the selected tag", async () => {
    const user = userEvent.setup();
    global.fetch = mockFetch(
      [
        () =>
          jsonResponse({
            items: [{ id: 1, title: "Hello", content: "World #work", tags: [{ id: 9, name: "work" }] }],
            total: 1,
            page: 1,
            page_size: 10,
          }),
        () =>
          jsonResponse({
            items: [{ id: 1, title: "Hello", content: "World #work", tags: [{ id: 9, name: "work" }] }],
            total: 1,
            page: 1,
            page_size: 10,
          }),
      ],
      [{ id: 9, name: "work" }]
    );

    render(<NotesSection />);
    expect(await screen.findByText(/Hello: World #work/)).toBeInTheDocument();
    expect(document.querySelector(".tag-chip").textContent).toBe("work");

    await user.selectOptions(screen.getByLabelText("Filter by tag"), "work");

    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/notes/search/?tag=work&page=1&page_size=10&sort=created_desc",
        undefined
      )
    );
  });

  it("optimistically removes a note on delete and rolls back on failure", async () => {
    const user = userEvent.setup();
    global.fetch = mockFetch([
      () =>
        jsonResponse({
          items: [{ id: 1, title: "Hello", content: "World" }],
          total: 1,
          page: 1,
          page_size: 10,
        }),
      () =>
        Promise.resolve({
          ok: false,
          status: 404,
          json: () => Promise.resolve({ detail: "Note not found" }),
          text: () => Promise.resolve("Note not found"),
        }),
    ]);

    render(<NotesSection />);
    expect(await screen.findByText(/Hello: World/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Delete" }));

    // Rolled back to showing the note again after the failed request.
    expect(await screen.findByText(/Hello: World/)).toBeInTheDocument();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("optimistically updates a note on edit and rolls back on failure", async () => {
    const user = userEvent.setup();
    global.fetch = mockFetch([
      () =>
        jsonResponse({
          items: [{ id: 1, title: "Hello", content: "World" }],
          total: 1,
          page: 1,
          page_size: 10,
        }),
      () =>
        Promise.resolve({
          ok: false,
          status: 422,
          json: () => Promise.resolve({ detail: "Invalid" }),
          text: () => Promise.resolve("Invalid"),
        }),
    ]);

    render(<NotesSection />);
    expect(await screen.findByText(/Hello: World/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Edit" }));
    const titleInput = screen.getByLabelText("Edit title 1");
    await user.clear(titleInput);
    await user.type(titleInput, "Updated");
    await user.click(screen.getByRole("button", { name: "Save" }));

    // Rolled back to the original note after the failed request.
    expect(await screen.findByText(/Hello: World/)).toBeInTheDocument();
    expect(screen.queryByText(/Updated: World/)).not.toBeInTheDocument();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
