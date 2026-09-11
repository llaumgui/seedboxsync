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
export function createDoughnutChart(ctx, data, element, label = "count") {
  const labels = data.map((d) => d.mime_type);
  const total = data.map((d) => d[element]);

  return new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          label: label,
          data: total,
          backgroundColor: [
            "rgb(191, 97, 106)",
            "rgb(208, 135, 112)",
            "rgb(235, 203, 139)",
            "rgb(163, 190, 140)",
            "rgb(180, 142, 173)",
          ],
          hoverOffset: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const item = data[context.dataIndex];
              const humanizedKey = `human_${element}`;

              if (item[humanizedKey] !== undefined) {
                return ` ${context.dataset.label}: ${item[humanizedKey]}`;
              }

              return ` ${context.dataset.label}: ${context.raw}`;
            },
          },
        },
      },
    },
  });
}

/**
 * Load chart data from a URL and create a bar chart.
 * @param {*} ctx
 * @param {*} url
 * @param {*} label
 */
export function loadChart(ctx1, field1, label1, ctx2, field2, label2, url) {
  fetch(url)
    .then((res) => res.json())
    .then((json) => {
      createDoughnutChart(ctx1, json.data, field1, label1)
      createDoughnutChart(ctx2, json.data, field2, label2)
    })
    .catch((err) => console.error("Error loading chart:", err));
}
