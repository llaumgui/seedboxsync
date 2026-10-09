/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Return the application locale from the HTML document.
 *
 * @returns {string|undefined} Application locale when available.
 */
function _getLocale() {
  if (typeof document === "undefined") {
    return undefined;
  }

  return document.documentElement?.lang || undefined;
}

/**
 * Date and time formatting options used by the application.
 *
 * @type {Intl.DateTimeFormatOptions}
 */
export const dateTimeOption = {
  weekday: "short",
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
};

/**
 * Format dates as localized relative time values.
 *
 * Uses the browser locale and automatically selects the most relevant
 * time unit between days, hours, minutes, and seconds.
 */
const relativeTimeFormatter = new Intl.RelativeTimeFormat(_getLocale(), {
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


/**
 * Format a date using the application locale.
 *
 * @param {Date} date - Date to format.
 * @param {Intl.DateTimeFormatOptions} [options=dateTimeOption]
 *   Date and time formatting options.
 * @returns {string} Localized date and time string.
 */
export function localeDateString(date, options = dateTimeOption) {
  return date.toLocaleString(_getLocale(), options);
}