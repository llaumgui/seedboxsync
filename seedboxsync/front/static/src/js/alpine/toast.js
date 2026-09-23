/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { Toast as btToast } from "bootstrap";

/**
 * Alpine toast manager.
 *
 * @returns {object}
 */
export function ToastManager() {
  return {
    toasts: [],

    show({ message, type = "info" }) {
      const id = crypto.randomUUID();

      this.toasts.push({ id, message, type });

      this.$nextTick(() => {
        const element = this.$root.querySelector(`[data-toast-id="${id}"]`);

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

    remove(id) {
      this.toasts = this.toasts.filter((item) => item.id !== id);
    },
  };
}
