import { describe, expect, it } from "vitest";

import { FormatAxisValue } from "@seedboxsync/utils/format.js";

describe("format utils", () => {
  it("formats byte-based totals using binary units", () => {
    expect(FormatAxisValue(0, "total_size")).toBe("0 B");
    expect(FormatAxisValue(1024, "total_size")).toBe("1 KiB");
    expect(FormatAxisValue(1536, "total_size")).toBe("1.5 KiB");
  });

  it("formats numeric totals using the document locale", () => {
    const previousDocument = globalThis.document;
    globalThis.document = { documentElement: { lang: "en" } };

    try {
      expect(FormatAxisValue(1234, "total")).toBe(
        new Intl.NumberFormat("en", { maximumFractionDigits: 0 }).format(1234),
      );
    } finally {
      globalThis.document = previousDocument;
    }
  });
});
