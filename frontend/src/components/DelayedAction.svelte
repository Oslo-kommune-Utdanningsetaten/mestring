<script lang="ts">
  interface Props {
    onAction: () => void
    onAbort: () => void
    delay?: number
    title?: string
  }

  const defaultDelay = 10
  const defaultTitle = 'Klikk for å avbryte'

  const { onAction, delay = defaultDelay, title = defaultTitle, onAbort }: Props = $props()

  let secondsLeft = $state(0)
  let intervalId: ReturnType<typeof setInterval> | null = $state(null)
  let isActive = $state(false)

  const startCountdown = () => {
    intervalId = setInterval(() => {
      secondsLeft--
      if (secondsLeft <= 0) {
        clearCountdown()
        isActive = false
        onAction()
      }
    }, 1000)
  }

  const clearCountdown = () => {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  const abort = () => {
    clearCountdown()
    isActive = false
    secondsLeft = 0
    onAbort()
  }

  $effect(() => {
    secondsLeft = delay
    isActive = true
    startCountdown()
  })
</script>

{#if isActive}
  <button
    class="delayed-action"
    {title}
    aria-label={title}
    onclick={abort}
    onkeydown={e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        abort()
      }
    }}
  >
    Slettes om {secondsLeft}
  </button>
{/if}

<style>
  .delayed-action {
    height: 32px;
    width: 100px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 0.7rem;
    white-space: nowrap;
    cursor: pointer;
    border: 1px solid var(--bs-gray);
    border-radius: 3px;
    background-color: var(--pkt-color-signal-red-100, #fde8e8);
    color: var(--pkt-color-signal-red-700, #c30000);
    padding: 0 4px;
    margin-left: 8px;
    transition: background-color 0.2s;
  }

  .delayed-action:hover {
    background-color: var(--pkt-color-grays-gray-100, #f0f0f0);
    color: inherit;
  }
</style>
