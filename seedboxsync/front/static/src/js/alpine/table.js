/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Build AlpineJS table components.
 * @param {string} apiUrl
 * @param {number} refreshMs
 * @returns
 */
export function TableComponent(apiUrl, refreshMs = 30000) {
  return {
    data: [],
    loading: true,
    error: false,
    load() {
      this.loading = true;
      this.error = false;
      fetch(apiUrl)
        .then((r) => {
          if (!r.ok) throw new Error();
          return r.json();
        })
        .then((json) => {
          this.data = json.data;
        })
        .catch(() => {
          this.error = true;
          this.data = [];
        })
        .finally(() => {
          this.loading = false;
        });
    },
    init() {
      this.load();
      setInterval(() => this.load(), refreshMs);
      window.addEventListener("force-refresh", () => this.load());
    },
  };
};
