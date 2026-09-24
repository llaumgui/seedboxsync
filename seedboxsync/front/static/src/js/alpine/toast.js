/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { Toast as btToast } from "bootstrap";

/**
 * Create an Alpine.js toast manager.
 *
 * The manager maintains the list of active toasts and integrates it with
 * Bootstrap's Toast component. Toasts are automatically hidden after a
 * configurable delay and removed from the Alpine.js state when hidden.
 *
 * @returns {object} Alpine.js toast manager state and methods.
 */
export function ToastManager() {
  return {
    /** @type {Array<object>} List of currently active toast notifications. */
    toasts: [],

    /**
     * Display a new toast notification.
     *
     * The toast is added to the Alpine.js state and initialized as a
     * Bootstrap Toast component once the corresponding DOM element is rendered.
     *
     * @param {object} options - Toast configuration.
     * @param {string} options.message - Message displayed in the toast.
     * @param {string} [options.type="info"] - Bootstrap contextual type of the toast.
     * @param {string} [options.title=""] - Optional title displayed in the toast.
     * @returns {void}
     */
    show({ message, type = "info", title = "" }) {
      const id = crypto.randomUUID();

      this.toasts.push({ id, message, type, title });

      this.$nextTick(() => {
        const element = this.$root.querySelector(
          `[data-toast-id="${id}"]`,
        );

        if (!element) {
          return;
        }

        const instance = btToast.getOrCreateInstance(element, {
          autohide: true,
          delay: 5000,
        });

        element.addEventListener(
          "hidden.bs.toast",
          () => {
            this.remove(id);
          },
          { once: true },
        );

        instance.show();
      });
    },

    /**
     * Remove a toast from the active toast list.
     *
     * @param {string} id - Unique identifier of the toast to remove.
     * @returns {void}
     */
    remove(id) {
      this.toasts = this.toasts.filter((item) => item.id !== id);
    },
  };
}