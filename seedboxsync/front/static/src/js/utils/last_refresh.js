/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Manage the last refresh timestamp.
 *
 * @returns {Object} Alpine component containing the last refresh date.
 */
export function LastRefresh() {
  return {
    lastRefresh: new Date(),

    init() {
      window.addEventListener("force-refresh", () => {
        this.lastRefresh = new Date();
      });
    },
  };
}
