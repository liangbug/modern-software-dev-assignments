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

  it("renders notes fetched from the API", async () => {
    global.fetch = vi.fn(() =>
      jsonResponse([{ id: 1, title: "Hello", content: "World" }])
    );

    render(<NotesSection />);

    expect(await screen.findByText(/Hello: World/)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/notes/", undefined);
  });

  it("creates a new note and refreshes the list", async () => {
    const user = userEvent.setup();
    global.fetch = vi
      .fn()
      .mockImplementationOnce(() => jsonResponse([]))
      .mockImplementationOnce(() =>
        jsonResponse({ id: 2, title: "New", content: "Note" }, 201)
      )
      .mockImplementationOnce(() =>
        jsonResponse([{ id: 2, title: "New", content: "Note" }])
      );

    render(<NotesSection />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));

    await user.type(screen.getByLabelText("Note title"), "New");
    await user.type(screen.getByLabelText("Note content"), "Note");
    await user.click(screen.getByRole("button", { name: "Add" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(3));
    expect(await screen.findByText(/New: Note/)).toBeInTheDocument();
  });
});
