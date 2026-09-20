import './tooltip';

// Mode Dark / Light / Prefers
const theme = document.documentElement.dataset.bsTheme;

if (theme !== "light" && theme !== "dark") {
  document.documentElement.dataset.bsTheme = window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches
    ? "dark"
    : "light";
}
