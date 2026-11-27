import { randomInt } from 'node:crypto';

export const baseUrl = (
  process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5000'
).replace(/\/$/, '');

export function uniqueLetters(length = 8): string {
  return Array.from({ length }, () =>
    String.fromCharCode(65 + randomInt(26))
  ).join('');
}
