import { makeRouter, type RouteDef } from './routes-core';
export const LOCALES = ['en'] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = 'en';
/** Pages par montant : salaire annuel et taux horaire, chacune adossée à un seuil propre (lib/amount-angles.ts). */
export const ANNUAL = [30000, 40000, 50000, 53500, 60000, 65000, 70000, 78100, 80000, 90000, 100000, 120000, 150000, 180000] as const;
export const HOURLY = [25, 30, 35, 40, 50, 60] as const;
export const ROUTES: RouteDef<Locale>[] = [
  { id: 'home', paths: { en: '/en/' } },
  { id: 'salary', paths: { en: '/en/salary-calculator/' } },
  { id: 'takeHome', paths: { en: '/en/take-home-pay-calculator/' } },
  { id: 'incomeTax', paths: { en: '/en/income-tax-calculator/' } },
  { id: 'refund', paths: { en: '/en/ird-tax-calculator/' } },
  { id: 'contractor', paths: { en: '/en/contractor-tax-calculator/' } },
  { id: 'hourly', paths: { en: '/en/hourly-to-salary-calculator/' } },
  { id: 'holidayCalc', paths: { en: '/en/holiday-pay-calculator/' } },
  { id: 'kiwisaver', paths: { en: '/en/kiwisaver-calculator/' } },
  { id: 'studentLoan', paths: { en: '/en/student-loan-repayment-calculator/' } },
  { id: 'employerCost', paths: { en: '/en/employer-cost-calculator/' } },
  { id: 'secondary', paths: { en: '/en/secondary-tax-calculator/' } },
  { id: 'netToGross', paths: { en: '/en/net-to-gross-salary/' } },
  { id: 'payeRates', paths: { en: '/en/paye-tax-rates/' } },
  { id: 'taxRates', paths: { en: '/en/income-tax-rates/' } },
  { id: 'taxCodes', paths: { en: '/en/tax-codes/' } },
  { id: 'ksChanges', paths: { en: '/en/kiwisaver-changes-2026/' } },
  { id: 'acc', paths: { en: '/en/acc-levy/' } },
  { id: 'ietcGuide', paths: { en: '/en/independent-earner-tax-credit/' } },
  { id: 'minimumWage', paths: { en: '/en/minimum-wage/' } },
  { id: 'averageSalary', paths: { en: '/en/average-salary/' } },
  { id: 'selfEmployed', paths: { en: '/en/self-employed-tax/' } },
  { id: 'holidayPay', paths: { en: '/en/holiday-pay/' } },
  { id: 'employeeVsContractor', paths: { en: '/en/employee-vs-contractor/' } },
  ...ANNUAL.map((a) => ({ id: `y-${a}`, paths: { en: `/en/${a}-salary-after-tax/` } })),
  ...HOURLY.map((a) => ({ id: `h-${a}`, paths: { en: `/en/${a}-an-hour-salary/` } })),
  { id: 'glossary', paths: { en: '/en/glossary/' } },
  { id: 'method', paths: { en: '/en/methodology/' } },
  { id: 'widget', paths: { en: '/en/widget/' }, noindex: true },
  { id: 'about', paths: { en: '/en/about/' } },
  { id: 'contact', paths: { en: '/en/contact/' } },
  { id: 'editorial', paths: { en: '/en/editorial-policy/' } },
  { id: 'privacy', paths: { en: '/en/privacy/' }, noindex: true },
  { id: 'terms', paths: { en: '/en/terms/' }, noindex: true },
  { id: 'cookies', paths: { en: '/en/cookies/' }, noindex: true },
];
export const { NOINDEX_PATHS, route, hasRoute, altPaths } = makeRouter(LOCALES, ROUTES);
