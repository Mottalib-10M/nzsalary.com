/** Mini-simulateurs des guides (RECETTE §9.3) : un par sujet, calculés par le moteur néo-zélandais. */
import { compute, accLevy, ietc, incomeTax, marginalRate, contractor, secondaryCode, holidayPay } from './engine/nz';
import P from '../data/params-2026.json';
import { formatMoney as $, formatPercent as pct } from './format';
import type { MiniSpec } from './mini-types';

const salary = (def = 65000) => ({ id: 's', label: 'Salary or wages per year', def, unit: '$', max: 5000000 });
const A = (g: number, o: Record<string, unknown> = {}) => compute({ gross: g, ...o } as Parameters<typeof compute>[0]).annual;
const KS = [{ value: '0.03', label: '3 %' }, { value: '0.035', label: '3.5 %' }, { value: '0.04', label: '4 %' }, { value: '0.06', label: '6 %' }, { value: '0.08', label: '8 %' }, { value: '0.1', label: '10 %' }];

const SPECS: Record<string, MiniSpec> = {
  acc: { title: 'Work out your ACC earners’ levy', cta: 'Full PAYE calculator', inputs: [salary()], run: ({ s }) => {
    const a = accLevy(s); return { head: ['ACC earners’ levy for 2026-27', $(a)], rows: [['Rate', pct(P.acc.rate, 2)], ['Maximum liable earnings', $(P.acc.max_liable)], ['Per week', $(a / 52, 2)]] };
  } },
  average: { title: 'Compare your pay with the median', cta: 'Take-home pay calculator', inputs: [salary(Math.round(P.stats.median_hourly_jun2026 * 40 * 52))], run: ({ s }) => {
    const ft = P.stats.median_hourly_jun2026 * 40 * 52; const d = s / ft - 1; const a = A(s, { kiwisaver: 0.035 });
    return { head: ['Take-home pay per week', $(a.takeHome / 52)], rows: [['Against the full-time median', `${d >= 0 ? '+' : '−'}${pct(Math.abs(d), 0)}`], ['Take-home per year', $(a.takeHome)], ['PAYE and ACC per year', $(a.paye + a.acc)]] };
  } },
  contractorVs: { title: 'Employee or contractor: what you keep', cta: 'Contractor tax calculator', inputs: [{ id: 'f', label: 'Contract fees per year', def: 90000, unit: '$', max: 5000000 }, { id: 'e', label: 'Business expenses', def: 5000, unit: '$', max: 5000000 }], run: ({ f, e }) => {
    const c = contractor({ fees: f, expenses: e, rate: 0.2 }); const net = f - e - c.tax - c.acc;
    return { head: ['Kept as a contractor', $(net)], rows: [['Income tax on the profit', $(c.tax)], ['ACC levy', $(c.acc)], ['Same amount as a salary, take-home', $(A(f).takeHome)]], note: 'The contractor has no paid leave, no employer KiwiSaver and must pay ACC and provisional tax.' };
  } },
  holiday: { title: 'Your 8 % holiday pay after tax', cta: 'Holiday pay calculator', inputs: [{ id: 'e', label: 'Gross earnings the 8 % is paid on', def: 20000, unit: '$', max: 5000000 }, salary(52000)], run: ({ e, s }) => {
    const h = holidayPay({ earnings: e, annualPay: s }); return { head: ['Holiday pay after PAYE', $(h.net)], rows: [['Holiday pay at 8 %', $(h.pay)], ['Extra-pay rate with ACC', pct(h.rate, 2)], ['PAYE and ACC', $(h.paye)]] };
  } },
  tax: { title: 'Income tax on your income', cta: 'Income tax calculator', inputs: [salary()], run: ({ s }) => {
    const t = incomeTax(s); return { head: ['Income tax for 2026-27', $(t)], rows: [['Marginal rate', pct(marginalRate(s), 1)], ['Average rate', pct(s ? t / s : 0, 1)], ['Plus ACC levy', $(accLevy(s))]] };
  } },
  ietc: { title: 'Do you qualify for the IETC?', cta: 'PAYE calculator with the ME code', inputs: [salary(66000)], run: ({ s }) => {
    const c = ietc(s); return { head: ['Independent earner tax credit', $(c)], rows: [['Full credit between', `${$(P.ietc.min_income)} and ${$(P.ietc.abate_from)}`], ['Reduced by 13 c per $1 above', $(P.ietc.abate_from)], ['Per week with the ME code', $(c / 52, 2)]] };
  } },
  ks: { title: 'Your KiwiSaver at the new rates', cta: 'KiwiSaver calculator', inputs: [salary(), { id: 'r', label: 'Your contribution rate', def: 0.035, options: KS }], run: ({ s, r }) => {
    const a = A(s, { kiwisaver: r }); return { head: ['Into your KiwiSaver per year', $(a.kiwisaver + a.employerKsNet + a.govtContribution)], rows: [['You', $(a.kiwisaver)], ['Employer after ESCT', $(a.employerKsNet)], ['Government contribution', $(a.govtContribution)]] };
  } },
  minwage: { title: 'Minimum wage take-home pay', cta: 'Hourly to salary calculator', inputs: [{ id: 'h', label: 'Hours a week', def: 40, unit: 'h', max: 80 }], run: ({ h }) => {
    const g = P.min_wage.adult * h * 52; const a = A(g); return { head: ['Take-home per week', $(a.takeHome / 52)], rows: [['Hourly rate', $(P.min_wage.adult, 2)], ['Gross per week', $(g / 52)], ['Gross per year', $(g)]] };
  } },
  paye: { title: 'PAYE on one weekly pay', cta: 'Take-home pay calculator', inputs: [{ id: 'w', label: 'Gross pay per week', def: 1250, unit: '$', max: 100000 }], run: ({ w }) => {
    const p = compute({ gross: w * 52, period: 'weekly' }).perPeriod; return { head: ['Take-home this week', $(p.takeHome)], rows: [['PAYE', $(p.paye)], ['ACC levy', $(p.acc)], ['Tax code', 'M, no KiwiSaver']] };
  } },
  selfemp: { title: 'Tax on your self-employed profit', cta: 'Contractor tax calculator', inputs: [{ id: 'p', label: 'Profit for the year', def: 70000, unit: '$', max: 5000000 }], run: ({ p }) => {
    const t = incomeTax(p); const a = accLevy(p); return { head: ['Income tax and ACC', $(t + a)], rows: [['Income tax', $(t)], ['ACC earners’ levy', $(a)], ['Kept after both', $(p - t - a)]] };
  } },
  secondary: { title: 'Which tax code for a second job?', cta: 'Secondary tax calculator', inputs: [{ id: 'm', label: 'Main job, per year', def: 50000, unit: '$', max: 5000000 }, { id: 'x', label: 'Second job, per year', def: 15000, unit: '$', max: 5000000 }], run: ({ m, x }) => {
    const code = secondaryCode(m + x); const r = compute({ gross: x, code }).annual;
    return { head: ['Tax code for the second job', code], rows: [['Total income', $(m + x)], ['PAYE on the second job', $(r.paye)], ['Take-home from the second job', $(r.takeHome)]] };
  } },
};

export function getSpec(kind: string, _lang?: string): MiniSpec {
  const s = SPECS[kind]; if (!s) throw new Error(`Mini-simulateur inconnu : ${kind}`); return s;
}
