import { describe, expect, it } from 'vitest'
import { riskColor } from './risk'

describe('risk presentation', () => {
  it('maps every operational level to a semantic color', () => {
    expect(riskColor('LOW')).toBe('#42b58b')
    expect(riskColor('MODERATE')).toBe('#eebd4d')
    expect(riskColor('HIGH')).toBe('#ed8b4d')
    expect(riskColor('CRITICAL')).toBe('#e25050')
  })
})
