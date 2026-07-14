/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Validate if a string is a valid host (domain or IP)
 * @param {string} host
 * @returns {boolean}
 */
export function isValidHost(host) {
  if (!host || typeof host !== "string") return false;

  // Check for IPv4
  const ipv4 =
    /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;

  // Check for IPv6 (simplified)
  const ipv6 = /^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::1)$/;

  // Check for domain name
  const domain = /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$/;

  return ipv4.test(host) || ipv6.test(host) || domain.test(host);
}

/**
 * Validate is a valid port number
 * @param {int} port
 * @returns {boolean}
 */
export function isValidPort(port) {
  return port > 0 && port <= 65535;
}

/**
 * Validate is a valid max concurrent prefetch requests number
 * @param {int} max
 * @returns {boolean}
 */
export function isValidMaxConcPrefetchReq(max) {
  return max > 0 && max <= 1024;
}

/**
 * Validate is a valid port number
 * @param {int} port
 * @returns {boolean}
 */
export function isValidTimeout(timeout) {
  return timeout > 0 && timeout <= 100000;
}

/**
 * Check if a value is provided (non-empty string, non-null, non-undefined)
 * @param {any} value
 * @returns {boolean}
 */
export function isRequired(value) {
    if (value === null || value === undefined) return false;
    if (typeof value === "string") return value.trim().length > 0;
    return true;
}

/**
 * Validate if a string is a valid octal chmod value (e.g. 755, 0755, 0o755)
 * @param {string} value
 * @returns {boolean}
 */
export function isOctalChmod(chmod) {
    if (typeof chmod !== "string") return false;
    return /^0o[0-7]{3,4}$/.test(chmod.trim());
}

/**
 * Validate if a string is a valid URL
 * @param {string} value
 * @returns {boolean}
 */
export function isValidUrl(url, enabled) {
  if(!enabled) return true;
  try {
    new URL(url);
    return true;
  } catch (_) { // eslint-disable-line no-unused-vars
    return false;
  }
}
