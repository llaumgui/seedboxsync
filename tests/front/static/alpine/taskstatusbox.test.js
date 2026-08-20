import { beforeEach, describe, expect, it, vi } from "vitest";

const { toast } = vi.hoisted(() => ({ toast: vi.fn() }));
vi.mock("bulma-toast", () => ({ toast }));

import { TaskStatusBoxComponent } from "@seedboxsync/alpine/taskstatusbox.js";

describe("TaskStatusBoxComponent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    globalThis.Translations = {
      never_launched: "Never launched",
      in_progress_since: "In progress since",
      completed_since: "Completed since",
      error_loading_lock_status: "Unable to load",
      task_scheduled: "Scheduled",
      task_not_scheduled: "Not scheduled",
    };
    globalThis.dateTimeOption = {};
    globalThis.window = { addEventListener: vi.fn() };
  });

  it("loads never-launched, running, and finished states", async () => {
    const component = TaskStatusBoxComponent("/info", "/launch", "Sync");
    fetch.mockResolvedValueOnce({ status: 404 });
    await component.loadTaskStatus();
    expect(component.taskStatusMessage).toBe("Never launched");

    fetch.mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ data: { running: true, started: "2025-01-01T00:00:00Z" } }) });
    await component.loadTaskStatus();
    expect(component.taskStatusMessage).toContain("In progress since");

    fetch.mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ data: { running: false, finished: "2025-01-02T00:00:00Z" } }) });
    await component.loadTaskStatus();
    expect(component.taskStatusMessage).toContain("Completed since");
    expect(toast).toHaveBeenCalledWith(expect.objectContaining({ type: "is-info" }));
  });

  it("reports status errors and task launch outcomes", async () => {
    const component = TaskStatusBoxComponent("/info", "/launch", "Sync");
    fetch.mockResolvedValueOnce({ ok: false, status: 500 });
    await component.loadTaskStatus();
    expect(component.error).toBe("Unable to load");

    fetch.mockResolvedValueOnce({ status: 202 });
    await component.taskLaunch();
    expect(fetch).toHaveBeenLastCalledWith("/launch", { method: "POST" });
    expect(toast).toHaveBeenLastCalledWith(expect.objectContaining({ type: "is-success" }));
    expect(component.tasking).toBe(false);

    fetch.mockResolvedValueOnce({ status: 500 });
    await component.taskLaunch();
    expect(toast).toHaveBeenLastCalledWith(expect.objectContaining({ type: "is-danger" }));
  });

  it("handles a network failure while launching", async () => {
    const component = TaskStatusBoxComponent("/info", "/launch", "Sync");
    fetch.mockRejectedValue(new Error("network"));

    await component.taskLaunch();

    expect(component.tasking).toBe(false);
    expect(toast).not.toHaveBeenCalled();
  });

  it("loads immediately and registers periodic refresh", async () => {
    vi.useFakeTimers();
    fetch.mockResolvedValue({ status: 404 });
    const component = TaskStatusBoxComponent("/info", "/launch", "Sync", 1000);
    const load = vi.spyOn(component, "loadTaskStatus");

    await component.init();

    expect(load).toHaveBeenCalledOnce();
    expect(window.addEventListener).toHaveBeenCalledWith("force-refresh", expect.any(Function));
    vi.advanceTimersByTime(1000);
    expect(load).toHaveBeenCalledTimes(2);
    vi.useRealTimers();
  });
});