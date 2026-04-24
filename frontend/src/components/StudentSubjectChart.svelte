<script lang="ts">
  import { dataStore } from '../stores/data'
  import type { UserType, SubjectType, ObservationType } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { fetchGoalsForSubjectAndStudent, isNumber } from '../utils/functions'
  import { useMasteryCalculations, getMasteryLevelColorByValue } from '../utils/masteryHelpers'
  import { PolarArea } from 'svelte-chartjs'
  import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, RadialLinearScale } from 'chart.js'

  ChartJS.register(Title, Tooltip, Legend, ArcElement, RadialLinearScale)

  const { subject, student } = $props<{
    subject: SubjectType
    student: UserType
  }>()

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
          display: true,
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
    // data
    const tempData = goalsForSubjectDecorated.map(goal => {
      const masteryValue = goal.observations.reduce(
        (max: number, observation: ObservationType) =>
          isNumber(observation.masteryValue) && observation.masteryValue > (max ?? -Infinity)
            ? observation.masteryValue
            : max,
        null as number | null
      )
      return masteryValue || 0
    })
    data.datasets[0].data = tempData

    // colors
    //data.datasets[0].backgroundColor = goalsForSubjectDecorated.map(goal => goal.displayColor)
    tempData.forEach(value => {
      const color = getMasteryLevelColorByValue(value, masterySchema.config?.levels, 0.5)
      data.datasets[0].backgroundColor.push(color)
    })

    // labels
    data.labels = goalsForSubjectDecorated.map(goal => goal.title)
    data = { ...data } // Trigger reactivity
  }

  $effect(() => {
    if (student && subject) {
      fetchGoals()
    }
  })
</script>

<div class="chart-container">
  <PolarArea {data} options={chartOptions} />
</div>

<style>
  .chart-container {
    padding: 2rem 0rem;
    height: 300px;
  }
</style>
