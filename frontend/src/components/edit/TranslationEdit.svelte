<script lang="ts">
  import '@oslokommune/punkt-elements/dist/pkt-icon.js'
  import { JSONEditor, type Content, Mode } from 'svelte-jsoneditor'
  import type { SchoolType } from '../../generated/types.gen'
  import { schoolsUpdate } from '../../generated/sdk.gen'

  import ButtonMini from '../ButtonMini.svelte'

  const { school, onDone } = $props<{
    school: SchoolType
    onDone: () => void
  }>()
  let localSchool = $state<SchoolType>({ ...school })
  let editorContent = $state<Content>({
    json: localSchool?.uiTranslations || {},
  })

  const handleSave = async () => {
    try {
      if ('json' in editorContent) {
        localSchool.uiTranslations = editorContent.json as Content
      } else if ('text' in editorContent) {
        localSchool.uiTranslations = JSON.parse(editorContent.text) as Content
      }
    } catch (error) {
      console.error('Invalid JSON in editor:', error)
      return
    }
    try {
      await schoolsUpdate({
        path: { id: localSchool.id },
        body: localSchool as SchoolType,
      })
      onDone()
    } catch (error) {
      console.error('Error updating school:', error)
    }
  }
</script>

<div class="p-4 translations-edit">
  <h3 class="pb-2">Rediger oversettelser</h3>

  <div style="height: 40vh;">
    <JSONEditor bind:content={editorContent} mode={Mode.text} />
  </div>

  <div class="d-flex gap-2 justify-content-start">
    <ButtonMini
      options={{
        title: 'Lagre',
        iconName: 'check',
        skin: 'primary',
        variant: 'label-only',
        classes: 'mt-3',
        onClick: () => handleSave(),
      }}
    >
      Lagre
    </ButtonMini>

    <ButtonMini
      options={{
        title: 'Avbryt',
        iconName: 'close',
        skin: 'secondary',
        variant: 'label-only',
        classes: 'mt-3 ms-3',
        onClick: () => onDone(),
      }}
    >
      Avbryt
    </ButtonMini>
  </div>
</div>

<style>
  .translations-edit {
    width: 100%;
    max-width: 100%;
  }
</style>
