/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import { BaseChart, SeriesChart } from "./base.js";

/**
 * Create a bar chart.
 *
 * @param {HTMLCanvasElement} ctx
 * @param {Array} data
 * @param {string} labelFiles
 * @param {string} labelSize
 * @param {string} labelField
 * @returns {Chart}
 */
export function createLineChart(ctx, data, labelFiles, labelSize, labelField) {
  return SeriesChart.create({
    ctx,
    type: "line",
    data,
    labelField,
    datasets: [
      {
        label: labelFiles,
        value: (d) => d.files,
        backgroundColor: "#b48ead",
        borderWidth: 2,
        borderColor: "#a27f9b",
        tension: 0.3,
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHitRadius: 10,
      },
      {
        label: labelSize,
        value: (d) => Number.parseFloat(d.total_size),
        backgroundColor: "#a3be8c",
        borderWidth: 2,
        borderColor: "#92ab7e",
        tension: 0.3,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHitRadius: 10,
      },
    ],
  });
}

/**
 * Load chart data from a URL and create a bar chart.
 *
 * @param {HTMLCanvasElement} ctx
 * @param {string} url
 * @param {string} labelFiles
 * @param {string} labelSize
 * @param {string} labelField
 * @param {AbortSignal} signal
 * @returns {Promise<Chart>}
 */
export async function loadChart(
  ctx,
  url,
  labelFiles,
  labelSize,
  labelField,
  signal,
) {
  const data = await BaseChart.loadData(url, signal);

  return createLineChart(ctx, data, labelFiles, labelSize, labelField);
}
