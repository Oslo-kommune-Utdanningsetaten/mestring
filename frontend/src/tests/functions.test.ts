import { describe, it, expect, assert } from 'vitest'
import { inferMastery, aggregateMasterys } from '../utils/functions'
import type { ObservationType } from '../generated/types.gen'
import type { GoalDecorated } from '../types/models'

// Minimal observation factory
const createObservation = (
  masteryValue: number | null | undefined,
  createdAt: string
): ObservationType => ({
  id: crypto.randomUUID(),
  createdAt,
  updatedAt: createdAt,
  maintainedAt: null,
  createdById: 'user-1',
  updatedById: 'user-1',
  goalId: 'goal-1',
  studentId: 'student-1',
  masteryValue,
})

// Minimal GoalDecorated factory
const createGoal = (masteryData: GoalDecorated['masteryData']): GoalDecorated => ({
  id: crypto.randomUUID(),
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
  maintainedAt: null,
  createdById: 'user-1',
  updatedById: 'user-1',
  groupId: 'group-1',
  masterySchemaId: 'schema-1',
  title: 'Goal',
  sortOrder: 0,
  isIndividual: false,
  isRelevant: true,
  masteryData,
})

// inferMastery
describe('inferMastery', () => {
  it('returns null for an empty observations array', () => {
    expect(inferMastery([])).toBeNull()
  })

  it('returns mastery equal to the single observation value', () => {
    const result = inferMastery([createObservation(3, '2024-01-01T00:00:00Z')])
    assert(result !== null)
    expect(result.mastery).toBe(3)
  })

  it('returns the latest observation value as mastery', () => {
    const obs = [
      createObservation(2, '2024-01-01T00:00:00Z'),
      createObservation(4, '2024-01-03T00:00:00Z'),
      createObservation(3, '2024-01-02T00:00:00Z'), // intentionally out of order
    ]
    const result = inferMastery(obs)
    assert(result !== null)
    expect(result.mastery).toBe(4)
    expect(result.observationValues).toEqual([2, 3, 4])
  })

  it('includes all numeric masteryValues in observationValues', () => {
    const obs = [
      createObservation(1, '2024-01-01T00:00:00Z'),
      createObservation(null, '2024-01-02T00:00:00Z'), // should be filtered out
      createObservation(3, '2024-01-03T00:00:00Z'),
    ]
    const result = inferMastery(obs)
    assert(result !== null)
    expect(result.observationValues).toEqual([1, 3])
  })

  it('returns trend 0 when there is only one numeric observation', () => {
    const result = inferMastery([createObservation(5, '2024-01-01T00:00:00Z')])
    assert(result !== null)
    expect(result.trend).toBe(0)
  })

  it('returns a positive trend for an increasing sequence', () => {
    const obs = [
      createObservation(1, '2024-01-01T00:00:00Z'),
      createObservation(3, '2024-01-02T00:00:00Z'),
      createObservation(5, '2024-01-03T00:00:00Z'),
    ]
    const result = inferMastery(obs)
    assert(result !== null)
    expect(result.trend).toBeGreaterThan(0)
  })

  it('returns a negative trend for a decreasing sequence', () => {
    const obs = [
      createObservation(5, '2024-01-01T00:00:00Z'),
      createObservation(3, '2024-01-02T00:00:00Z'),
      createObservation(1, '2024-01-03T00:00:00Z'),
    ]
    const result = inferMastery(obs)
    assert(result !== null)
    expect(result.trend).toBeLessThan(0)
  })

  it('returns trend 0 for a flat sequence', () => {
    const obs = [
      createObservation(3, '2024-01-01T00:00:00Z'),
      createObservation(3, '2024-01-02T00:00:00Z'),
      createObservation(3, '2024-01-03T00:00:00Z'),
    ]
    const result = inferMastery(obs)
    assert(result !== null)
    expect(result.trend).toBe(0)
  })

  it('handles observations where masteryValue is undefined', () => {
    const obs = [
      createObservation(undefined, '2024-01-01T00:00:00Z'),
      createObservation(4, '2024-01-02T00:00:00Z'),
    ]
    const result = inferMastery(obs)
    assert(result !== null)
    expect(result.mastery).toBe(4)
    expect(result.observationValues).toEqual([4])
  })
})

// aggregateMasterys
describe('aggregateMasterys', () => {
  it('returns null when the goals array is empty', () => {
    expect(aggregateMasterys([])).toBeNull()
  })

  it('returns null when no goal has mastery data', () => {
    const goals = [createGoal(null), createGoal(undefined)]
    expect(aggregateMasterys(goals)).toBeNull()
  })

  it('returns the single goal mastery value when there is one goal', () => {
    const goals = [createGoal({ mastery: 4, trend: 1, observationValues: [4] })]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.mastery).toBe(4)
    expect(result.trend).toBe(1)
  })

  it('averages mastery values across goals', () => {
    const goals = [
      createGoal({ mastery: 2, trend: 0, observationValues: [2] }),
      createGoal({ mastery: 4, trend: 0, observationValues: [4] }),
    ]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.mastery).toBe(3)
  })

  it('averages trend values across goals', () => {
    const goals = [
      createGoal({ mastery: 3, trend: -1, observationValues: [3] }),
      createGoal({ mastery: 3, trend: 3, observationValues: [3] }),
    ]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.trend).toBe(1)
  })

  it('sets observationValues to the list of individual goal mastery values', () => {
    const goals = [
      createGoal({ mastery: 1, trend: 0, observationValues: [1] }),
      createGoal({ mastery: 5, trend: 0, observationValues: [5] }),
    ]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.observationValues).toStrictEqual([1, 5])
  })

  it('sets goalsCount to the total number of goals passed in', () => {
    const goals = [
      createGoal({ mastery: 2, trend: 0, observationValues: [2] }),
      createGoal({ mastery: 4, trend: 0, observationValues: [4, 3] }),
      createGoal(null), // no masteryData, but still counts toward goalsCount
    ]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.goalsCount).toBe(3)
    expect(result.observationValues).toStrictEqual([2, 4, 3]) // flattened list of all observationValues
  })

  it('ignores goals without mastery data when computing averages', () => {
    const goals = [createGoal({ mastery: 6, trend: 2, observationValues: [6] }), createGoal(null)]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    // Only one goal with real data – averages equal that goal's values
    expect(result.mastery).toBe(6)
    expect(result.trend).toBe(2)
  })

  it('returns trend 0 when no goal has trend data', () => {
    const goals = [createGoal({ mastery: 3, trend: 0, observationValues: [3] })]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.trend).toBe(0)
  })
})

// infer + aggregate in concert
describe('infer + aggregate masterys', () => {
  it('feeds masteryData from inferMastery into aggregateMasterys', () => {
    const goal1Observations = [
      createObservation(2, '2024-01-01T00:00:00Z'),
      createObservation(4, '2024-01-02T00:00:00Z'),
    ]
    const goal2Observations = [
      createObservation(5, '2024-01-01T00:00:00Z'),
      createObservation(1, '2024-01-02T00:00:00Z'),
    ]
    const masteryData1 = inferMastery(goal1Observations)
    const masteryData2 = inferMastery(goal2Observations)
    assert(masteryData1 !== null)
    assert(masteryData2 !== null)
    assert(masteryData1.observationValues !== null && masteryData1.observationValues.length > 0)
    assert(masteryData2.observationValues !== null && masteryData2.observationValues.length > 0)
    expect(masteryData1.mastery).toBe(4)
    expect(masteryData2.mastery).toBe(1)
    expect(masteryData1.trend).toBeGreaterThan(0)
    expect(masteryData2.trend).toBeLessThan(0)
    const goals = [createGoal(masteryData1), createGoal(masteryData2)]
    const result = aggregateMasterys(goals)
    assert(result !== null)
    expect(result.goalsCount).toBe(2)
    expect(result.observationValues).toStrictEqual([2, 4, 5, 1]) // flattened list of all observationValues
    expect(result.mastery).toBe((masteryData1.mastery + masteryData2.mastery) / 2) // mastery average
    expect(result.trend).toBe((masteryData1.trend + masteryData2.trend) / 2) // trend average
  })
})
