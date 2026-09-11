import { describe, expect, it } from "vitest";

import { getMimeIconClass } from "@seedboxsync/alpine/mimeicon.js";

describe("getMimeIconClass", () => {
  it("returns icons for the main MIME types", () => {
    expect(getMimeIconClass("video/mp4")).toBe("fa-solid fa-video has-text-link");
    expect(getMimeIconClass("image/png")).toBe("fa-solid fa-image has-text-success");
    expect(getMimeIconClass("audio/mpeg")).toBe("fa-solid fa-music has-text-warning");
    expect(getMimeIconClass("text/plain")).toBe("fa-solid fa-file-lines has-text-info");
    expect(getMimeIconClass("application/x-bittorrent")).toBe("fa-solid fa-download has-text-primary");
  });

  it("returns specific icons for supported application types", () => {
    expect(getMimeIconClass("application/pdf")).toBe("fa-solid fa-file-pdf has-text-danger");
    expect(getMimeIconClass("application/zip")).toBe("fa-solid fa-file-zipper has-text-warning");
    expect(getMimeIconClass("application/x-7z-compressed")).toBe("fa-solid fa-file-zipper has-text-warning");
    expect(getMimeIconClass("application/x-rar-compressed")).toBe("fa-solid fa-file-zipper has-text-warning");
    expect(getMimeIconClass("application/x-tar")).toBe("fa-solid fa-file-zipper has-text-warning");
    expect(getMimeIconClass("application/json")).toBe("fa-solid fa-file-code has-text-link");
    expect(getMimeIconClass("application/xml")).toBe("fa-solid fa-file-code has-text-link");
  });

  it("uses the default file icon for missing or unknown MIME types", () => {
    expect(getMimeIconClass()).toBe("fa-solid fa-file has-text-grey");
    expect(getMimeIconClass("")).toBe("fa-solid fa-file has-text-grey");
    expect(getMimeIconClass("application/octet-stream")).toBe("fa-solid fa-file has-text-grey");
    expect(getMimeIconClass("application/unknown")).toBe("fa-solid fa-file has-text-grey");
  });
});