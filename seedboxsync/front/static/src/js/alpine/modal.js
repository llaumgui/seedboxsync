/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import { Modal } from "bootstrap";
import { Toast } from "./toast";

/**
 * Modal confirmation and call API.
 *
 * @returns {object}
 */
export function ModalConfirmCallComponent() {
  return {
    title: "",
    content: "",
    apiUrl: "",
    toastMessage: "",
    apiMethod: "POST",
    loading: false,
    error: false,
    modal: null,

    init() {
      this.modal = Modal.getOrCreateInstance(this.$refs.modal);
    },

    open(title, content, url = "", method = "POST", toastMessage = "") {
      this.title = title;
      this.content = content;
      this.apiUrl = url;
      this.apiMethod = method;
      this.toastMessage = toastMessage;
      this.loading = false;
      this.error = false;

      this.modal.show();
    },

    close() {
      this.modal.hide();
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
        const response = await fetch(this.apiUrl, {
          method: this.apiMethod,
        });

        if (!response.ok) {
          throw new Error("API call failed");
        }

        Toast({
          message: this.toastMessage,
          type: "success",
        });

        window.dispatchEvent(new CustomEvent("force-refresh"));

        this.close();
      } catch (e) {
        console.error(e);

        Toast({
          message: e.message,
          type: "danger",
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
  toastMessage = "",
) {
  const component = document.querySelector(
    "#ModalConfirmCallComponent",
  ).__modal;

  component.open(title, content, url, method, toastMessage);
}
