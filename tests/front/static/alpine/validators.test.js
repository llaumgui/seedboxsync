import { describe, expect, it } from "vitest";
import {
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
    expect(isValidHost("seedbox.example.com")).toBe(true);
    expect(isValidHost("192.168.1.10")).toBe(true);
    expect(isValidHost("256.168.1.10")).toBe(false);
    expect(isValidHost("-seedbox.example.com")).toBe(false);
  });

  it("validates numeric settings at their boundaries", () => {
    expect(isValidPort(1)).toBe(true);
    expect(isValidPort(65535)).toBe(true);
    expect(isValidPort(0)).toBe(false);
    expect(isValidPort(65536)).toBe(false);
    expect(isValidMaxConcPrefetchReq(1024)).toBe(true);
    expect(isValidMaxConcPrefetchReq(1025)).toBe(false);
    expect(isValidTimeout(100000)).toBe(true);
    expect(isValidTimeout(100001)).toBe(false);
  });

  it("checks required values, chmod values, and enabled URLs", () => {
    expect(isRequired("value")).toBe(true);
    expect(isRequired("  ")).toBe(false);
    expect(isRequired(null)).toBe(false);
    expect(isOctalChmod("0755")).toBe(false);
    expect(isOctalChmod("0o755")).toBe(true);
    expect(isOctalChmod("0899")).toBe(false);
    expect(isOctalChmod("0o899")).toBe(false);
    expect(isOctalChmod(755)).toBe(false);
    expect(isOctalChmod(" 0o755 ")).toBe(true);
    expect(isValidUrl("not a url", false)).toBe(true);
    expect(isValidUrl("https://example.com", true)).toBe(true);
    expect(isValidUrl("not a url", true)).toBe(false);
  });
});