<script lang="ts">
  import { collapseTextChangeRangesAcrossMultipleVersions } from 'typescript'
  import type { GroupType } from '../generated/types.gen'
  import { GROUP_TYPE_BASIS, GROUP_TYPE_TEACHING } from '../utils/constants'
  import Link from './Link.svelte'
  import { is } from 'date-fns/locale'

  const {
    group,
    title,
    isTypeWarningEnabled,
    isGroupNameEnabled,
    isGroupTypeNameEnabled,
    onclick,
    href,
    classes,
  } = $props<{
    group: GroupType | null
    title?: string
    isTypeWarningEnabled?: boolean
    isGroupNameEnabled?: boolean
    isGroupTypeNameEnabled?: boolean
    onclick?: () => void
    href?: string
    classes?: string
  }>()

  const label: string = $derived(
    [
      isGroupNameEnabled ? group?.displayName : null,
      isGroupTypeNameEnabled
        ? group?.type === GROUP_TYPE_BASIS
          ? 'Basisgruppe'
          : 'Undervisningsgruppe'
        : null,
    ]
      .filter(Boolean)
      .join(' - ')
  )

  const skin: string = $derived(group.type === GROUP_TYPE_BASIS ? 'blue' : 'green')

  const isGroupTypeChanged = $derived.by(() => {
    // Inspect feideId to determine original group type
    const originalType =
      group.feideId.split(':')[3] === 'u' ? GROUP_TYPE_TEACHING : GROUP_TYPE_BASIS
    return originalType !== group.type
  })

  const accessibleLabel: string = $derived(
    isGroupTypeChanged && isTypeWarningEnabled ? `${label} (endret gruppetype)` : label
  )
</script>

{#if group}
  {#if onclick}
    <span class="button-container">
      <button
        type="button"
        class="p-0 m-0 border-0"
        title={title || label}
        {onclick}
        aria-label={accessibleLabel}
      >
        <pkt-tag iconName="group" {skin} class={classes}>
          <span>{label}</span>
          {#if isGroupTypeChanged && isTypeWarningEnabled}
            <span class="colored-icon">
              <pkt-icon
                name="alert-warning"
                class="pkt-icon--medium warning-icon"
                aria-hidden="true"
              ></pkt-icon>
            </span>
          {/if}
        </pkt-tag>
      </button>
    </span>
  {:else if href}
    <pkt-tag iconName="group" {skin} class={classes}>
      <Link to={href}>
        <span
          class={group.isEnabled ? '' : 'disabled'}
          title={group.isEnabled ? 'Enabled' : 'Disabled'}
        >
          {label}
        </span>
      </Link>
    </pkt-tag>
  {:else}
    <pkt-tag iconName="group" {skin} class={classes}>
      <span
        class={group.isEnabled ? '' : 'disabled'}
        title={group.isEnabled ? 'Enabled' : 'Disabled'}
      >
        {label}
      </span>
    </pkt-tag>
  {/if}
{/if}

<style>
  .button-container {
    display: inline-block;
    position: relative;
  }

  .warning-icon {
    position: absolute;
    top: 2px;
    right: -14px;
    z-index: 3;
    transform: rotate(5deg);
    filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.12)) drop-shadow(0 2px 2px rgba(0, 0, 0, 0.12))
      drop-shadow(0 4px 4px rgba(0, 0, 0, 0.12)) drop-shadow(0 8px 8px rgba(0, 0, 0, 0.12));
  }

  .colored-icon pkt-icon {
    --fg-color: var(--pkt-color-brand-red-1000);
  }

  button {
    background: none;
    cursor: pointer;
  }

  button:hover {
    transform: scale(1.1);
    transition: transform 0.3s ease;
  }

  .disabled {
    text-decoration: line-through;
    text-decoration-thickness: 3px;
    text-decoration-color: color-mix(in srgb, var(--pkt-color-brand-red-1000) 80%, transparent);
    opacity: 0.7;
  }
</style>
