/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
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
  labelFiles = "Files",
  labelSize = "Size (GiB)",
  labelField = "month"
) {
  const labels = data.map((d) => d[labelField]);
  const filesData = data.map((d) => d.files);
  const sizeData = data.map((d) => parseFloat(d.total_size));

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: labelFiles,
          data: filesData,
          backgroundColor: "#9fee5c",
          borderWidth: 1,
          borderColor: "#a3be8c",
        },
        {
          label: labelSize,
          data: sizeData,
          backgroundColor: "#ee54d2",
          borderWidth: 1,
          borderColor: "#b48ead",
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
export function loadChart(ctx, url, labelField) {
  fetch(url)
    .then((res) => res.json())
    .then((json) =>
      createBarChart(ctx, json.data, "Files", "Size (GiB)", labelField)
    )
    .catch((err) => console.error("Error loading chart:", err));
}
