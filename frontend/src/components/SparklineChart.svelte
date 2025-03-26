<script>
  // @ts-nocheck
  import { Chart, registerables } from 'chart.js'
  Chart.register(...registerables)

  import { onMount } from 'svelte'

  export let data = []
  export let lineColor = 'rgb(75, 192, 192)'
  export let label = 'Data'
  let chartContainer
  let chart

  function updateChart() {
    if (!chartContainer) return
    if (!chart) {
      chart = new Chart(chartContainer, {
        type: 'line',
        data: {
          labels: Array.from({ length: data.length }, (_, i) => i + 1),
          datasets: [
            {
              data: data.map(point => (typeof point === 'object' ? point.y : point)),
              fill: false,
              borderColor: lineColor,
              borderWidth: 1.5,
              label: label,
              pointRadius: 0,
              tension: 0.1,
            },
          ],
        },
        options: {
          scales: {
            x: {
              display: true,
              grid: {
                display: false,
              },
              border: {
                display: true,
                width: 1,
                color: '#e0e0e0',
              },
              ticks: {
                display: false,
              },
            },
            y: {
              display: true,
              grid: {
                display: false,
              },
              border: {
                display: true,
                width: 1,
                color: '#e0e0e0',
              },
              min: 0,
              max: 100,
              ticks: {
                display: false,
              },
            },
          },
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              enabled: false,
            },
          },
          elements: {
            line: {
              tension: 0.2,
            },
          },
        },
      })
    } else {
      chart.data.datasets[0].data = data.map(point => (typeof point === 'object' ? point.y : point))
      chart.data.labels = Array.from({ length: data.length }, (_, i) => i + 1)
      chart.update('none')
    }
  }

  $: if (data) updateChart()

  onMount(() => {
    updateChart()
  })
</script>

<div class="chart-container">
  <canvas bind:this={chartContainer}></canvas>
</div>

<style>
  .chart-container {
    width: 100%;
    height: 100%;
    margin-left: -5px;
    margin-bottom: -5px;
  }
</style>
