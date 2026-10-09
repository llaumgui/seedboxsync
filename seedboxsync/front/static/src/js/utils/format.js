/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Format a byte count using binary units.
 *
 * @param {number} bytes - Size in bytes.
 * @returns {string} Human-readable size.
 */
function humanizeBytes(bytes) {
  if (bytes === 0) return "0 B";

  const units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"];
  const index = Math.min(
    Math.floor(Math.log(Math.abs(bytes)) / Math.log(1024)),
    units.length - 1,
  );

  return `${Number((bytes / 1024 ** index).toFixed(1))} ${units[index]}`;
}

/**
 * Format a chart axis value according to its data type.
 *
 * @param {number} value - Numeric axis value.
 * @param {string} fieldTotal - Field containing the numeric value.
 * @returns {string} Formatted axis value.
 */
export function FormatAxisValue(value, fieldTotal) {
  if (fieldTotal.endsWith("_size")) {
    return humanizeBytes(value);
  }

  return new Intl.NumberFormat(document.documentElement.lang || "en", {
    maximumFractionDigits: 0,
  }).format(value);
}
