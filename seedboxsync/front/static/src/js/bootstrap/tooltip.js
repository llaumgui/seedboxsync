/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import { Tooltip } from "bootstrap";

// Tooltip
const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map( // eslint-disable-line no-unused-vars
  (tooltipTriggerEl) => new Tooltip(tooltipTriggerEl),
);

window.Tooltip = Tooltip;
