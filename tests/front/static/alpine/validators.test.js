import { describe, expect, it } from "vitest";
import {
  form,
  isOctalChmod,
  isRequired,
  isValidHost,
  isValidMaxConcPrefetchReq,
  isValidPort,
  isValidTimeout,
  isValidUrl,
} from "@seedboxsync/alpine/validators.js";

describe("validators", () => {
  it("accepts valid hosts and rejects malformed hosts", () => {
    expect(isValidHost(false, "")).toBe(true);
    expect(isValidHost(true, "seedbox.example.com")).toBe(true);
    expect(isValidHost(true, "192.168.1.10")).toBe(true);
    expect(isValidHost(true, "256.168.1.10")).toBe(false);
    expect(isValidHost(true, "-seedbox.example.com")).toBe(false);
  });

  it("validates numeric settings at their boundaries", () => {
    expect(isValidPort(false, 0)).toBe(true);
    expect(isValidPort(true, 1)).toBe(true);
    expect(isValidPort(true, 65535)).toBe(true);
    expect(isValidPort(true, 0)).toBe(false);
    expect(isValidPort(true, 65536)).toBe(false);
    expect(isValidMaxConcPrefetchReq(false, 0)).toBe(true);
    expect(isValidMaxConcPrefetchReq(true, 1024)).toBe(true);
    expect(isValidMaxConcPrefetchReq(true, 1025)).toBe(false);
    expect(isValidTimeout(false, 0)).toBe(true);
    expect(isValidTimeout(true, 100000)).toBe(true);
    expect(isValidTimeout(true, 100001)).toBe(false);
  });

  it("checks required values, chmod values, and enabled URLs", () => {
    expect(isRequired(false, "")).toBe(true);
    expect(isRequired(true, "value")).toBe(true);
    expect(isRequired(true, "  ")).toBe(false);
    expect(isRequired(true, null)).toBe(false);
    expect(isOctalChmod(false, "")).toBe(true);
    expect(isOctalChmod(true, "0755")).toBe(false);
    expect(isOctalChmod(true, "0o755")).toBe(true);
    expect(isOctalChmod(true, "0899")).toBe(false);
    expect(isOctalChmod(true, "0o899")).toBe(false);
    expect(isOctalChmod(true, 755)).toBe(false);
    expect(isOctalChmod(true, " 0o755 ")).toBe(true);
    expect(isValidUrl(false, "", false)).toBe(true);
    expect(isValidUrl(true, "not a url", false)).toBe(true);
    expect(isValidUrl(true, "https://example.com", true)).toBe(true);
    expect(isValidUrl(true, "not a url", true)).toBe(false);
  });

  it("tracks field state and enables submission only for touched valid fields", () => {
    const validation = form();

    expect(validation.canSubmit()).toBe(false);

    validation.setFieldState("host", true, false);
    expect(validation.canSubmit()).toBe(false);

    validation.setFieldState("port", false, true);
    expect(validation.fields).toEqual({
      host: { valid: true, touched: false },
      port: { valid: false, touched: true },
    });
    expect(validation.canSubmit()).toBe(false);

    validation.setFieldState("port", true, true);
    expect(validation.canSubmit()).toBe(true);
  });
});