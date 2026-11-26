<script lang="ts">
  import CircleSVG from '../../assets/circle.svg.svelte'
  import CircleCheckSVG from '../../assets/circle-check.svg.svelte'

  let {
    allTags = [],
    selectedTags = [],
    onChange = () => {},
  }: {
    allTags: string[]
    selectedTags: string[]
    onChange: (tags: string[]) => void
  } = $props()

  const handleTagToggle = (tag: string) => {
    const newSelectedTags = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag]

    selectedTags = newSelectedTags
    onChange(newSelectedTags)
  }
</script>

<div class="tags-list">
  {#each allTags as tag}
    {@const isSelected = selectedTags.includes(tag)}
    <button
      type="button"
      class="tag"
      class:selected={isSelected}
      class:unselected={!isSelected}
      aria-pressed={isSelected}
      onclick={() => handleTagToggle(tag)}
    >
      {#if isSelected}
        <CircleCheckSVG />
      {:else}
        <CircleSVG />
      {/if}
      {tag}
    </button>
  {/each}
</div>

<style>
  .tags-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .tag {
    border: 2px solid #d8e0ea;
    border-radius: 3px;
    background: #fff;
    color: var(--bs-primary);
    padding: 0.35rem 0.75rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition:
      background-color 0.1s ease,
      border-color 0.1s ease,
      color 0.1s ease;
  }

  .tag:hover {
    border-color: #8eacd3;
    background: #eaf0f7;
  }

  .tag.selected {
    border-color: var(--bs-primary);
    background: var(--bs-primary);
    color: white;
  }

  .tag :global(svg) {
    width: 1.25em;
    height: 1.25em;
  }
</style>
