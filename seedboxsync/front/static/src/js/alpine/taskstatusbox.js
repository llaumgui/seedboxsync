/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { toast } from "bulma-toast";

/**
 * Build AlpineJS taskstatus box components.
 * @param {string} apiUrl
 * @param {string} title
 * @param {number} refreshMs
 * @returns
 */
export function TaskStatusBoxComponent(url, title, refreshMs = 30000) {
  return {
    loading: true,
    error: null,
    taskStatusData: null,
    taskStatusMessage: "",
    taskStatusTitle: title,
    previousLockMessage: "",

    async init() {
      await this.loadTaskStatus();
      if (refreshMs > 0) {
        setInterval(() => this.loadTaskStatus(), refreshMs);
      }
      window.addEventListener("force-refresh", () => this.loadTaskStatus());
    },

    async loadTaskStatus() {
      this.loading = true;
      this.error = null;
      try {
        const res = await fetch(url);

        if (res.status === 404) {
          // Specific handling for never launched
          this.taskStatusData = null;
          this.updateLockMessage(Translations.never_launched);
          this.loading = false;
          return;
        };

        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const json = await res.json();
        this.taskStatusData = json.data;

        if (this.taskStatusData.running) {
          this.updateLockMessage(
            `${Translations.in_progress_since} ${new Date(
              this.taskStatusData.started
            ).toLocaleString(undefined, dateTimeOption)}`
          );
        } else {
          this.updateLockMessage(
            `${Translations.completed_since} ${new Date(
              this.taskStatusData.finished
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
      if (this.taskStatusMessage !== "" && this.taskStatusMessage !== newMessage) {
        toast({
          message: "<strong>" + this.taskStatusTitle + "</strong>\n<br>" + newMessage,
          type: "is-info",
        });
      }
      this.previousLockMessage = this.taskStatusMessage;
      this.taskStatusMessage = newMessage;
    }
  };
}
