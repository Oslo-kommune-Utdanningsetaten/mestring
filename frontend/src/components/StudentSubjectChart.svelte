<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { UserType, SubjectType, ObservationType, GoalType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { fetchGoalsForSubjectAndStudent, isNumber } from '../utils/functions'
  import { useMasteryCalculations, getMasteryLevelColorByValue } from '../utils/masteryHelpers'
  import { PolarArea } from 'svelte-chartjs'
  import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, RadialLinearScale } from 'chart.js'

  ChartJS.register(Title, Tooltip, Legend, ArcElement, RadialLinearScale)

  const {
    subject,
    student,
    size = 'large',
  } = $props<{
    subject: SubjectType
    student: UserType
    size?: 'small' | 'large'
  }>()

  const labelMaxLength = 18

  let { masterySchemas, currentSchool, currentUser } = $derived($dataStore)
  let goalsForSubjectDecorated = $state<GoalDecorated[]>([])
  let data = $state<{
    datasets: { data: number[]; backgroundColor: string[] }[]
    labels: string[]
  }>({ datasets: [{ data: [], backgroundColor: [] }], labels: [] })

  const masterySchema = $derived(
    // assume all goals for this subject use same mastery schema, just grab the first one
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
          display: size === 'large', // only dispaly goal labels for large version
          centerPointLabels: true,
          font: {
            size: 12,
          },
          callback: (label: string) =>
            label.length > labelMaxLength ? label.slice(0, labelMaxLength - 1) + '…' : label,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
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
    assembleChartData()
  }

  const assembleChartData = () => {
    const numberOfGoals = goalsForSubjectDecorated.length
    const maxNumberOfObservations = Math.max(
      ...goalsForSubjectDecorated.map(goal => goal.observations.length)
    )
    const datasets = [{ data: [] as number[], backgroundColor: [] as string[] }]
    // initialize datasets
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

<div class={size === 'large' ? 'chart-large' : 'chart-small'}>
  <PolarArea {data} options={chartOptions} />
</div>

<style>
  .chart-large {
    width: min(350px, 100%);
    aspect-ratio: 1;
  }

  .chart-small {
    width: 75px;
    height: 75px;
  }
</style>
