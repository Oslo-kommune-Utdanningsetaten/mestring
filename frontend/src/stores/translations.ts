import { derived, get } from 'svelte/store'
import { currentSchool } from './data'

type FormOptions = 'sin-indef' | 'sin-def' | 'plu-indef' | 'plu-def'

type TranslationOptions = {
  form?: FormOptions
  capitalize?: boolean
}

const defaultTranslations: Record<string, any> = {
  goal: {
    'sin-indef': 'mål',
    'sin-def': 'målet',
    'plu-indef': 'mål',
    'plu-def': 'målene',
  },
  observation: {
    'sin-indef': 'observasjon',
    'sin-def': 'observasjonen',
    'plu-indef': 'observasjoner',
    'plu-def': 'observasjonene',
  },
  status: {
    'sin-indef': 'status',
    'sin-def': 'statusen',
    'plu-indef': 'statuser',
    'plu-def': 'statusene',
  },
}

const schoolUITranslations = derived(
  currentSchool,
  $currentSchool => $currentSchool?.uiTranslations ?? {}
)

const capitalizeString = (item: string): string => {
  return item.charAt(0).toUpperCase() + item.slice(1)
}

// Accepts a key and options, returns a translated string (based on school or default translations)
// If no translation is found, returns the key itself
export const t = (key: string, options?: TranslationOptions): string => {
  if (!key) throw new Error('Translation key is required')
  const { form, capitalize } = options ?? {}
  const schoolTranslations = get(schoolUITranslations)

  const phraseLookup: Record<string, string> | string =
    schoolTranslations[key] || defaultTranslations[key] || {}

  let result: string
  if (form && typeof phraseLookup === 'object') {
    // object
    result = phraseLookup[form]
  } else if (typeof phraseLookup === 'string' || phraseLookup instanceof String) {
    // string
    result = phraseLookup as string
  } else {
    // if no translation is found, use key itself
    result = key + '(' + form + ')'
  }

  if (capitalize) {
    result = capitalizeString(result)
  }
  return result
}
