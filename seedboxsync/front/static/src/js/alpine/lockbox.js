/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { toast } from "bulma-toast";

/**
 * Build AlpineJS lock box components.
 * @param {string} apiUrl
 * @param {string} title
 * @param {number} refreshMs
 * @returns
 */
export function LockBoxComponent(url, title, refreshMs = 30000) {
  return {
    loading: true,
    error: null,
    lockData: null,
    lockMessage: "",
    lockTitle: title,
    previousLockMessage: "",

    async init() {
      await this.loadLock();
      if (refreshMs > 0) {
        setInterval(() => this.loadLock(), refreshMs);
      }
      window.addEventListener("force-refresh", () => this.loadLock());
    },

    async loadLock() {
      this.loading = true;
      this.error = null;
      try {
        const res = await fetch(url);

        if (res.status === 404) {
          // Specific handling for never launched
          this.lockData = null;
          this.updateLockMessage(Translations.never_launched);
          this.loading = false;
          return;
        };

        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const json = await res.json();
        this.lockData = json.data;

        if (this.lockData.locked) {
          this.updateLockMessage(
            `${Translations.in_progress_since} ${new Date(
              this.lockData.locked_at
            ).toLocaleString(undefined, dateTimeOption)}`
          );
        } else {
          this.updateLockMessage(
            `${Translations.completed_since} ${new Date(
              this.lockData.unlocked_at
            ).toLocaleString(undefined, dateTimeOption)}`
          );
        }
      } catch (e) {
        this.error = Translations.error_loading_lock_status;
        console.error(e);
      } finally {
        this.loading = false;
      }
    },

    updateLockMessage(newMessage) {
      // Trigger toast if message changed
      if (this.lockMessage !== "" && this.lockMessage !== newMessage) {
        toast({
          message: "<strong>" + this.lockTitle + "</strong>\n<br>" + newMessage,
          type: "is-info",
        });
      }
      this.previousLockMessage = this.lockMessage;
      this.lockMessage = newMessage;
    }
  };
}
