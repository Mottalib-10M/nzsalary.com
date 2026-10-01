import { describe, it, expect } from 'vitest';
import { incomeTax, accLevy, ietc, studentLoanAnnual, compute, secondaryCode, esctRate, grossForNet, partYearRefund, contractor, extraPayRate, holidayPay } from './nz';

describe('Barème IRD depuis le 1er avril 2025', () => {
  it.each([[15600, 1638], [53500, 8270.5], [78100, 15650.5], [180000, 49277.5], [200000, 57077.5]])('revenu %i → %i', (i, t) => expect(incomeTax(i)).toBeCloseTo(t, 2));
  it('0 sur 0', () => expect(incomeTax(0)).toBe(0));
});
describe('ACC 2026-27 : 1,75 % jusqu’à 156 641 $', () => {
  it('100 000 $ → 1 750 $', () => expect(accLevy(100000)).toBe(1750));
  it('plafond → 2 741,22 $ (maximum publié)', () => expect(accLevy(300000)).toBe(2741.22));
});
describe('IETC', () => {
  it('24 000–66 000 $ → 520 $', () => { expect(ietc(24000)).toBe(520); expect(ietc(66000)).toBe(520); });
  it('68 000 $ → 260 $ (13 c par dollar au-delà de 66 000 $)', () => expect(ietc(68000)).toBe(260));
  it('hors bornes → 0', () => { expect(ietc(23999)).toBe(0); expect(ietc(70001)).toBe(0); });
});
describe('Prêt étudiant', () => {
  it('12 % au-delà de 24 128 $', () => expect(studentLoanAnnual(50000)).toBeCloseTo(3104.64, 2));
  it('sous le seuil → 0', () => expect(studentLoanAnnual(20000)).toBe(0));
});
describe('Codes secondaires et ESCT', () => {
  it('code secondaire selon le revenu total', () => { expect(secondaryCode(15000)).toBe('SB'); expect(secondaryCode(40000)).toBe('S'); expect(secondaryCode(60000)).toBe('SH'); expect(secondaryCode(100000)).toBe('ST'); expect(secondaryCode(200000)).toBe('SA'); });
  it('ESCT : seuils 2025', () => { expect(esctRate(18720)).toBe(0.105); expect(esctRate(62100)).toBe(0.175); expect(esctRate(90000)).toBe(0.30); expect(esctRate(216001)).toBe(0.39); });
});
describe('Calcul complet', () => {
  it('65 000 $, M, KiwiSaver 3,5 %', () => {
    const r = compute({ gross: 65000, kiwisaver: 0.035 });
    expect(r.annual.paye).toBeCloseTo(incomeTax(65000), 2);
    expect(r.annual.acc).toBe(1137.5);
    expect(r.annual.kiwisaver).toBe(2275);
    expect(r.annual.employerKsGross).toBe(2275);
    expect(r.annual.esct).toBeCloseTo(2275 * 0.30, 2);
    expect(r.annual.govtContribution).toBe(260.72);
  });
  it('code ME : l’IETC réduit le PAYE', () => {
    expect(compute({ gross: 50000, code: 'ME' }).annual.paye).toBeCloseTo(incomeTax(50000) - 520, 2);
  });
  it('au-delà de 180 000 $ : pas de contribution de l’État', () => expect(compute({ gross: 190000, kiwisaver: 0.04 }).annual.govtContribution).toBe(0));
  it('code secondaire SH : 30 % à plat', () => expect(compute({ gross: 20000, code: 'SH' }).annual.paye).toBe(6000));
  it('par semaine = annuel / 52', () => { const r = compute({ gross: 52000, period: 'weekly' }); expect(r.perPeriod.gross).toBe(1000); });
  it('net → brut réciproque', () => { const g = grossForNet(50000, { kiwisaver: 0.035 }); expect(compute({ gross: g, kiwisaver: 0.035 }).annual.takeHome).toBeCloseTo(50000, 0); });
});
describe('Année incomplète et indépendants', () => {
  it('4 mois à 6 000 $ : PAYE retenu sur une base annuelle de 72 000 $, trop-perçu remboursé', () => {
    const r = partYearRefund({ monthly: 6000, months: 4 });
    expect(r.actualIncome).toBe(24000);
    expect(r.refund).toBeGreaterThan(1500);
  });
  it('schedular : retenue minimale 10 %', () => expect(contractor({ fees: 50000, expenses: 5000, rate: 0.05 }).withheld).toBe(5000));
});

describe('extra pay et indemnité de congés 8 %', () => {
  // Barème IRD « Calculate PAYE for a lump sum payment », 2026-27 (en vigueur au 18 mai 2026).
  it('applique les taux IRD, ACC comprise sous le plafond', () => {
    expect(extraPayRate(10000, 500)).toBeCloseTo(0.1225, 6);
    expect(extraPayRate(40000, 3000)).toBeCloseTo(0.1925, 6);
    expect(extraPayRate(60000, 4800)).toBeCloseTo(0.3175, 6);
    expect(extraPayRate(100000, 8000)).toBeCloseTo(0.3475, 6);
    expect(extraPayRate(160000, 5000)).toBeCloseTo(0.33, 6);
    expect(extraPayRate(200000, 5000)).toBeCloseTo(0.39, 6);
  });
  it('calcule 8 % des gains puis la PAYE au taux extra pay', () => {
    const h = holidayPay({ earnings: 30000, annualPay: 52000 });
    expect(h.pay).toBe(2400);
    expect(h.rate).toBeCloseTo(0.3175, 6); // 52 000 + 2 400 = 54 400 > 53 500
    expect(h.paye).toBe(762);
    expect(h.net).toBe(1638);
  });
});


import { bonus, redundancy, gstAdd, gstRemove, payRise, publicHolidayPay, overtime, finalPay, rwt, provisional, superAfterTax } from './nz';
describe('Pages ajoutées le 2026-10-01', () => {
  it('prime de 5 000 $ sur 70 000 $ : 30 % + ACC 1,75 %', () => { const b = bonus({ amount: 5000, annualPay: 70000 }); expect(b.rate).toBeCloseTo(0.3175, 4); expect(b.paye).toBe(1587.5); expect(b.net).toBe(3412.5); });
  it('prime avec KiwiSaver 3,5 % et prêt étudiant', () => { const b = bonus({ amount: 2000, annualPay: 60000, kiwisaver: 0.035, studentLoan: true }); expect(b.kiwisaver).toBe(70); expect(b.studentLoan).toBe(240); });
  it('licenciement : pas d’ACC, 33 % au-delà de 78 100 $', () => { const r = redundancy({ amount: 20000, annualPay: 70000 }); expect(r.rate).toBe(0.33); expect(r.paye).toBe(6600); expect(r.net).toBe(13400); });
  it('GST : 100 $ + 15 % = 115 $ ; 115 $ contient 15 $ (3/23)', () => { expect(gstAdd(100).incl).toBe(115); expect(gstRemove(115).gst).toBe(15); expect(gstRemove(230).excl).toBe(200); });
  it('augmentation de 5 % sur 60 000 $ : 3 000 $ bruts, taxés à 30 % + ACC', () => { const p = payRise({ gross: 60000, percent: 0.05 }); expect(p.extraGross).toBe(3000); expect(p.extraNet).toBeCloseTo(3000 * (1 - 0.3175), 2); });
  it('jour férié : 8 h à 30 $ → 360 $ et un jour de repos de 240 $', () => { const h = publicHolidayPay({ hourly: 30, hours: 8 }); expect(h.pay).toBe(360); expect(h.alternativeDay).toBe(240); expect(publicHolidayPay({ hourly: 30, hours: 8, otherwiseWorking: false }).alternativeDay).toBe(0); });
  it('heures supplémentaires : 5 h à 1,5 × 30 $ = 225 $ par semaine', () => { const o = overtime({ hourly: 30, hoursPerWeek: 40, overtimeHours: 5, multiplier: 1.5 }); expect(o.extraWeek).toBe(225); expect(o.netWeek).toBeGreaterThan(140); expect(o.netWeek).toBeLessThan(225); });
  it('solde de tout compte : 2 semaines à 1 200 $ + 8 % de 30 000 $', () => { const f = finalPay({ weeklyPay: 1200, leaveWeeks: 2, earningsSinceAnniversary: 30000 }); expect(f.untaken).toBe(2400); expect(f.accrued).toBe(2400); expect(f.total).toBe(4800); expect(f.rate).toBeCloseTo(0.3175, 4); });
  it('RWT : 2 000 $ d’intérêts avec 60 000 $ de salaire → 30 %', () => { const r = rwt({ interest: 2000, otherIncome: 60000 }); expect(r.rate).toBe(0.30); expect(r.withheld).toBe(600); expect(r.balance).toBe(0); });
  it('impôt provisionnel : dû au-delà de 5 000 $, majoré de 5 %', () => { expect(provisional({ residual: 5000 }).due).toBe(false); const p = provisional({ residual: 12000 }); expect(p.total).toBe(12600); expect(p.instalment).toBe(4200); expect(provisional({ residual: 12000, twoYearsAgo: true }).total).toBe(13200); });
  it('NZ Super, personne seule : le net du barème officiel au code M à 0,50 $ près', () => { const s = superAfterTax({ fortnightGross: 1294.74 }); expect(Math.abs(s.netFortnight - 1110.30)).toBeLessThan(0.5); const c = superAfterTax({ fortnightGross: 984.28 }); expect(Math.abs(c.netFortnight - 854.08)).toBeLessThan(0.5); });
});
