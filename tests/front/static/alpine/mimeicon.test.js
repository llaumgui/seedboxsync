import { describe, expect, it } from "vitest";

import { getMimeIconClass } from "@seedboxsync/alpine/mimeicon.js";

describe("getMimeIconClass", () => {
  it("returns icons for the main MIME types", () => {
    expect(getMimeIconClass("video/mp4")).toBe("cursor-pointer fa-solid fa-video text-blue");
    expect(getMimeIconClass("image/png")).toBe("cursor-pointer fa-solid fa-image text-purple");
    expect(getMimeIconClass("audio/mpeg")).toBe("cursor-pointer fa-solid fa-music text-red");
    expect(getMimeIconClass("text/plain")).toBe("cursor-pointer fa-solid fa-file-lines text-orange");
    expect(getMimeIconClass("application/x-bittorrent")).toBe("fa-solid fa-download text-grey");
  });

  it("returns specific icons for supported application types", () => {
    expect(getMimeIconClass("application/pdf")).toBe("cursor-pointer fa-solid fa-file-pdf text-green");
    expect(getMimeIconClass("application/zip")).toBe("cursor-pointer fa-solid fa-file-zipper text-warning");
    expect(getMimeIconClass("application/x-7z-compressed")).toBe("cursor-pointer fa-solid fa-file-zipper text-warning");
    expect(getMimeIconClass("application/x-rar-compressed")).toBe("cursor-pointer fa-solid fa-file-zipper text-warning");
    expect(getMimeIconClass("application/x-tar")).toBe("cursor-pointer fa-solid fa-file-zipper text-warning");
    expect(getMimeIconClass("application/json")).toBe("cursor-pointer fa-solid fa-file-code text-secondary");
    expect(getMimeIconClass("application/xml")).toBe("cursor-pointer fa-solid fa-file-code text-secondary");
  });

  it("uses the default file icon for missing or unknown MIME types", () => {
    expect(getMimeIconClass()).toBe("cursor-pointer fa-solid fa-file text-grey");
    expect(getMimeIconClass("")).toBe("cursor-pointer fa-solid fa-file text-grey");
    expect(getMimeIconClass("application/octet-stream")).toBe("cursor-pointer fa-solid fa-file text-grey");
    expect(getMimeIconClass("application/unknown")).toBe("cursor-pointer fa-solid fa-file text-grey");
  });
});