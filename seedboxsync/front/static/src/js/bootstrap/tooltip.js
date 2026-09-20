import { Tooltip } from "bootstrap";

// Tooltip
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map( // eslint-disable-line no-unused-vars
  (tooltipTriggerEl) => new Tooltip(tooltipTriggerEl),
);

window.Tooltip = Tooltip;
