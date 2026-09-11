/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Get Font Awesome icon class based on MIME type.
 *
 * @param {string} mimeType - The MIME type string (e.g., 'application/pdf', 'video/mp4').
 * @returns {string} The Font Awesome icon CSS class string.
 */
export function getMimeIconClass(mimeType) {
  if (!mimeType || mimeType === "application/octet-stream")
    return "fa-solid fa-file has-text-grey";

  // Main type
  if (mimeType.startsWith("video/"))
    return "fa-solid fa-video has-text-link";
  if (mimeType.startsWith("image/"))
    return "fa-solid fa-image has-text-success";
  if (mimeType.startsWith("audio/"))
    return "fa-solid fa-music has-text-warning";
  if (mimeType.startsWith("text/"))
    return "fa-solid fa-file-lines has-text-info";
  if (mimeType.startsWith("application/x-bittorrent"))
    return "fa-solid fa-download has-text-primary";

  // Others types
  switch (mimeType) {
    case "application/pdf":
      return "fa-solid fa-file-pdf has-text-danger";
    case "application/zip":
    case "application/x-7z-compressed":
    case "application/x-rar-compressed":
    case "application/x-tar":
      return "fa-solid fa-file-zipper has-text-warning";
    case "application/json":
    case "application/xml":
      return "fa-solid fa-file-code has-text-link";
    default:
      return "fa-solid fa-file has-text-grey";
  }
}