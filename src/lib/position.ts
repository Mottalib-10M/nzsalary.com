/** Places an annual salary against Stats NZ's median hourly earnings, at 40 hours a week. */
import P from '../data/params-2026.json';
import { formatMoney, formatPercent } from './format';
const S = P.stats;
export const FT_MEDIAN = Math.round(S.median_hourly_jun2026 * 40 * 52);
export function position(annual: number): string {
  const x = annual / FT_MEDIAN - 1;
  const rel = Math.abs(x) < 0.005 ? 'about the same as' : `${formatPercent(Math.abs(x), 0)} ${x > 0 ? 'more than' : 'less than'}`;
  return `Stats NZ put median hourly earnings at ${formatMoney(S.median_hourly_jun2026, 2)} in the June 2026 quarter, which is ${formatMoney(FT_MEDIAN)} a year for a 40-hour week. A salary of ${formatMoney(Math.round(annual))} is ${rel} that full-time equivalent of the median${x > 0 ? ', so it pays better than the typical hourly rate' : x < 0 ? ', so it pays below the typical hourly rate' : ''}. Median weekly earnings for all wage earners, part-time included, are lower at ${formatMoney(S.median_weekly_wages_jun2026)} a week.`;
}
