/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import { formatRelativeTime } from "../utils/date";

/**
 * Store the last known task status timestamp for each task.
 *
 * The URL used to retrieve the task status uniquely identifies a task
 * component. A Map is used instead of hashing the URL because the URL
 * itself is already a suitable and readable key.
 *
 * This state is shared by all TaskStatusComponent instances.
 *
 * @type {Map<string, string|null>}
 */
const taskStatusTimestamps = new Map();

/**
 * Create an Alpine.js component for monitoring and launching a task.
 *
 * The component periodically retrieves the task status from an API,
 * displays its current state, and allows the task to be launched manually.
 * It also displays notifications when the task status timestamp changes.
 *
 * A task status timestamp is defined as:
 * - `started` when the task is running.
 * - `finished` when the task has completed.
 *
 * The first status retrieval never triggers a notification. A notification
 * is displayed only when a subsequent retrieval reports a different status
 * timestamp for the same task endpoint.
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

    /**
     * Get the CSS class for the task status indicator.
     *
     * A completed task is considered successful when it finished within
     * the configured freshness threshold.
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
      return now - finished < threshold ? "text-success" : "text-danger";
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
     * A toast is displayed only when the task status timestamp changes after
     * the initial status retrieval.
     *
     * @returns {Promise<void>}
     */
    async loadTaskStatus() {
      this.loading = true;
      this.error = null;

      try {
        const res = await fetch(urlInfo);

        if (res.status === 404) {
          // A missing task status means that the task has never been launched.
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

        // Use the start timestamp while the task is running and the finish
        // timestamp once the task has completed.
        const statusTimestamp = this.taskStatusData.running
          ? this.taskStatusData.started
          : this.taskStatusData.finished;

        // Retrieve the timestamp previously known for this task endpoint.
        const previousTimestamp = taskStatusTimestamps.get(urlInfo);

        // The first successful retrieval only initializes the stored state.
        // Subsequent changes trigger a status notification.
        const statusChanged =
          previousTimestamp !== undefined &&
          previousTimestamp !== statusTimestamp;

        const statusMessage = this.taskStatusData.running
          ? `${Translations.in_progress} ${formatRelativeTime(
              new Date(statusTimestamp),
            )}`
          : `${Translations.completed} ${formatRelativeTime(
              new Date(statusTimestamp),
            )}`;

        this.updateLockMessage(statusMessage, statusChanged);

        // Store the latest status timestamp for this task endpoint.
        taskStatusTimestamps.set(urlInfo, statusTimestamp);
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
     * A notification is displayed only when the underlying task status
     * timestamp has changed.
     *
     * @param {string} newMessage - New human-readable task status message.
     * @param {boolean} [statusChanged=false] Whether the task status changed.
     * @returns {void}
     */
    updateLockMessage(newMessage, statusChanged = false) {
      if (statusChanged) {
        this.$dispatch("show-toast", {
          message: newMessage,
          type: "info",
          title: this.taskStatusTitle,
        });
      }

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

        const res = await fetch(urlLaunch, {
          method: "POST",
        });

        if (res.status === 202) {
          this.$dispatch("show-toast", {
            message: `${Translations.task_scheduled}`,
            type: "success",
            title: this.taskStatusTitle,
          });
        } else {
          this.$dispatch("show-toast", {
            message: `${Translations.task_not_scheduled}`,
            type: "danger",
            title: this.taskStatusTitle,
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
