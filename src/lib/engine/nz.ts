/**
 * Moteur Nouvelle-Zélande 2026-27 : impôt sur le revenu, PAYE par période, ACC, KiwiSaver
 * (salarié, employeur, ESCT, contribution de l'État), prêt étudiant, IETC, codes secondaires,
 * paiements « schedular » des travailleurs indépendants. Fonctions pures ; paramètres dans params-2026.json.
 */
import P from '../../data/params-2026.json';

export type Period = 'weekly' | 'fortnightly' | 'monthly' | 'annual';
export type Code = 'M' | 'ME' | 'SB' | 'S' | 'SH' | 'ST' | 'SA';
export const PERIODS = P.periods as Record<Period, number>;
const r2 = (x: number) => Math.round(x * 100) / 100;

/** Impôt annuel au barème (sans crédit d'impôt). */
export function incomeTax(income: number, brackets = P.tax.brackets): number {
  let tax = 0, prev = 0;
  for (const b of brackets) { const top = b.upto ?? Infinity; if (income > prev) tax += (Math.min(income, top) - prev) * b.rate; prev = top; if (income <= top) break; }
  return r2(tax);
}
export function marginalRate(income: number): number { for (const b of P.tax.brackets) if (income <= (b.upto ?? Infinity)) return b.rate; return 0.39; }
export const accLevy = (income: number) => r2(Math.min(Math.max(0, income), P.acc.max_liable) * P.acc.rate);
/** Crédit IETC : 520 $ entre 24 000 et 66 000 $, réduit de 13 c par dollar jusqu'à 70 000 $. */
export function ietc(income: number): number {
  const I = P.ietc;
  if (income < I.min_income || income > I.max_income) return 0;
  return r2(Math.max(0, I.amount - Math.max(0, income - I.abate_from) * I.abate_rate));
}
export const studentLoanAnnual = (income: number) => r2(Math.max(0, income - P.student_loan.threshold_annual) * P.student_loan.rate);
/** Code secondaire recommandé d'après le revenu annuel total estimé, tous emplois confondus. */
export function secondaryCode(totalIncome: number): Code {
  for (const b of P.tax.secondary_bands) if (totalIncome <= (b.upto ?? Infinity)) return b.code as Code;
  return 'SA';
}
export function esctRate(salaryPlusEmployerContrib: number): number { for (const b of P.esct) if (salaryPlusEmployerContrib <= (b.upto ?? Infinity)) return b.rate; return 0.39; }

export interface Input {
  gross: number;               // revenu annuel brut de cet emploi
  code?: Code;                 // M (principal), ME (avec IETC), ou code secondaire
  kiwisaver?: number;          // taux salarié : 0 si non-membre, 0.03 (réduction temporaire) à 0.10
  employerKs?: number;         // taux employeur, 3,5 % par défaut pour un membre
  studentLoan?: boolean;
  period?: Period;
}
export interface Result {
  period: Period; n: number;
  annual: { gross: number; tax: number; ietc: number; paye: number; acc: number; kiwisaver: number; studentLoan: number; takeHome: number;
    employerKsGross: number; esct: number; employerKsNet: number; employerCost: number; govtContribution: number; effective: number; marginal: number };
  perPeriod: { gross: number; paye: number; acc: number; kiwisaver: number; studentLoan: number; takeHome: number };
}

export function compute(i: Input): Result {
  const period = i.period ?? 'annual'; const n = PERIODS[period];
  const gross = Math.max(0, i.gross); const code = i.code ?? 'M';
  const secondary = code !== 'M' && code !== 'ME';
  const tax = secondary ? r2(gross * (P.tax.secondary as Record<string, number>)[code]) : incomeTax(gross);
  const credit = code === 'ME' ? ietc(gross) : 0;
  const paye = r2(Math.max(0, tax - credit));
  const acc = accLevy(gross);
  const ksRate = i.kiwisaver ?? 0; const kiwisaver = r2(gross * ksRate);
  // Prêt étudiant : 12 % au-delà du seuil sur l'emploi principal, 12 % du tout sur un emploi secondaire (code « SL »).
  const studentLoan = i.studentLoan ? (secondary ? r2(gross * P.student_loan.rate) : studentLoanAnnual(gross)) : 0;
  const takeHome = r2(gross - paye - acc - kiwisaver - studentLoan);
  const erRate = ksRate > 0 ? (i.employerKs ?? P.kiwisaver.employer_min) : 0;
  const employerKsGross = r2(gross * erRate);
  const esct = r2(employerKsGross * esctRate(gross + employerKsGross));
  const govt = ksRate > 0 && gross <= P.kiwisaver.govt_income_cap ? r2(Math.min(kiwisaver * P.kiwisaver.govt_rate, P.kiwisaver.govt_max)) : 0;
  const per = (x: number) => r2(x / n);
  return {
    period, n,
    annual: { gross, tax, ietc: credit, paye, acc, kiwisaver, studentLoan, takeHome, employerKsGross, esct, employerKsNet: r2(employerKsGross - esct),
      employerCost: r2(gross + employerKsGross), govtContribution: govt, effective: gross > 0 ? (paye + acc) / gross : 0, marginal: secondary ? (P.tax.secondary as Record<string, number>)[code] : marginalRate(gross) },
    perPeriod: { gross: per(gross), paye: per(paye), acc: per(acc), kiwisaver: per(kiwisaver), studentLoan: per(studentLoan), takeHome: per(takeHome) },
  };
}

/** Salaire brut annuel nécessaire pour un net annuel donné (mêmes options). */
export function grossForNet(net: number, o: Omit<Input, 'gross'>): number {
  if (net <= 0) return 0;
  let lo = net, hi = net * 2.2 + 5000;
  for (let k = 0; k < 90; k++) { const mid = (lo + hi) / 2; if (compute({ ...o, gross: mid }).annual.takeHome < net) lo = mid; else hi = mid; }
  return r2(hi);
}

/**
 * Remboursement de fin d'année pour une année incomplète : le PAYE d'une période est calculé
 * comme si le salaire de la période se répétait toute l'année. Qui ne travaille que quelques mois
 * a donc trop payé ; IRD rembourse l'écart à l'évaluation automatique.
 */
export function partYearRefund(o: { monthly: number; months: number; code?: Code }) {
  const code = o.code ?? 'M';
  const payeMonth = compute({ gross: o.monthly * 12, code, period: 'monthly' }).perPeriod.paye;
  const deducted = r2(payeMonth * o.months);
  const actualIncome = o.monthly * o.months;
  const actual = r2(Math.max(0, incomeTax(actualIncome) - (ietc(actualIncome))));
  return { deducted, actual, refund: r2(deducted - actual), actualIncome };
}

/** Paiements « schedular » : retenue au taux choisi contre impôt réel sur le bénéfice (+ ACC). */
export function contractor(o: { fees: number; expenses: number; rate: number; otherIncome?: number }) {
  const withheld = r2(o.fees * Math.max(o.rate, P.schedular.min_rate));
  const profit = Math.max(0, o.fees - o.expenses);
  const other = o.otherIncome ?? 0;
  const taxOnAll = incomeTax(profit + other); const taxOnOther = incomeTax(other);
  const tax = r2(taxOnAll - taxOnOther); const acc = r2(accLevy(profit + other) - accLevy(other));
  const suggested = o.fees > 0 ? Math.ceil(((tax + acc) / o.fees) * 100) / 100 : 0;
  return { withheld, profit, tax, acc, balance: r2(tax + acc - withheld), suggestedRate: Math.max(P.schedular.min_rate, suggested) };
}

export const hourlyToAnnual = (h: number, hoursPerWeek = 40) => h * hoursPerWeek * 52;
