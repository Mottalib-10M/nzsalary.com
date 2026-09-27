import { route, ANNUAL, HOURLY, type Locale } from './routes';
export interface NavLink { href: string; label: string } export interface NavCategory { label: string; links: NavLink[] }
const L: Record<string, string> = {
  home: 'PAYE calculator', salary: 'Salary calculator', takeHome: 'Take-home pay calculator', incomeTax: 'Income tax calculator', refund: 'IRD tax refund calculator',
  contractor: 'Contractor tax calculator', hourly: 'Hourly to salary', kiwisaver: 'KiwiSaver calculator', studentLoan: 'Student loan repayments', employerCost: 'Employer cost calculator',
  secondary: 'Secondary tax calculator', netToGross: 'Net to gross salary', payeRates: 'PAYE tax rates', taxRates: 'Income tax rates', taxCodes: 'Tax codes', ksChanges: 'KiwiSaver changes 2026',
  acc: 'ACC earners’ levy', ietcGuide: 'Independent earner tax credit', minimumWage: 'Minimum wage', averageSalary: 'Average salary', selfEmployed: 'Self-employed tax',
  holidayPay: 'Holiday pay', employeeVsContractor: 'Employee vs contractor', glossary: 'Glossary', method: 'Methodology and sources', widget: 'Embed the calculator',
  about: 'About', contact: 'Contact', editorial: 'Editorial policy', privacy: 'Privacy', terms: 'Terms of use', cookies: 'Cookies',
};
export const label = (id: string, _l?: Locale) => L[id] ?? id;
const link = (id: string, lang: Locale): NavLink => ({ href: route(id, lang), label: label(id) });
export const annualLabel = (a: number) => `$${a.toLocaleString('en-NZ')} a year`;
export const hourlyLabel = (a: number) => `$${a} an hour`;
export function navCategories(lang: Locale): NavCategory[] {
  return [
    { label: 'Calculators', links: ['home', 'salary', 'takeHome', 'incomeTax', 'refund', 'netToGross', 'hourly', 'secondary', 'contractor', 'kiwisaver', 'studentLoan', 'employerCost'].map((i) => link(i, lang)) },
    { label: 'Tax guides', links: ['payeRates', 'taxRates', 'taxCodes', 'acc', 'ietcGuide', 'selfEmployed', 'employeeVsContractor'].map((i) => link(i, lang)) },
    { label: 'Pay and KiwiSaver', links: ['ksChanges', 'minimumWage', 'averageSalary', 'holidayPay'].map((i) => link(i, lang)) },
    { label: 'By salary', links: [...ANNUAL.map((a) => ({ href: route(`y-${a}`, lang), label: annualLabel(a) })), ...HOURLY.map((a) => ({ href: route(`h-${a}`, lang), label: hourlyLabel(a) }))] },
  ];
}
export const navDirect = (lang: Locale): NavLink[] => [link('method', lang)];
export const footerColumns = (lang: Locale): NavCategory[] => [...navCategories(lang).slice(0, 3), { label: 'The site', links: ['about', 'contact', 'editorial', 'method', 'glossary', 'widget', 'privacy', 'terms', 'cookies'].map((i) => link(i, lang)) }];
export const popularLinks = (lang: Locale): NavLink[] => [...ANNUAL.map((a) => ({ href: route(`y-${a}`, lang), label: annualLabel(a) })), ...HOURLY.map((a) => ({ href: route(`h-${a}`, lang), label: hourlyLabel(a) }))];
