/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import Chart from "chart.js/auto";
import { createBarChart, loadChart as loadBarChart } from "./bar";
import { createDoughnutChart, load2Chart as load2DoughnutChart } from "./doughnut";

window.Chart = Chart;
window.createBarChart = createBarChart;
window.loadBarChart = loadBarChart;
window.createDoughnutChart = createDoughnutChart;
window.load2DoughnutChart = load2DoughnutChart;
