<script lang="ts">
  import { dataStore } from '../stores/data'
  import { USER_ROLES } from '../utils/constants'
  import { t } from '../stores/translations'

  const {
    roleNames,
    options = {},
  }: {
    roleNames: string[]
    options?: Record<string, any>
  } = $props()

  const { currentSchool } = $derived($dataStore)
  const { teacherType } = options
</script>

{#if roleNames.includes(USER_ROLES.TEACHER) && teacherType === 'teaching'}
  <span>
    <span class="fw-bold">Lærer i undervisningsgruppe</span>
    kan opprette {t('goal', { form: 'plu-indef' })} og {t('observation', { form: 'plu-indef' })} for elevene
    i sin undervisningsgruppe.
  </span>
{/if}

{#if roleNames.includes(USER_ROLES.TEACHER) && teacherType === 'basis'}
  <span>
    <span class="fw-bold">Lærer i basisgruppe</span>
    kan se {t('goal', { form: 'plu-indef' })} og {t('observation', { form: 'plu-indef' })} for sine elever,
    i alle fag. Kan opprette individuelle {t('goal', { form: 'plu-indef' })} (og
    {t('observation', { form: 'plu-indef' })}
    på disse) for sine elever i alle fag.
  </span>
{/if}

{#if roleNames.includes(USER_ROLES.INSPECTOR)}
  <span>
    <span class="fw-bold">Skoleinspektør</span>
    kan se {t('goal', { form: 'plu-indef' })} og {t('observation', { form: 'plu-indef' })} for alle elever
    ved {currentSchool ? currentSchool.displayName : 'sin skole'}. Kan se og endre enkelte
    innstillinger for skolen.
  </span>
{/if}

{#if roleNames.includes(USER_ROLES.ADMIN)}
  <span>
    <span class="fw-bold">Skoleadmin</span>
    kan se og redigere {t('goal', { form: 'plu-indef' })} og {t('observation', {
      form: 'plu-indef',
    })} for alle elever ved {currentSchool ? currentSchool.displayName : 'sin skole'}. Kan se og
    endre enkelte innstillinger for skolen.
  </span>
{/if}

{#if roleNames.includes(USER_ROLES.SUPERADMIN)}
  <span>
    <span class="fw-bold">Superadmin</span>
    kan se og redigere {t('goal', { form: 'plu-indef' })} og {t('observation', {
      form: 'plu-indef',
    })} for alle elever ved alle skoler. Kan endre innstillinger for skolene.
  </span>
{/if}

<style>
</style>
