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
    return "cursor-pointer fa-solid fa-file text-grey";

  // Main type
  if (mimeType.startsWith("video/"))
    return "cursor-pointer fa-solid fa-video text-blue";
  if (mimeType.startsWith("image/"))
    return "cursor-pointer fa-solid fa-image text-purple";
  if (mimeType.startsWith("audio/"))
    return "cursor-pointer fa-solid fa-music text-red";
  if (mimeType.startsWith("text/"))
    return "cursor-pointer fa-solid fa-file-lines text-orange";
  if (mimeType.startsWith("application/x-bittorrent"))
    return "fa-solid fa-download text-grey";

  // Others types
  switch (mimeType) {
    case "application/pdf":
      return "cursor-pointer fa-solid fa-file-pdf text-green";
    case "application/zip":
    case "application/x-7z-compressed":
    case "application/x-rar-compressed":
    case "application/x-tar":
      return "cursor-pointer fa-solid fa-file-zipper text-warning";
    case "application/json":
    case "application/xml":
      return "cursor-pointer fa-solid fa-file-code text-secondary";
    default:
      return "cursor-pointer fa-solid fa-file text-grey";
  }
}