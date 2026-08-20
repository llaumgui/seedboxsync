import { beforeEach, describe, expect, it, vi } from "vitest";

const { toast } = vi.hoisted(() => ({ toast: vi.fn() }));
vi.mock("bulma-toast", () => ({ toast }));

import { ModalConfirmCallComponent, OpenModalConfirmCall } from "@seedboxsync/alpine/modal.js";

describe("modal components", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    globalThis.window = { dispatchEvent: vi.fn() };
    globalThis.CustomEvent = class CustomEvent {
      constructor(type) {
        this.type = type;
      }
    };
  });

  it("opens and closes with the provided modal values", () => {
    const modal = ModalConfirmCallComponent();
    modal.open("Title", "Content", "/api", "DELETE", "Done");
    expect(modal).toMatchObject({
      title: "Title",
      content: "Content",
      apiUrl: "/api",
      apiMethod: "DELETE",
      toastMessage: "Done",
      isActive: true,
    });
    modal.close();
    expect(modal).toMatchObject({ isActive: false, loading: false, error: false });
  });

  it("closes without calling the API when no URL is provided", async () => {
    const modal = ModalConfirmCallComponent();
    modal.isActive = true;
    await modal.confirm();
    expect(fetch).not.toHaveBeenCalled();
    expect(modal.isActive).toBe(false);
  });

  it("confirms successful calls and refreshes the page", async () => {
    fetch.mockResolvedValue({ ok: true });
    const modal = ModalConfirmCallComponent();
    modal.open("Title", "Content", "/api", "POST", "Done");

    await modal.confirm();

    expect(fetch).toHaveBeenCalledWith("/api", { method: "POST" });
    expect(toast).toHaveBeenCalledWith({ message: "Done", type: "is-success" });
    expect(window.dispatchEvent).toHaveBeenCalledWith(expect.objectContaining({ type: "force-refresh" }));
    expect(modal.isActive).toBe(false);
  });

  it("marks failed calls and displays the error", async () => {
    fetch.mockResolvedValue({ ok: false });
    const modal = ModalConfirmCallComponent();
    modal.open("Title", "Content", "/api");

    await modal.confirm();

    expect(modal.error).toBe(true);
    expect(toast).toHaveBeenCalledWith({ message: "API call failed", type: "is-danger" });
    expect(modal.loading).toBe(false);
  });

  it("opens the Alpine modal from the document", () => {
    const open = vi.fn();
    globalThis.document = { querySelector: vi.fn(() => ({ __modal: { open } })) };

    OpenModalConfirmCall("/api", "PUT", "Title", "Content", "Done");

    expect(open).toHaveBeenCalledWith("Title", "Content", "/api", "PUT", "Done");
  });
});