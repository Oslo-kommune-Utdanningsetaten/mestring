<script lang="ts">
  import { getISOWeek } from 'date-fns'
  import type { GroupType, ObservationType } from '../generated'
  import { observationsList } from '../generated/sdk.gen'
  import BarChart from './BarChart.svelte'

  interface Props {
    group: GroupType
    width?: number
    height?: number
    title?: string
  }

  // Props with sane defaults
  const { group, width = 200, height = 100, title: providedTitle }: Props = $props()

  let observations = $state<ObservationType[]>([])
  let data = $state<number[]>([])
  let hasSufficientData = $derived(
    Array.isArray(data) && data.length > 0 && data.every(n => Number.isFinite(n))
  )
  const title = $derived(providedTitle ?? (hasSufficientData ? data.join(', ') : 'Mangler data'))
  const fromDate = $derived.by(() => {
    const now = new Date()
    return now.getMonth() < 7 ? `${now.getFullYear()}-01-01` : `${now.getFullYear() - 1}-08-01`
  })
  let xLabels = $state<string[]>([])

  const fetchObservations = async () => {
    const obsResults = await observationsList({
      query: { group: group.id, from: fromDate },
    })
    observations = obsResults.data || []
    // group observations by week number, counting how many observations fall into each week
    const obsByWeek: Record<number, number> = {}
    observations.forEach(obs => {
      const week = getISOWeek(new Date(obs.observedAt || obs.createdAt))
      obsByWeek[week] = (obsByWeek[week] || 0) + 1
    })
    console.log('Observations by week:', obsByWeek)
    const beginAtWeek = getISOWeek(new Date(fromDate))
    const endAtWeek = getISOWeek(new Date())
    for (let week = beginAtWeek; week <= endAtWeek; week++) {
      data.push(obsByWeek[week] || 0)
      xLabels.push(`${week}`)
    }
  }

  $effect(() => {
    fetchObservations()
  })
</script>

<BarChart {data} yMaxValue={10} yResolution={1} {width} {height} {title} {xLabels}></BarChart>

<style>
</style>
