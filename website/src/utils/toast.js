import Toastify from "toastify-js";
import "toastify-js/src/toastify.css";

function showToast(messages, type = "info") {
  Toastify({
    text: messages,
    duration: 2800,
    newWindow: true,
    close: true,
    gravity: "top",
    position: "right",
    stopOnFocus: true,
    className: `app-toast toast-${type}`,
    offset: {
      x: 16,
      y: 72,
    },
    style: {
      background: "#ffffff",
    },
    onClick: function () {},
  }).showToast();
}

export default class Toast {
  /**
   * Display an informational toast message.
   * @param {*} messages
   */
  static info(messages) {
    showToast(messages, "info");
  }

  /**
   * Display a success toast message.
   * @param {*} messages
   */
  static success(messages) {
    showToast(messages, "success");
  }

  /**
   * Display a warning toast message.
   * @param {*} messages
   */
  static warning(messages) {
    showToast(messages, "warning");
  }

  /**
   * Display an error toast message.
   * @param {*} messages
   */
  static error(messages) {
    showToast(messages, "error");
  }
}

