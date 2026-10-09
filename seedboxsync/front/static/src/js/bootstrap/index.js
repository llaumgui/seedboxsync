/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import "./tooltip";

// Mode Dark / Light / Prefers
const theme = document.documentElement.dataset.bsTheme;

if (theme !== "light" && theme !== "dark") {
  document.documentElement.dataset.bsTheme = window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches
    ? "dark"
    : "light";
}
