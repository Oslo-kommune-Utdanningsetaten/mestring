import type { MasteryConfigLevel, MasterySchemaConfig } from '../types/models'
import type { MasterySchemaReadable } from '../generated/types.gen'
import { isNumber } from './functions'

export type MasterySchemaWithConfig = MasterySchemaReadable & {
  config?: MasterySchemaConfig
}

export function useMasteryCalculations(masterySchema: MasterySchemaWithConfig | null) {
  const masteryLevels = masterySchema?.config?.levels || []
  const hasLevels = masteryLevels.length > 0

  const minValue = hasLevels ? Math.min(...masteryLevels.map(lev => lev.minValue)) : 0
  const maxValue = hasLevels ? Math.max(...masteryLevels.map(lev => lev.maxValue)) : 100
  const sliderValueIncrement = masterySchema?.config?.inputIncrement || 1
  const defaultValue = (minValue + maxValue) / 2

  const calculateSafeMasteryValue = (value: number | null | undefined): number => {
    if (value !== null && value !== undefined && isNumber(value)) return value as number
    return defaultValue
  }

  return {
    masteryLevels,
    minValue,
    maxValue,
    sliderValueIncrement,
    defaultValue,
    calculateSafeMasteryValue,
    hasLevels,
  }
}
