import { beforeEach, describe, expect, it, vi } from "vitest";

const { modalInstance } = vi.hoisted(() => ({
  modalInstance: { show: vi.fn(), hide: vi.fn() },
}));
vi.mock("bootstrap", () => ({
  Modal: { getOrCreateInstance: vi.fn(() => modalInstance) },
}));

import { ModalConfirmCallComponent, OpenModalConfirmCall } from "@seedboxsync/alpine/modal.js";

describe("modal components", () => {
  function createModal() {
    const modal = ModalConfirmCallComponent();
    modal.modal = modalInstance;
    return modal;
  }

  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    globalThis.window = { dispatchEvent: vi.fn() };
    globalThis.CustomEvent = class CustomEvent {
      constructor(type, init = {}) {
        this.type = type;
        this.detail = init.detail;
      }
    };
  });

  it("opens and closes with the provided modal values", () => {
    const modal = createModal();
    modal.open("Title", "Content", "/api", "DELETE", "Done");
    expect(modal).toMatchObject({
      title: "Title",
      content: "Content",
      apiUrl: "/api",
      apiMethod: "DELETE",
      toastMessage: "Done",
    });
    modal.close();
    expect(modal).toMatchObject({ loading: false, error: false });
  });

  it("closes without calling the API when no URL is provided", async () => {
    const modal = createModal();
    await modal.confirm();
    expect(fetch).not.toHaveBeenCalled();
    expect(modal.modal.hide).toHaveBeenCalled();
  });

  it("confirms successful calls and refreshes the page", async () => {
    fetch.mockResolvedValue({ ok: true });
    const modal = createModal();
    modal.open("Title", "Content", "/api", "POST", "Done");

    await modal.confirm();

    expect(fetch).toHaveBeenCalledWith("/api", { method: "POST" });
    expect(window.dispatchEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "show-toast",
        detail: { message: "Done", type: "success" },
      }),
    );
    expect(window.dispatchEvent).toHaveBeenCalledWith(expect.objectContaining({ type: "force-refresh" }));
    expect(modal.modal.hide).toHaveBeenCalled();
  });

  it("marks failed calls and displays the error", async () => {
    fetch.mockResolvedValue({ ok: false });
    const modal = createModal();
    modal.open("Title", "Content", "/api");

    await modal.confirm();

    expect(modal.error).toBe(true);
    expect(window.dispatchEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        type: "show-toast",
        detail: { message: "API call failed", type: "danger" },
      }),
    );
    expect(modal.loading).toBe(false);
  });

  it("opens the Alpine modal from the document", () => {
    const open = vi.fn();
    globalThis.document = { querySelector: vi.fn(() => ({ __modal: { open } })) };

    OpenModalConfirmCall("/api", "PUT", "Title", "Content", "Done");

    expect(open).toHaveBeenCalledWith("Title", "Content", "/api", "PUT", "Done");
  });
});