/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import Alpine from "alpinejs";
import * as validators from "./validators";
import { TableComponent } from "./table";
import { TablePaginedComponent } from "./table_pagined";
import { TaskStatusBoxComponent } from "./taskstatusbox";
import { ModalConfirmCallComponent, OpenModalConfirmCall } from "./modal";

// Tables
window.TableComponent = TableComponent;
window.TablePaginedComponent = TablePaginedComponent;
window.TaskStatusBoxComponent = TaskStatusBoxComponent;

// Modales
window.ModalConfirmCallComponent = ModalConfirmCallComponent;
window.OpenModalConfirmCall = OpenModalConfirmCall;

// Validators
window.isValidHost = validators.isValidHost;
window.isValidPort = validators.isValidPort;
window.isOctalChmod = validators.isOctalChmod;
window.isRequired = validators.isRequired;
window.isValidTimeout = validators.isValidTimeout;
window.isValidUrl = validators.isValidUrl;
window.isValidMaxConcPrefetchReq = validators.isValidMaxConcPrefetchReq;

window.Alpine = Alpine;
Alpine.start();