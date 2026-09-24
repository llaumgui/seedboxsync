/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { Modal } from "bootstrap";

/**
 * Create an Alpine.js component for displaying a confirmation modal
 * and optionally executing an API request when confirmed.
 *
 * The component manages the modal state, API request status, success and
 * error notifications, and refresh events after a successful operation.
 *
 * @returns {object} Alpine.js component state and methods.
 */
export function ModalConfirmCallComponent() {
  return {
    /** @type {string} Modal title displayed to the user. */
    title: "",

    /** @type {string} Modal body content displayed to the user. */
    content: "",

    /** @type {string} API endpoint to call on confirmation. */
    apiUrl: "",

    /** @type {string} Success message displayed after a successful API call. */
    toastMessage: "",

    /** @type {string} Title displayed with the toast notification. */
    toastTitle: "",

    /** @type {string} HTTP method used for the API request. */
    apiMethod: "POST",

    /** @type {boolean} Whether an API request is currently in progress. */
    loading: false,

    /** @type {boolean} Whether the last API request failed. */
    error: false,

    /** @type {Modal|null} Bootstrap modal instance. */
    modal: null,

    /**
     * Initialize the Bootstrap modal instance.
     *
     * @returns {void}
     */
    init() {
      this.modal = Modal.getOrCreateInstance(this.$refs.modal);
    },

    /**
     * Configure and display the confirmation modal.
     *
     * @param {string} title - Modal title.
     * @param {string} content - Modal body content.
     * @param {string} [url=""] - API endpoint to call on confirmation.
     * @param {string} [method="POST"] - HTTP method used for the API request.
     * @param {string} [toastMessage=""] - Success message displayed after completion.
     * @param {string} [toastTitle=""] - Title displayed with the toast notification.
     * @returns {void}
     */
    open(
      title,
      content,
      url = "",
      method = "POST",
      toastMessage = "",
      toastTitle = "",
    ) {
      this.title = title;
      this.content = content;
      this.apiUrl = url;
      this.apiMethod = method;
      this.toastMessage = toastMessage;
      this.toastTitle = toastTitle;
      this.loading = false;
      this.error = false;

      this.modal.show();
    },

    /**
     * Close the modal and reset its transient state.
     *
     * @returns {void}
     */
    close() {
      this.modal.hide();
      this.loading = false;
      this.error = false;
    },

    /**
     * Execute the configured API request after user confirmation.
     *
     * If no API URL is configured, the modal is simply closed.
     * On success, a success toast is dispatched and a global refresh event
     * is emitted. API errors are logged and displayed through an error toast.
     *
     * @returns {Promise<void>}
     */
    async confirm() {
      if (!this.apiUrl) {
        this.close();
        return;
      }

      this.loading = true;
      this.error = false;

      try {
        const response = await fetch(this.apiUrl, {
          method: this.apiMethod,
        });

        if (!response.ok) {
          throw new Error("API call failed");
        }

        this.$dispatch("show-toast", {
          message: this.toastMessage,
          type: "success",
          title: this.toastTitle,
        });

        window.dispatchEvent(new CustomEvent("force-refresh"));

        this.close();
      } catch (e) {
        console.error(e);

        this.$dispatch("show-toast", {
          message: e.message,
          type: "danger",
          title: this.toastTitle,
        });

        this.error = true;
      } finally {
        this.loading = false;
      }
    },
  };
}