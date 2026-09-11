/**
 * Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
import Chart from "chart.js/auto";

/**
 * Create a bar chart.
 */
export function createBarChart(
  ctx,
  data,
  labelFiles,
  labelSize,
  labelField
) {
  const labels = data.map((d) => d[labelField]);
  const dataFiles = data.map((d) => d.files);
  const dataSize = data.map((d) => Number.parseFloat(d.total_size));

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: labelFiles,
          data: dataFiles,
          backgroundColor: "#a3be8c",
          borderWidth: 1,
          borderColor: "#92ab7e",
        },
        {
          label: labelSize,
          data: dataSize,
          backgroundColor: "#b48ead",
          borderWidth: 1,
          borderColor: "#a27f9b",
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: { y: { beginAtZero: true } },
    },
  });
}

/**
 * Load chart data from a URL and create a bar chart.
 * @param {*} ctx
 * @param {*} url
 * @param {*} labelField
 */
export function loadChart(ctx, url, label_file, label_size, labelField) {
  fetch(url)
    .then((res) => res.json())
    .then((json) =>
      createBarChart(ctx, json.data, label_file, label_size, labelField),
    )
    .catch((err) => console.error("Error loading chart:", err));
}
