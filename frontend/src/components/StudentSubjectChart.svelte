<script lang="ts">
  import { useTinyRouter } from 'svelte-tiny-router'
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { dataStore } from '../stores/data'
  import type {
    UserType,
    ObservationType,
    GoalType,
    StatusType,
    SubjectType,
  } from '../generated/types.gen'
  import type { GoalDecorated } from '../types/models'
  import { observationsDestroy, goalsDestroy, goalsUpdate, goalsCreate } from '../generated/sdk.gen'
  import Link from './Link.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge.svelte'
  import MasteryBarChart from './MasteryBarChart.svelte'
  import ButtonMini from './ButtonMini.svelte'
  import ButtonIcon from './ButtonIcon.svelte'
  import Statuses from './Statuses.svelte'
  import AuthorInfo from './AuthorInfo.svelte'
  import { localStorage } from '../stores/localStorage'
  import { fetchGoalsForSubjectAndStudent, urlStringFrom } from '../utils/functions'
  import { hasUserAccessToFeature } from '../stores/access'
  import { addAlert } from '../stores/alerts'
  import { trackEvent } from '../stores/analytics'

  const { subject, student } = $props<{
    subject: SubjectType
    student: UserType
    onRefreshRequired?: Function
  }>()

  const router = useTinyRouter()

  let { masterySchemas, currentSchool, currentUser } = $derived($dataStore)
  let goalsForSubject = $state<GoalDecorated[]>([])
  let statusesKey = $state<number>(0) // key used to force re-render of Statuses component

  const getMasterySchmemaForGoal = (goal: GoalType) => {
    return masterySchemas.find(ms => ms.id === goal.masterySchemaId)
  }

  const fetchGoals = async () => {
    goalsForSubject = await fetchGoalsForSubjectAndStudent(
      subject.id,
      student.id,
      currentSchool?.id!,
      currentUser.allGroups
    )
  }

  $effect(() => {
    if (student && subject) {
      fetchGoals()
    }
  })
</script>

<div class="mt-2">
  <hr />
  <h3>
    Chart: {student.name} @ {subject.shortName || subject.displayName}
  </h3>
  <hr />
</div>

<style>
  h3 {
    font-size: 1.5rem;
  }
</style>
