import type { MasterySchemaWithConfig, MasteryConfigLevel } from '../types/models'
import { isNumber } from './functions'

export const getMasteryColorByValue = (value: number, masteryLevels: any[]): string => {
  const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
  return masteryLevel ? masteryLevel.color : 'black'
}

export function useMasteryCalculations(masterySchema: MasterySchemaWithConfig | null) {
  const masteryLevels = masterySchema?.config?.levels || []
  const hasLevels = masteryLevels.length > 0

  const minValue = hasLevels
    ? Math.min(...masteryLevels.map((lev: MasteryConfigLevel) => lev.minValue))
    : 0
  const maxValue = hasLevels
    ? Math.max(...masteryLevels.map((lev: MasteryConfigLevel) => lev.maxValue))
    : 100
  const sliderValueIncrement = masterySchema?.config?.inputIncrement || 1
  const defaultValue = Math.floor((minValue + maxValue) / 2)
  const deltaValue = maxValue - minValue
  const flatTrendThreshold = masterySchema?.config?.flatTrendThreshold || 1

  const calculateSafeMasteryValue = (value: number | null | undefined): number => {
    let result: number = defaultValue
    if (value !== null && value !== undefined && isNumber(value)) {
      result = value
    }
    return Number(result.toFixed(0))
  }

  return {
    masteryLevels,
    minValue,
    maxValue,
    deltaValue,
    sliderValueIncrement,
    defaultValue,
    calculateSafeMasteryValue,
    flatTrendThreshold,
    hasLevels,
  }
}
