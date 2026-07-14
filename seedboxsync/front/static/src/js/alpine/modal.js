/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Settable modal with confirmation and call API.
 *
 * @returns
 */
import { toast } from "bulma-toast";

/**
 * Modal confirmation and call API.
 * @returns
 */
export function ModalConfirmCallComponent() {
  return {
    isActive: false,
    title: "",
    content: "",
    apiUrl: "",
    toastMessage: "",
    apiMethod: "POST",
    loading: false,
    error: false,

    open(title, content, url = "", method = "POST", toastMessage = "") {
      this.title = title;
      this.content = content;
      this.apiUrl = url;
      this.apiMethod = method;
      this.toastMessage = toastMessage;
      this.isActive = true;
      this.loading = false;
      this.error = false;
    },

    close() {
      this.isActive = false;
      this.loading = false;
      this.error = false;
    },

    async confirm() {
      if (!this.apiUrl) {
        this.close();
        return;
      }
      this.loading = true;
      this.error = false;

      try {
        const response = await fetch(this.apiUrl, { method: this.apiMethod });
        if (!response.ok) throw new Error("API call failed");
        toast({
          message: this.toastMessage,
          type: "is-success",
        });
        window.dispatchEvent(new CustomEvent("force-refresh")); // Refresh all components

        this.close();
      } catch (e) {
        console.error(e);
        toast({
          message: e.message,
          type: "is-danger",
        });
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
  };
}

/**
 * Open modal outside Alpine.
 *
 * @param {string} url
 * @param {string} method
 * @param {string} title
 * @param {string} content
 * @param {string} toastMessage
 */
export function OpenModalConfirmCall(
  url,
  method,
  title,
  content,
  toastMessage = ""
) {
  const modal = document.querySelector("#ModalConfirmCallComponent").__modal;
  modal.open(title, content, url, method, toastMessage);
}
