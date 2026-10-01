/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Format dates as localized relative time values.
 *
 * Uses the browser locale and automatically selects the most relevant
 * time unit between days, hours, minutes, and seconds.
 */
const relativeTimeFormatter = new Intl.RelativeTimeFormat(undefined, {
  numeric: "auto",
});

/**
 * Format a date relative to the current time.
 *
 * @param {Date} date - Date to format.
 * @returns {string} Localized relative time string.
 */
export function formatRelativeTime(date) {
  // Calculate the difference between the target date and the current time in seconds.
  const seconds = Math.round((date.getTime() - Date.now()) / 1000);

  // Use the largest appropriate time unit for the given difference.
  const units = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
    ["second", 1],
  ];

  for (const [unit, divisor] of units) {
    if (Math.abs(seconds) >= divisor) {
      return relativeTimeFormatter.format(Math.round(seconds / divisor), unit);
    }
  }

  // Handle differences smaller than one second.
  return relativeTimeFormatter.format(0, "second");
}
