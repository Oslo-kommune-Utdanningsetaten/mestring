<script lang="ts">
  import { Chart, registerables } from 'chart.js'
  Chart.register(...registerables)

  interface Props {
    data: Array<number>
    lineColor?: string
    label?: string
  }

  const { data, lineColor = 'rgb(200, 200, 192)', label = 'Data' }: Props = $props()
  let chartContainer: HTMLCanvasElement | null = $state(null)
  let chart: Chart | null = null

  const updateChart = () => {
    if (!chartContainer) return
    if (data.some(isNaN)) {
      console.warn('Data contains non-numeric values, cannot render chart:', data)
      return
    }
    if (!chart) {
      chart = new Chart(chartContainer, {
        type: 'line',
        data: {
          labels: Array.from({ length: data.length }, (_, i) => i + 1),
          datasets: [
            {
              data,
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
      chart.data.datasets[0].data = data
      chart.data.labels = Array.from({ length: data.length }, (_, i) => i + 1)
      chart.update('none')
    }
  }

  $effect(() => {
    if (data?.length) {
      updateChart()
    }
  })
</script>

{#if data?.length}
  <div class="chart-container" title={data.join(', ')}>
    <canvas bind:this={chartContainer}></canvas>
  </div>
{/if}

<style>
  .chart-container {
    width: 35px;
    height: 30px;
    margin-left: -5px;
    margin-bottom: -5px;
  }
</style>
