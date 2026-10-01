/** Mini-simulateurs des guides (RECETTE §9.3) : un par sujet, calculés par le moteur néo-zélandais. */
import { compute, accLevy, ietc, incomeTax, marginalRate, contractor, secondaryCode, holidayPay, bonus, redundancy, gstAdd, gstRemove, payRise, publicHolidayPay, overtime, finalPay, rwt, provisional, superAfterTax, hourlyToAnnual } from './engine/nz';
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
  bonus: { title: 'Your bonus after tax', cta: 'Take-home pay calculator', inputs: [{ id: 'b', label: 'Bonus before tax', def: 5000, unit: '$', max: 5000000 }, salary(70000)], run: ({ b, s }) => {
    const x = bonus({ amount: b, annualPay: s, kiwisaver: 0.035 }); return { head: ['Bonus in your bank account', $(x.net)], rows: [['Extra-pay rate with ACC', pct(x.rate, 2)], ['PAYE and ACC', $(x.paye)], ['KiwiSaver at 3.5 %', $(x.kiwisaver)]] };
  } },
  redundancy: { title: 'Your redundancy pay after tax', cta: 'Take-home pay calculator', inputs: [{ id: 'r', label: 'Redundancy payment before tax', def: 20000, unit: '$', max: 5000000 }, salary(70000)], run: ({ r, s }) => {
    const x = redundancy({ amount: r, annualPay: s }); return { head: ['Redundancy pay you keep', $(x.net)], rows: [['PAYE rate on the payment', pct(x.rate, 1)], ['PAYE deducted', $(x.paye)], ['ACC levy and KiwiSaver', $(0)]] };
  } },
  gst: { title: 'Add or remove 15 % GST', cta: 'Contractor tax calculator', inputs: [{ id: 'a', label: 'Amount', def: 1000, unit: '$', max: 100000000, decimals: 2 }, { id: 'm', label: 'The amount is', def: 0, options: [{ value: '0', label: 'GST exclusive (add GST)' }, { value: '1', label: 'GST inclusive (remove GST)' }] }], run: ({ a, m }) => {
    const x = m === 1 ? gstRemove(a) : gstAdd(a); return { head: [m === 1 ? 'Price excluding GST' : 'Price including GST', $(m === 1 ? x.excl : x.incl, 2)], rows: [['GST at 15 %', $(x.gst, 2)], ['GST exclusive', $(x.excl, 2)], ['GST inclusive', $(x.incl, 2)]] };
  } },
  payrise: { title: 'What your pay rise leaves after tax', cta: 'Take-home pay calculator', inputs: [salary(), { id: 'p', label: 'Pay rise', def: 4, unit: '%', max: 200, decimals: 1 }], run: ({ s, p }) => {
    const x = payRise({ gross: s, percent: p / 100, kiwisaver: 0.035 }); return { head: ['Extra take-home per week', $(x.extraNet / 52, 2)], rows: [['New salary', $(x.newGross)], ['Extra before tax per year', $(x.extraGross)], ['Extra take-home per year', $(x.extraNet)], ['Share of the rise you keep', pct(x.kept, 0)]] };
  } },
  pubhol: { title: 'Pay for working a public holiday', cta: 'Hourly to salary calculator', inputs: [{ id: 'h', label: 'Hourly rate', def: 30, unit: '$', max: 2000, decimals: 2 }, { id: 'n', label: 'Hours worked that day', def: 8, unit: 'h', max: 24, decimals: 1 }], run: ({ h, n }) => {
    const x = publicHolidayPay({ hourly: h, hours: n }); return { head: ['Pay for the day at time and a half', $(x.pay, 2)], rows: [['Ordinary pay for those hours', $(x.ordinary, 2)], ['Premium for the public holiday', $(x.premium, 2)], ['Value of the alternative holiday', $(x.alternativeDay, 2)]], note: 'The alternative holiday applies only if the day would otherwise be a working day for you.' };
  } },
  overtime: { title: 'Overtime pay after tax', cta: 'Hourly to salary calculator', inputs: [{ id: 'h', label: 'Hourly rate', def: 30, unit: '$', max: 2000, decimals: 2 }, { id: 'o', label: 'Overtime hours a week', def: 5, unit: 'h', max: 60, decimals: 1 }, { id: 'm', label: 'Overtime rate in your agreement', def: 1.5, options: [{ value: '1', label: 'Ordinary rate (T1)' }, { value: '1.5', label: 'Time and a half (T1.5)' }, { value: '2', label: 'Double time (T2)' }] }], run: ({ h, o, m }) => {
    const x = overtime({ hourly: h, hoursPerWeek: 40, overtimeHours: o, multiplier: m }); return { head: ['Overtime in hand per week', $(x.netWeek, 2)], rows: [['Overtime before tax', $(x.extraWeek, 2)], ['Tax rate on the extra hours', pct(x.marginal, 1)], ['Base week', '40 hours, code M']] };
  } },
  finalpay: { title: 'Annual leave paid out in your final pay', cta: 'Holiday pay calculator', inputs: [{ id: 'w', label: 'Ordinary weekly pay', def: 1300, unit: '$', max: 100000 }, { id: 'l', label: 'Untaken leave you are entitled to (weeks)', def: 2, unit: 'wk', max: 30, decimals: 1 }, { id: 'e', label: 'Gross earnings since your last anniversary', def: 30000, unit: '$', max: 5000000 }], run: ({ w, l, e }) => {
    const x = finalPay({ weeklyPay: w, leaveWeeks: l, earningsSinceAnniversary: e }); return { head: ['Leave pay-out after PAYE and ACC', $(x.net)], rows: [['Untaken entitled leave', $(x.untaken)], ['8 % since the anniversary', $(x.accrued)], ['Extra-pay rate with ACC', pct(x.rate, 2)]] };
  } },
  sick: { title: 'What a sick day pays', cta: 'Take-home pay calculator', inputs: [{ id: 'h', label: 'Hourly rate', def: 30, unit: '$', max: 2000, decimals: 2 }, { id: 'n', label: 'Hours you would have worked that day', def: 8, unit: 'h', max: 24, decimals: 1 }], run: ({ h, n }) => {
    const d = h * n; return { head: ['Sick pay for the day, before tax', $(d, 2)], rows: [['Minimum entitlement per year', `${P.leave.sick_days} days`], ['Value of a full year’s entitlement', $(d * P.leave.sick_days)], ['Most you can hold', `${P.leave.sick_max_balance} days`]] };
  } },
  living: { title: 'Living Wage take-home pay', cta: 'Hourly to salary calculator', inputs: [{ id: 'h', label: 'Hours a week', def: 40, unit: 'h', max: 80 }], run: ({ h }) => {
    const g = hourlyToAnnual(P.living_wage.hourly, h); const a = A(g, { code: g >= P.ietc.min_income && g <= P.ietc.max_income ? 'ME' : 'M' }); const m = A(hourlyToAnnual(P.min_wage.adult, h), { code: 'M' });
    return { head: ['Take-home per week on the Living Wage', $(a.takeHome / 52)], rows: [['Living Wage per hour', $(P.living_wage.hourly, 2)], ['Gross per year', $(g)], ['More than the minimum wage, per week in hand', $((a.takeHome - m.takeHome) / 52)]] };
  } },
  rwt: { title: 'Tax on your savings interest', cta: 'Income tax calculator', inputs: [{ id: 'i', label: 'Interest earned in the year', def: 2000, unit: '$', max: 5000000 }, { id: 's', label: 'Other income (salary, wages, pension)', def: 65000, unit: '$', max: 5000000 }], run: ({ i, s }) => {
    const x = rwt({ interest: i, otherIncome: s }); return { head: ['RWT rate to give your bank', pct(x.rate, 1)], rows: [['RWT deducted', $(x.withheld)], ['Interest you keep', $(x.net)], ['Left to pay or refund at year end', $(x.balance)]] };
  } },
  provisional: { title: 'Your provisional tax instalments', cta: 'Contractor tax calculator', inputs: [{ id: 'r', label: 'Residual income tax last year', def: 12000, unit: '$', max: 5000000 }], run: ({ r }) => {
    const x = provisional({ residual: r }); return { head: [x.due ? 'Each of the three instalments' : 'Provisional tax due', x.due ? $(x.instalment) : $(0)], rows: [['Standard option, last year plus 5 %', $(x.total)], ['Threshold', $(P.provisional.rit_threshold)], ['Due dates', P.provisional_tax.instalments.join(', ')]] };
  } },
  super: { title: 'NZ Super after tax, with your other income', cta: 'Income tax calculator', inputs: [{ id: 'k', label: 'Your situation', def: P.super.fortnight_gross.single_alone, options: [{ value: String(P.super.fortnight_gross.single_alone), label: 'Single, living alone' }, { value: String(P.super.fortnight_gross.single_sharing), label: 'Single, sharing' }, { value: String(P.super.fortnight_gross.couple_each), label: 'Couple, both qualify (each)' }] }, { id: 'o', label: 'Other income per year', def: 0, unit: '$', max: 5000000 }], run: ({ k, o }) => {
    const x = superAfterTax({ fortnightGross: k, otherIncome: o }); return { head: ['NZ Super per fortnight after tax', $(x.netFortnight, 2)], rows: [['Before tax per fortnight', $(k, 2)], ['Tax on the pension per year', $(x.tax)], ['Rate on your next dollar', pct(x.marginal, 1)]] };
  } },
};

export function getSpec(kind: string, _lang?: string): MiniSpec {
  const s = SPECS[kind]; if (!s) throw new Error(`Mini-simulateur inconnu : ${kind}`); return s;
}
