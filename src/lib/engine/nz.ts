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

/** Taux PAYE d'un paiement exceptionnel (extra pay, IRD) : revenu des 4 dernières semaines × 13 + le paiement, taux marginal + ACC sous le plafond. */
export function extraPayRate(annualised: number, amount: number): number {
  const t = Math.max(0, annualised) + Math.max(0, amount);
  return marginalRate(t) + (t <= P.acc.max_liable ? P.acc.rate : 0);
}

/** Indemnité de congés « pay-as-you-go » de 8 % versée en une fois, imposée comme extra pay. */
export function holidayPay(o: { earnings: number; annualPay: number; kiwisaver?: number; studentLoan?: boolean }) {
  const pay = r2(Math.max(0, o.earnings) * P.leave.payg_rate);
  const rate = extraPayRate(o.annualPay, pay);
  const paye = r2(pay * rate);
  const kiwisaver = r2(pay * (o.kiwisaver ?? 0));
  const studentLoan = o.studentLoan && o.annualPay + pay > P.student_loan.threshold_annual ? r2(pay * P.student_loan.rate) : 0;
  return { pay, rate, paye, kiwisaver, studentLoan, net: r2(pay - paye - kiwisaver - studentLoan) };
}

/** Paiement exceptionnel (prime, bonus) : PAYE au taux « extra pay » ACC comprise, KiwiSaver et prêt étudiant. */
export function bonus(o: { amount: number; annualPay: number; kiwisaver?: number; studentLoan?: boolean }) {
  const amount = Math.max(0, o.amount); const rate = extraPayRate(o.annualPay, amount);
  const paye = r2(amount * rate); const kiwisaver = r2(amount * (o.kiwisaver ?? 0));
  const studentLoan = o.studentLoan && o.annualPay + amount > P.student_loan.threshold_annual ? r2(amount * P.student_loan.rate) : 0;
  return { amount, rate, paye, kiwisaver, studentLoan, net: r2(amount - paye - kiwisaver - studentLoan) };
}

/** Indemnité de licenciement économique : extra pay, mais ni cotisation ACC ni KiwiSaver (IRD). */
export function redundancy(o: { amount: number; annualPay: number; studentLoan?: boolean }) {
  const amount = Math.max(0, o.amount); const rate = marginalRate(Math.max(0, o.annualPay) + amount);
  const paye = r2(amount * rate);
  const studentLoan = o.studentLoan && o.annualPay + amount > P.student_loan.threshold_annual ? r2(amount * P.student_loan.rate) : 0;
  return { amount, rate, paye, studentLoan, net: r2(amount - paye - studentLoan) };
}

/** GST à 15 % : ajouter la taxe à un prix hors taxe, ou l'extraire d'un prix taxe comprise (3/23). */
export const gstAdd = (excl: number) => { const gst = r2(Math.max(0, excl) * P.gst.rate); return { excl: r2(Math.max(0, excl)), gst, incl: r2(Math.max(0, excl) + gst) }; };
export const gstRemove = (incl: number) => { const i = Math.max(0, incl); const gst = r2(i * P.gst.rate / (1 + P.gst.rate)); return { incl: r2(i), gst, excl: r2(i - gst) }; };

/** Augmentation : ce qu'elle laisse après PAYE, ACC et KiwiSaver. */
export function payRise(o: { gross: number; percent: number; kiwisaver?: number; code?: Code }) {
  const before = compute({ gross: o.gross, kiwisaver: o.kiwisaver, code: o.code }).annual;
  const newGross = r2(Math.max(0, o.gross) * (1 + o.percent));
  const after = compute({ gross: newGross, kiwisaver: o.kiwisaver, code: o.code }).annual;
  const extraGross = r2(newGross - before.gross); const extraNet = r2(after.takeHome - before.takeHome);
  return { newGross, extraGross, extraNet, kept: extraGross > 0 ? extraNet / extraGross : 0, before, after };
}

/** Jour férié travaillé : au moins une fois et demie le taux, plus un jour de repos payé si c'est un jour habituellement travaillé. */
export function publicHolidayPay(o: { hourly: number; hours: number; otherwiseWorking?: boolean }) {
  const ordinary = r2(Math.max(0, o.hourly) * Math.max(0, o.hours));
  const pay = r2(ordinary * P.public_holidays.premium);
  return { ordinary, pay, premium: r2(pay - ordinary), alternativeDay: (o.otherwiseWorking ?? true) ? ordinary : 0 };
}

/** Heures supplémentaires à un taux majoré convenu (aucune majoration légale hors jours fériés) et ce qu'elles laissent. */
export function overtime(o: { hourly: number; hoursPerWeek: number; overtimeHours: number; multiplier: number }) {
  const base = hourlyToAnnual(o.hourly, o.hoursPerWeek);
  const extraWeek = r2(Math.max(0, o.hourly) * Math.max(0, o.overtimeHours) * Math.max(1, o.multiplier));
  const a = compute({ gross: base }).annual; const b = compute({ gross: base + extraWeek * 52 }).annual;
  return { extraWeek, netWeek: r2((b.takeHome - a.takeHome) / 52), marginal: b.marginal };
}

/** Solde de tout compte : congés acquis non pris au taux hebdomadaire, plus 8 % des gains depuis le dernier anniversaire, imposés en extra pay. */
export function finalPay(o: { weeklyPay: number; leaveWeeks: number; earningsSinceAnniversary: number; kiwisaver?: number }) {
  const untaken = r2(Math.max(0, o.weeklyPay) * Math.max(0, o.leaveWeeks));
  const accrued = r2(Math.max(0, o.earningsSinceAnniversary) * P.leave.payg_rate);
  const total = r2(untaken + accrued); const rate = extraPayRate(o.weeklyPay * 52, total);
  const paye = r2(total * rate); const kiwisaver = r2(total * (o.kiwisaver ?? 0));
  return { untaken, accrued, total, rate, paye, kiwisaver, net: r2(total - paye - kiwisaver) };
}

/** RWT sur les intérêts : taux à choisir d'après le revenu annuel total, intérêts compris. */
export function rwt(o: { interest: number; otherIncome: number }) {
  const interest = Math.max(0, o.interest); const rate = marginalRate(Math.max(0, o.otherIncome) + interest);
  const tax = r2(incomeTax(o.otherIncome + interest) - incomeTax(o.otherIncome));
  const withheld = r2(interest * rate);
  return { rate, withheld, net: r2(interest - withheld), tax, balance: r2(tax - withheld) };
}

/** Impôt provisionnel, option standard : impôt résiduel de l'an dernier majoré de 5 %, en trois versements. */
export function provisional(o: { residual: number; twoYearsAgo?: boolean }) {
  const rit = Math.max(0, o.residual);
  const due = rit > P.provisional.rit_threshold;
  const uplift = o.twoYearsAgo ? P.provisional_tax.uplift_two_years : P.provisional_tax.uplift_last_year;
  const total = due ? r2(rit * uplift) : 0;
  return { due, total, instalment: r2(total / 3), uplift };
}

/** NZ Super : pension brute par quinzaine, imposée avec les autres revenus (aucune cotisation ACC sur la pension). */
export function superAfterTax(o: { fortnightGross: number; otherIncome?: number }) {
  const pension = r2(Math.max(0, o.fortnightGross) * 26); const other = Math.max(0, o.otherIncome ?? 0);
  const tax = r2(incomeTax(pension + other) - incomeTax(other));
  return { pension, tax, netYear: r2(pension - tax), netFortnight: r2((pension - tax) / 26), marginal: marginalRate(pension + other) };
}
