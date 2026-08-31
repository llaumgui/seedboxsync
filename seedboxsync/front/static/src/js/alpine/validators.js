/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Validate if a string is a valid host (domain or IP)
 * @param {boolean} touched
 * @param {string} host
 * @returns {boolean}
 */
export function isValidHost(touched, host) {
  if (!touched) return true;
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
 * @param {boolean} touched
 * @param {int} port
 * @returns {boolean}
 */
export function isValidPort(touched, port) {
  if (!touched) return true;
  return port > 0 && port <= 65535;
}

/**
 * Validate is a valid max concurrent prefetch requests number
 * @param {boolean} touched
 * @param {int} max
 * @returns {boolean}
 */
export function isValidMaxConcPrefetchReq(touched, max) {
  if (!touched) return true;
  return max > 0 && max <= 1024;
}

/**
 * Validate is a valid port number
 * @param {boolean} touched
 * @param {int} port
 * @returns {boolean}
 */
export function isValidTimeout(touched, timeout) {
  if (!touched) return true;
  return timeout > 0 && timeout <= 100000;
}

/**
 * Check if a value is provided (non-empty string, non-null, non-undefined)
 * @param {boolean} touched
 * @param {any} value
 * @returns {boolean}
 */
export function isRequired(touched, value) {
  if (!touched) return true;
  if (value === null || value === undefined) return false;
  if (typeof value === "string") return value.trim().length > 0;
  return true;
}

/**
 * Check the lenght of the value
 * @param {boolean} touched
 * @param {string} value
 * @param {int} min
 * @param {int} max
 * @returns
 */
export function Length(touched, value, min, max) {
  if (!touched) return true;
  const str = value ? String(value) : "";

  if (min !== undefined && min !== null && str.length < min) {
    return false;
  }
  if (max !== undefined && max !== null && str.length > max) {
    return false;
  }

  return true;
}

/**
 * Validate if a string is a valid octal chmod value (e.g. 755, 0755, 0o755)
 * @param {boolean} touched
 * @param {string} value
 * @returns {boolean}
 */
export function isOctalChmod(touched, chmod) {
  if (!touched) return true;
  if (typeof chmod !== "string") return false;
  return /^0o[0-7]{3,4}$/.test(chmod.trim());
}

/**
 * Validate if a string is a valid URL
 * @param {boolean} touched
 * @param {string} value
 * @returns {boolean}
 */
export function isValidUrl(touched, url, enabled) {
  if (!touched || !enabled) return true;
  try {
    new URL(url);
    return true;
  } catch (_) { // eslint-disable-line no-unused-vars
    return false;
  }
}

/**
 * Form validation and button enabling
 * @returns
 */
export function form() {
  return {
    fields: {},

    setFieldState(field, valid, touched) {
      this.fields[field] = { valid, touched };
    },

    canSubmit() {
      const fields = Object.values(this.fields);
      return (
        fields.some((field) => field.touched) &&
        fields.every((field) => field.valid)
      );
    },
  };
}
