/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import Alpine from "alpinejs";
import * as validators from "./validators";
import { CardsStats } from "./cards_stats";
import { ModalConfirmCallComponent } from "./modal";
import { TableComponent } from "./table";
import { TablePaginedComponent } from "./table_pagined";
import { TaskStatusComponent } from "./taskstatus";
import { ToastManager } from "./toast";
import { StatsPeriod } from "./stats";
import { getMimeIconClass } from "./mimeicon"
import { formatRelativeTime, localeDateString } from "../utils/date.js";
import { LastRefresh } from "../utils/last_refresh.js";

// Tables
Alpine.data("TableComponent", TableComponent);
Alpine.data("TablePaginedComponent", TablePaginedComponent);
Alpine.data("TaskStatusComponent", TaskStatusComponent);

// Others elements / helpers
Alpine.data("CardsStats", CardsStats)
Alpine.data("ModalConfirmCallComponent", ModalConfirmCallComponent);
Alpine.data("StatsPeriod", StatsPeriod);
Alpine.data("ToastManager", ToastManager);
Alpine.data("LastRefresh", LastRefresh);

// Alpine magics
Alpine.magic(
  "relativeTime",
  () => (date) => formatRelativeTime(new Date(date)),
);
Alpine.magic(
  "getMimeIconClass",
  () => (mime_type) => getMimeIconClass(mime_type),
);
Alpine.magic(
  "localeDateString",
  () => (date, options) => localeDateString(new Date(date), options),
);
Alpine.magic("validators", () => validators);

// Start !!!
Alpine.start();