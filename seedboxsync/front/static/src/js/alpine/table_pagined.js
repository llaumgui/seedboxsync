 /**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Build AlpineJS table pagined components.
 * @param {string} apiUrl
 * @param {number} perPage
 * @param {string|null} datePickerRef
 * @returns
 */
export function TablePaginedComponent(apiUrl, perPage = 20, datePickerRef = null) {
  return {
    data: [],
    loading: true,
    error: false,
    page: 1,
    perPage,
    offset: 0,
    total: 0,
    search: "",
    startDate: null,
    endDate: null,

    /**
     * Load the current page from the API with the active filters.
     *
     * @returns {Promise<void>}
     */
    async load() {
      this.loading = true;
      this.error = false;
      try {
        const url = new URL(apiUrl, window.location.origin);
        url.searchParams.set("limit", this.perPage);
        url.searchParams.set("offset", this.offset);
        if (this.search) url.searchParams.set("search", this.search);
        if (this.startDate) url.searchParams.set("start_date", this.startDate);
        if (this.endDate) url.searchParams.set("end_date", this.endDate);

        const r = await fetch(url);
        if (!r.ok) throw new Error("Fetch failed");

        const json = await r.json();
        this.data = json.data;
        this.total = json.data_total;
      } catch (e) {
        this.error = true;
        this.data = [];
        this.total = 0;
        console.error(e);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Get the number of pages required for the current result set.
     *
     * @returns {number} Total number of pages.
     */
    get totalPages() {
      return Math.ceil(this.total / this.perPage);
    },

    /**
     * Load the next page when one is available.
     *
     * @returns {void}
     */
    nextPage() {
      if (this.page < this.totalPages) {
        this.page++;
        this.offset = (this.page - 1) * this.perPage;
        this.load();
      }
    },

    /**
     * Load the previous page when one is available.
     *
     * @returns {void}
     */
    prevPage() {
      if (this.page > 1) {
        this.page--;
        this.offset = (this.page - 1) * this.perPage;
        this.load();
      }
    },

    /**
     * Load a specific page when it belongs to the current result set.
     *
     * @param {number} p Page number to load.
     * @returns {void}
     */
    goToPage(p) {
      if (p >= 1 && p <= this.totalPages) {
        this.page = p;
        this.offset = (this.page - 1) * this.perPage;
        this.load();
      }
    },

    /**
     * Build the page numbers displayed by the pagination controls.
     *
     * @returns {Array<{page: number|null, isEllipsis: boolean}>} Visible pages.
     */
    get visiblePages() {
      const delta = 2;
      const pages = [];
      const start = Math.max(1, this.page - delta);
      const end = Math.min(this.totalPages, this.page + delta);

      if (start > 1) pages.push({ page: 1, isEllipsis: false });
      if (start > 2) pages.push({ page: null, isEllipsis: true });

      for (let i = start; i <= end; i++)
        pages.push({ page: i, isEllipsis: false });

      if (end < this.totalPages - 1)
        pages.push({ page: null, isEllipsis: true });
      if (end < this.totalPages)
        pages.push({ page: this.totalPages, isEllipsis: false });

      return pages;
    },

    /**
     * Set the search filter and reload the first page.
     *
     * @param {string} value Search value.
     * @returns {void}
     */
    updateSearch(value) {
      this.search = value;
      this.page = 1;
      this.offset = 0;
      this.load();
    },

    /**
     * Format a date as an ISO date string using the local timezone.
     *
     * @param {Date} date Date to format.
     * @returns {string} Date formatted as YYYY-MM-DD.
     */
    formatDate(date) {
      return date.toLocaleDateString("sv-SE");
    },

    /**
     * Set the selected date range and reload the first page.
     *
     * @param {Date|null} startDate Start date of the selected period.
     * @param {Date|null} endDate End date of the selected period.
     * @returns {void}
     */
    updateDateRange(startDate, endDate) {
      this.startDate = startDate ? this.formatDate(startDate) : null;
      this.endDate = endDate ? this.formatDate(endDate) : null;
      this.page = 1;
      this.offset = 0;
      this.load();
    },

    /**
     * Initialize the component and register refresh listeners.
     *
     * @returns {void}
     */
    init() {
      if (datePickerRef && this.$refs[datePickerRef]) {
        this.$refs[datePickerRef].addEventListener("datepicker:select", (event) => {
          const value = event.detail.value;
          this.updateDateRange(value?.start, value?.end);
        });

        this.$refs[datePickerRef].addEventListener("datepicker:clear", () => {
          this.updateDateRange(null, null);
        });
      }

      this.load();
      window.addEventListener("force-refresh", () => this.load());
    },
  };
}
