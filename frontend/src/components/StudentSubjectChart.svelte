<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { UserType, SubjectType, ObservationType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { fetchGoalsForSubjectAndStudent, isNumber } from '../utils/functions'
  import { useMasteryCalculations, getMasteryLevelColorByValue } from '../utils/masteryHelpers'
  import { PolarArea } from 'svelte-chartjs'
  import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, RadialLinearScale } from 'chart.js'

  ChartJS.register(Title, Tooltip, Legend, ArcElement, RadialLinearScale)

  const {
    subject,
    student,
    isLabelEnabled = false,
  } = $props<{
    subject: SubjectType
    student: UserType
    isLabelEnabled?: boolean
  }>()

  let { masterySchemas, currentSchool, currentUser } = $derived($dataStore)
  let goalsForSubjectDecorated = $state<GoalDecorated[]>([])
  let data = $state<{
    datasets: { data: number[]; backgroundColor: string[] }[]
    labels: string[]
  }>({ datasets: [{ data: [], backgroundColor: [] }], labels: [] })

  // Assume all goals for this subject use same mastery schema, just grab the first one
  const masterySchema = $derived(
    masterySchemas.find(ms => ms.id === goalsForSubjectDecorated[0]?.masterySchemaId)
  )

  const { minValue, maxValue } = $derived(useMasteryCalculations(masterySchema))

  const chartOptions = $derived({
    scales: {
      r: {
        min: minValue,
        max: maxValue,
        ticks: {
          stepSize: maxValue / masterySchema?.config?.levels.length,
          display: false, // Hide numeric labels
        },
        pointLabels: {
          display: isLabelEnabled,
          centerPointLabels: true,
          font: {
            size: 12,
          },
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false, // dispable built-in tooltip since an exact number isn't what we really want from this chart
      },
    },
    responsive: true,
    maintainAspectRatio: false,
  })

  const fetchGoals = async () => {
    goalsForSubjectDecorated = await fetchGoalsForSubjectAndStudent(
      subject.id,
      student.id,
      currentSchool?.id!,
      currentUser.allGroups
    )
    if (goalsForSubjectDecorated.length) {
      assembleChartData()
    }
  }

  const assembleChartData = () => {
    const numberOfGoals = goalsForSubjectDecorated.length
    const maxNumberOfObservations = Math.max(
      ...goalsForSubjectDecorated.map(goal => goal.observations.length)
    )
    // initialize datasets
    const datasets = [{ data: [] as number[], backgroundColor: [] as string[] }]
    for (let i = 0; i < maxNumberOfObservations; i++) {
      datasets[i] = { data: new Array(numberOfGoals), backgroundColor: new Array(numberOfGoals) }
    }

    goalsForSubjectDecorated.forEach((goal: GoalDecorated, goalIndex: number) => {
      goal.observations.forEach((observation: ObservationType, observationIndex: number) => {
        if (isNumber(observation.masteryValue)) {
          const value = observation.masteryValue
          datasets[observationIndex].data[goalIndex] = value
          const color = getMasteryLevelColorByValue(value, masterySchema, 0.5)
          datasets[observationIndex].backgroundColor[goalIndex] = color
        }
      })
    })

    data.datasets = datasets

    // labels
    data.labels = goalsForSubjectDecorated.map(goal => goal.title || goal.sortOrder.toString())
    data = { ...data } // Trigger reactivity
  }

  $effect(() => {
    if (student && subject) {
      fetchGoals()
    }
  })
</script>

{#if data.datasets[0].data.length > 0}
  <div class="chart-container">
    <PolarArea {data} options={chartOptions} />
  </div>
{/if}

<style>
  .chart-container {
    width: 100%;
    height: 100%;
  }
</style>
