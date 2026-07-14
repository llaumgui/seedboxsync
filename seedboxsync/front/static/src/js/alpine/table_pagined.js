 /**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Build AlpineJS table pagined components.
 * @param {string} apiUrl
 * @param {number} perPage
 * @returns
 */
export function TablePaginedComponent(apiUrl, perPage = 20) {
  return {
    data: [],
    loading: true,
    error: false,
    page: 1,
    perPage,
    offset: 0,
    total: 0,
    search: "",

    async load() {
      this.loading = true;
      this.error = false;
      try {
        const url = new URL(apiUrl, window.location.origin);
        url.searchParams.set("limit", this.perPage);
        url.searchParams.set("offset", this.offset);
        if (this.search) url.searchParams.set("search", this.search);

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

    get totalPages() {
      return Math.ceil(this.total / this.perPage);
    },

    nextPage() {
      if (this.page < this.totalPages) {
        this.page++;
        this.offset = (this.page - 1) * this.perPage;
        this.load();
      }
    },

    prevPage() {
      if (this.page > 1) {
        this.page--;
        this.offset = (this.page - 1) * this.perPage;
        this.load();
      }
    },

    goToPage(p) {
      if (p >= 1 && p <= this.totalPages) {
        this.page = p;
        this.offset = (this.page - 1) * this.perPage;
        this.load();
      }
    },

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

    updateSearch(value) {
      this.search = value;
      this.page = 1;
      this.offset = 0;
      this.load();
    },

    init() {
      this.load();
      window.addEventListener("force-refresh", () => this.load());
    },
  };
}
