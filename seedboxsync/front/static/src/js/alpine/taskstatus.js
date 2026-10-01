/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import { formatRelativeTime } from "../utils/date";

/**
 * Create an Alpine.js component for monitoring and launching a task.
 *
 * The component periodically retrieves the task status from an API,
 * displays its current state, and allows the task to be launched manually.
 * It also displays notifications when the task status changes.
 *
 * @param {string} urlInfo - API URL used to retrieve the task status.
 * @param {string} urlLaunch - API URL used to launch the task.
 * @param {string} title - Title used for task status notifications.
 * @param {number} [refreshMs=30000] - Refresh interval in milliseconds.
 *   Set to 0 or a negative value to disable automatic refresh.
 * @returns {object} Alpine.js component state and methods.
 */
export function TaskStatusComponent(
  urlInfo,
  urlLaunch,
  title,
  refreshMs = 30000,
) {
  return {
    /** @type {boolean} Whether the task status is currently loading. */
    loading: true,

    /** @type {boolean} Whether the task is currently being launched. */
    tasking: false,

    /** @type {string|null} Error message displayed when status loading fails. */
    error: null,

    /** @type {object|null} Current task status data returned by the API. */
    taskStatusData: null,

    /** @type {string} Current human-readable task status message. */
    taskStatusMessage: "",

    /** @type {string} Task title used in notifications. */
    taskStatusTitle: title,

    /** @type {string} Previous task status message. */
    previousLockMessage: "",

    /**
     * @type {string}
     * CSS class applied to the task status indicator based on the freshness
     * of the last completed execution.
     */
    /**
     * Get the indicator class using a freshness threshold in minutes.
     *
     * @param {number} statusTime Minutes before a completed task is considered stale.
     * @returns {string} CSS class for the status indicator.
     */
    taskStatusIndicatorClass(statusTime) {
      // No task status or completion date means the task has never been completed.
      if (!this.taskStatusData?.finished) {
        return "text-body-secondary";
      }

      const finished = new Date(this.taskStatusData.finished).getTime();
      const now = Date.now();
      const threshold = statusTime * 60 * 1000;

      // Mark the task as successful when it completed within the configured threshold.
      return now - finished < threshold
        ? "text-success"
        : "text-danger";
    },

    /**
     * Initialize the component and start automatic status refreshes.
     *
     * The initial status is loaded immediately. When automatic refresh is
     * enabled, the status is then periodically refreshed at the configured
     * interval. A global refresh event also triggers an immediate update.
     *
     * @returns {Promise<void>}
     */
    async init() {
      await this.loadTaskStatus();

      if (refreshMs > 0) {
        setInterval(() => this.loadTaskStatus(), refreshMs);
      }

      window.addEventListener("force-refresh", () => this.loadTaskStatus());
    },

    /**
     * Load the current task status from the API.
     *
     * A 404 response is interpreted as the task having never been launched.
     * Successful responses update the task data and generate a human-readable
     * message based on whether the task is running or has completed.
     *
     * @returns {Promise<void>}
     */
    async loadTaskStatus() {
      this.loading = true;
      this.error = null;

      try {
        const res = await fetch(urlInfo);

        if (res.status === 404) {
          // Specific handling for a task that has never been launched.
          this.taskStatusData = null;
          this.updateLockMessage(Translations.never_launched);
          this.loading = false;
          return;
        }

        if (!res.ok) {
          throw new Error(`HTTP error ${res.status}`);
        }

        const json = await res.json();

        this.taskStatusData = json.data;

        if (this.taskStatusData.running) {
          this.updateLockMessage(
            `${Translations.in_progress} ${formatRelativeTime(new Date(this.taskStatusData.started))}`,
          );
        } else {
          this.updateLockMessage(
            `${Translations.completed} ${formatRelativeTime(new Date(this.taskStatusData.started))}`,
          );
        }
      } catch (e) {
        this.error = Translations.error_loading_lock_status;
        console.error(e);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Update the displayed task status message.
     *
     * A notification is displayed when an existing status message changes.
     *
     * @param {string} newMessage - New human-readable task status message.
     * @returns {void}
     */
    updateLockMessage(newMessage) {
      // Trigger a toast when the status message changes.
      if (
        this.taskStatusMessage !== "" &&
        this.taskStatusMessage !== newMessage
      ) {
        this.$dispatch("show-toast", {
          message: `${newMessage}`,
          type: "info",
          title: `${this.taskStatusTitle}`,
        });
      }

      this.previousLockMessage = this.taskStatusMessage;
      this.taskStatusMessage = newMessage;
    },

    /**
     * Launch the task through the configured API endpoint.
     *
     * A successful HTTP 202 response displays a success notification.
     * Other HTTP responses display a task scheduling error notification.
     *
     * @returns {Promise<void>}
     */
    async taskLaunch() {
      try {
        this.tasking = true;

        const res = await fetch(urlLaunch, { method: "POST" });

        if (res.status === 202) {
          this.$dispatch("show-toast", {
            message: `${Translations.task_scheduled}`,
            type: "success",
            title: `${this.taskStatusTitle}`,
          });
        } else {
          this.$dispatch("show-toast", {
            message: `${Translations.task_not_scheduled}`,
            type: "danger",
            title: `${this.taskStatusTitle}`,
          });
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.tasking = false;
      }
    },
  };
}