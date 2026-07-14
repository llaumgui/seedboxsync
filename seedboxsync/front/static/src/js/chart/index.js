/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import Chart from "chart.js/auto";
import { createBarChart, loadChart } from "./create_bar";

window.Chart = Chart;
window.createBarChart = createBarChart;
window.loadChart = loadChart;
