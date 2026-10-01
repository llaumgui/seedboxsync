/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
export function CardsStats(
  urlStats,
  refreshMs = 30000,
) {
  return {
    /** @type {boolean} Whether the statistics are currently loading. */
    loading: true,

    /** @type {string|null} Error message displayed when statistics loading fails. */
    error: null,

    /** @type {object|null} Statistics data returned by the API. */
    data: null,

    /**
     * Initialize the component and start automatic statistics refreshes.
     *
     * The initial statistics are loaded immediately. When automatic refresh
     * is enabled, the statistics are periodically refreshed at the configured
     * interval. A global refresh event also triggers an immediate update.
     *
     * @returns {Promise<void>}
     */
    async init() {
      await this.loadStats();

      if (refreshMs > 0) {
        setInterval(() => this.loadStats(), refreshMs);
      }

      window.addEventListener("force-refresh", () => this.loadStats());
    },

    /**
     * Load the current statistics from the API.
     *
     * Successful responses update the component data. HTTP errors and
     * request failures are stored in the component error state.
     *
     * @returns {Promise<void>}
     */
    async loadStats() {
      this.loading = true;
      this.error = null;

      try {
        const res = await fetch(urlStats);

        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }

        const json = await res.json();
        this.data = json.data;
      } catch (e) {
        this.error = Translations.error_loading_lock_status;
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
  };
}