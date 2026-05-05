/**
 * SPICE-style unit parser
 * Converts strings like "100u", "1n", "2.5M" to their numeric values.
 */

const UNIT_MULTIPLIERS: Record<string, number> = {
  't': 1e12,
  'g': 1e9,
  'meg': 1e6,
  'k': 1e3,
  'm': 1e-3,
  'u': 1e-6,
  'n': 1e-9,
  'p': 1e-12,
  'f': 1e-15,
  'a': 1e-18,
};

/**
 * Checks if a string is a valid SPICE-style value.
 * @param value The string to validate
 */
export function isValidSpiceValue(value: string | number): boolean {
  if (typeof value === 'number') return !isNaN(value);
  if (!value) return false;

  const trimmed = value.trim().toLowerCase();
  if (!trimmed) return false;

  // Match number followed by optional unit (meg, t, g, k, m, u, n, p, f, a)
  // Must end after the optional unit, no extra characters allowed
  const match = trimmed.match(/^([-+]?\d*\.?\d+(?:[e][-+]?\d+)?)(meg|[tgkmunpfa])?$/);
  
  return !!match;
}

/**
 * Parses a SPICE-style value string into a number.
 * If input is already a number, returns it.
 */
export function parseSpiceValue(value: string | number): number {
  if (typeof value === 'number') return value;
  if (!value) return 0;

  const trimmed = value.trim().toLowerCase();
  if (!trimmed) return 0;

  // Match number followed by optional unit
  const match = trimmed.match(/^([-+]?\d*\.?\d+(?:[e][-+]?\d+)?)(meg|[tgkmunpfa])?.*$/);
  
  if (!match) {
    const parsed = parseFloat(trimmed);
    return isNaN(parsed) ? 0 : parsed;
  }

  const numPart = parseFloat(match[1]);
  const unitPart = match[2];

  if (unitPart && UNIT_MULTIPLIERS[unitPart]) {
    return numPart * UNIT_MULTIPLIERS[unitPart];
  }

  return numPart;
}
