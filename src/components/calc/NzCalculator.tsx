import { useEffect, useMemo, useState } from 'react';
import NumberField from '../ui/NumberField';
import SelectField from '../ui/SelectField';
import Toggle from '../ui/Toggle';
import StackedBar from '../ui/StackedBar';
import { compute, grossForNet, hourlyToAnnual, secondaryCode, partYearRefund, contractor, type Code, type Period } from '../../lib/engine/nz';
import { formatMoney, formatPercent } from '../../lib/format';
import { readParams, num, str, updateURL } from '../../lib/url-state';

export type Mode = 'paye' | 'salary' | 'takeHome' | 'incomeTax' | 'refund' | 'contractor' | 'hourly' | 'kiwisaver' | 'studentLoan' | 'employerCost' | 'secondary' | 'netToGross';
interface Props { mode?: Mode; initialGross?: number; initialHourly?: number; initialPeriod?: Period; methodHref?: string }
const PERIOD_OPTS = [{ value: 'weekly', label: 'Weekly' }, { value: 'fortnightly', label: 'Fortnightly' }, { value: 'monthly', label: 'Monthly' }, { value: 'annual', label: 'Yearly' }];
const KS_OPTS = [{ value: '0', label: 'Not a member' }, { value: '0.03', label: '3 % (temporary reduction)' }, { value: '0.035', label: '3.5 % (default from April 2026)' }, { value: '0.04', label: '4 %' }, { value: '0.06', label: '6 %' }, { value: '0.08', label: '8 %' }, { value: '0.1', label: '10 %' }];
const CODE_OPTS = [{ value: 'M', label: 'M (main job)' }, { value: 'ME', label: 'ME (main job, with IETC)' }, { value: 'SB', label: 'SB (secondary, 10.5 %)' }, { value: 'S', label: 'S (secondary, 17.5 %)' }, { value: 'SH', label: 'SH (secondary, 30 %)' }, { value: 'ST', label: 'ST (secondary, 33 %)' }, { value: 'SA', label: 'SA (secondary, 39 %)' }];
const PER_LABEL: Record<Period, string> = { weekly: 'per week', fortnightly: 'per fortnight', monthly: 'per month', annual: 'per year' };

export default function NzCalculator({ mode = 'paye', initialGross = 65000, initialHourly = 30, initialPeriod = 'fortnightly', methodHref }: Props) {
  const sp = new URLSearchParams(); // premier rendu = HTML du build (RECETTE §17.5)
  const [gross, setGross] = useState(num(sp, 'g', initialGross));
  const [net, setNet] = useState(num(sp, 'n', 50000));
  const [hourly, setHourly] = useState(num(sp, 'h', initialHourly));
  const [hours, setHours] = useState(num(sp, 'hw', 40));
  const [period, setPeriod] = useState<Period>(str(sp, 'p', initialPeriod) as Period);
  const [code, setCode] = useState<Code>(str(sp, 'c', 'M') as Code);
  const [ks, setKs] = useState(str(sp, 'ks', '0.035'));
  const [sl, setSl] = useState(str(sp, 'sl', '0'));
  const [main, setMain] = useState(num(sp, 'main', 60000));
  const [months, setMonths] = useState(num(sp, 'mo', 4));
  const [expenses, setExpenses] = useState(num(sp, 'ex', 5000));
  const [wt, setWt] = useState(num(sp, 'wt', 20));
  const [copied, setCopied] = useState(false);
  useEffect(() => {
    const u = readParams(window.location.search);
    setGross(num(u, 'g', initialGross)); setNet(num(u, 'n', 50000)); setHourly(num(u, 'h', initialHourly)); setHours(num(u, 'hw', 40));
    setPeriod(str(u, 'p', initialPeriod) as Period); setCode(str(u, 'c', 'M') as Code); setKs(str(u, 'ks', '0.035')); setSl(str(u, 'sl', '0'));
    setMain(num(u, 'main', 60000)); setMonths(num(u, 'mo', 4)); setExpenses(num(u, 'ex', 5000)); setWt(num(u, 'wt', 20));
  }, []);
  const ksRate = Number(ks); const student = sl === '1';
  const secCode = secondaryCode(main + gross);
  const effCode: Code = mode === 'secondary' ? secCode : code;
  const effGross = mode === 'netToGross' ? grossForNet(net, { kiwisaver: ksRate, studentLoan: student, code }) : mode === 'hourly' ? hourlyToAnnual(hourly, hours) : gross;
  const r = useMemo(() => compute({ gross: effGross, code: effCode, kiwisaver: ksRate, studentLoan: student, period }), [effGross, effCode, ksRate, student, period]);
  const refund = useMemo(() => partYearRefund({ monthly: gross / 12, months: Math.max(1, Math.min(12, months)), code }), [gross, months, code]);
  const ctr = useMemo(() => contractor({ fees: gross, expenses, rate: wt / 100 }), [gross, expenses, wt]);
  useEffect(() => { updateURL({ g: ['netToGross', 'hourly'].includes(mode) ? undefined : gross, n: mode === 'netToGross' ? net : undefined, h: mode === 'hourly' ? hourly : undefined, hw: mode === 'hourly' && hours !== 40 ? hours : undefined, p: period === initialPeriod ? undefined : period, c: code === 'M' ? undefined : code, ks: ks === '0.035' ? undefined : ks, sl: sl === '1' ? 1 : undefined, main: mode === 'secondary' ? main : undefined, mo: mode === 'refund' ? months : undefined, ex: mode === 'contractor' ? expenses : undefined, wt: mode === 'contractor' ? wt : undefined }); }, [gross, net, hourly, hours, period, code, ks, sl, main, months, expenses, wt, mode]);

  const A = r.annual; const pp = r.perPeriod; const per = PER_LABEL[period];
  const head = (() => {
    switch (mode) {
      case 'incomeTax': return { l: 'Income tax for 2026-27', v: formatMoney(A.paye), s: `effective ${formatPercent(A.paye / Math.max(1, A.gross))} · marginal ${formatPercent(A.marginal, 1)}${A.ietc ? ` · IETC ${formatMoney(A.ietc)} applied` : ''}` };
      case 'refund': return { l: refund.refund >= 0 ? 'Likely refund at year end' : 'Likely tax to pay at year end', v: formatMoney(Math.abs(refund.refund)), s: `${formatMoney(refund.deducted)} PAYE deducted over ${months} months · ${formatMoney(refund.actual)} tax actually due` };
      case 'contractor': return { l: ctr.balance > 0 ? 'Tax still to pay after withholding' : 'Likely refund after withholding', v: formatMoney(Math.abs(ctr.balance)), s: `${formatMoney(ctr.withheld)} withheld at ${wt} % · rate that would cover it: about ${formatPercent(ctr.suggestedRate, 0)}` };
      case 'kiwisaver': return { l: 'Into your KiwiSaver each year', v: formatMoney(A.kiwisaver + A.employerKsNet + A.govtContribution), s: `you ${formatMoney(A.kiwisaver)} · employer ${formatMoney(A.employerKsNet)} after ESCT · government ${formatMoney(A.govtContribution)}` };
      case 'studentLoan': return { l: `Student loan repayment ${per}`, v: formatMoney(student ? pp.studentLoan : compute({ gross: effGross, code: effCode, studentLoan: true, period }).perPeriod.studentLoan), s: 'deducted by your employer with an SL tax code: 12 % above the repayment threshold' };
      case 'employerCost': return { l: 'Cost to the employer per year', v: formatMoney(A.employerCost), s: `salary ${formatMoney(A.gross)} + employer KiwiSaver ${formatMoney(A.employerKsGross)} (ESCT is deducted from it)` };
      case 'secondary': return { l: `Tax code for the second job: ${secCode}`, v: `${formatMoney(pp.takeHome)} ${per}`, s: `second job paid at ${formatPercent(A.marginal, 1)} + ACC · total income ${formatMoney(main + gross)}` };
      case 'netToGross': return { l: 'Gross salary needed per year', v: formatMoney(effGross), s: `for ${formatMoney(net)} a year after PAYE, ACC${ksRate ? ', KiwiSaver' : ''}${student ? ' and student loan' : ''}` };
      case 'hourly': return { l: `Take-home ${per}`, v: formatMoney(pp.takeHome), s: `${formatMoney(effGross)} a year for ${hours} h a week at ${formatMoney(hourly, 2)} an hour` };
      case 'salary': return { l: 'Take-home pay per year', v: formatMoney(A.takeHome), s: `${formatMoney(A.takeHome / 12)} a month · ${formatMoney(A.takeHome / 52)} a week` };
      default: return { l: `Take-home pay ${per}`, v: formatMoney(pp.takeHome), s: `${formatMoney(pp.gross)} gross − PAYE ${formatMoney(pp.paye)} − ACC ${formatMoney(pp.acc)}${pp.kiwisaver ? ` − KiwiSaver ${formatMoney(pp.kiwisaver)}` : ''}${pp.studentLoan ? ` − student loan ${formatMoney(pp.studentLoan)}` : ''}` };
    }
  })();
  const copy = async () => { try { await navigator.clipboard.writeText(`${head.l}: ${head.v}\n${window.location.href}`); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { /* indisponible */ } };
  const incomeLabel = mode === 'contractor' ? 'Contract income for the year (before expenses)' : mode === 'secondary' ? 'Income from the second job, per year' : mode === 'refund' ? 'Salary, per year equivalent' : 'Salary or wages per year, before tax';

  return (
    <div data-chrome className="rechner rounded-xl border border-navy-200 bg-navy-50 p-4 sm:p-6">
      <div className="grid gap-6 lg:grid-cols-5">
        <form className="space-y-4 lg:col-span-2" onSubmit={(e) => e.preventDefault()}>
          {mode === 'netToGross' ? <NumberField id="n" label="Take-home pay you want per year" value={net} onChange={setNet} unit="$" max={2000000} help="After PAYE, ACC and the deductions below" />
            : mode === 'hourly' ? (
              <div className="grid grid-cols-2 gap-3">
                <NumberField id="h" label="Hourly rate" value={hourly} onChange={setHourly} unit="$" max={1000} decimals={2} help="Before tax" />
                <NumberField id="hw" label="Hours a week" value={hours} onChange={setHours} unit="h" max={80} />
              </div>)
            : <NumberField id="g" label={incomeLabel} value={gross} onChange={setGross} unit="$" max={5000000} help={mode === 'refund' ? 'The salary you were paid while working, expressed per year' : undefined} />}
          {mode === 'secondary' && <NumberField id="main" label="Income from your main job, per year" value={main} onChange={setMain} unit="$" max={5000000} help="Used to pick the secondary tax code" />}
          {mode === 'refund' && <NumberField id="mo" label="Months worked in the tax year" value={months} onChange={setMonths} unit="months" min={1} max={12} help="From 1 April to 31 March; no other income assumed" />}
          {mode === 'contractor' && <div className="grid grid-cols-2 gap-3">
            <NumberField id="ex" label="Business expenses" value={expenses} onChange={setExpenses} unit="$" max={5000000} />
            <NumberField id="wt" label="Withholding rate you chose" value={wt} onChange={setWt} unit="%" min={10} max={100} help="At least 10 % on schedular payments" />
          </div>}
          {!['contractor', 'refund'].includes(mode) && <div className="grid grid-cols-2 gap-3">
            <SelectField id="p" label="Pay frequency" value={period} onChange={(v) => setPeriod(v as Period)} options={PERIOD_OPTS} />
            {mode === 'secondary'
              ? <SelectField id="ks" label="KiwiSaver" value={ks} onChange={setKs} options={KS_OPTS} />
              : <SelectField id="c" label="Tax code" value={code} onChange={(v) => setCode(v as Code)} options={CODE_OPTS} />}
          </div>}
          {!['contractor', 'refund', 'secondary'].includes(mode) && <SelectField id="ks" label="KiwiSaver contribution" value={ks} onChange={setKs} options={KS_OPTS} help={ksRate > 0 ? 'Your employer adds at least 3.5 %, taxed at your ESCT rate' : undefined} />}
          {!['contractor', 'refund'].includes(mode) && <Toggle id="sl" label="Student loan (SL code)?" options={[{ value: '0', label: 'No' }, { value: '1', label: 'Yes' }]} value={sl} onChange={setSl} />}
          <p className="text-xs text-navy-500">Calculated in your browser · nothing is sent · free</p>
        </form>
        <div className="lg:col-span-3" aria-live="polite">
          <div className="rounded-lg border border-accent-200 bg-white p-5">
            <div className="mb-4 text-center">
              <p className="text-sm font-medium text-navy-500">{head.l}</p>
              <p className="tabular-nums mt-1 text-4xl font-bold text-navy-900 sm:text-5xl">{head.v}</p>
              <p className="tabular-nums mt-1 text-sm text-navy-500">{head.s}</p>
            </div>
            {mode === 'refund' ? (
              <table className="mt-2 w-full text-sm"><tbody className="divide-y divide-navy-100">
                <Row l="Income actually earned in the tax year" v={formatMoney(refund.actualIncome)} />
                <Row l="PAYE deducted (as if the salary lasted all year)" v={formatMoney(refund.deducted)} />
                <Row l="Tax actually due on that income" v={formatMoney(refund.actual)} />
                <Row l={refund.refund >= 0 ? 'Refund issued by Inland Revenue' : 'Tax to pay'} v={formatMoney(Math.abs(refund.refund))} bold accent />
              </tbody></table>
            ) : mode === 'contractor' ? (
              <table className="mt-2 w-full text-sm"><tbody className="divide-y divide-navy-100">
                <Row l="Contract income" v={formatMoney(gross)} />
                <Row l="Business expenses" v={`− ${formatMoney(expenses)}`} />
                <Row l="Taxable profit" v={formatMoney(ctr.profit)} bold />
                <Row l="Income tax on the profit" v={formatMoney(ctr.tax)} />
                <Row l="ACC earners’ levy (invoiced by ACC; work levy extra)" v={formatMoney(ctr.acc)} />
                <Row l={`Tax withheld at ${wt} %`} v={`− ${formatMoney(ctr.withheld)}`} />
                <Row l={ctr.balance > 0 ? 'Still to pay' : 'Refund'} v={formatMoney(Math.abs(ctr.balance))} bold accent />
              </tbody></table>
            ) : (<>
              <StackedBar ariaPrefix="Where the pay goes" total={A.gross} segments={[
                { label: 'Take-home', value: A.takeHome, color: '#15803d' },
                { label: 'PAYE', value: A.paye, color: '#334155' },
                { label: 'ACC', value: A.acc, color: '#94a3b8' },
                { label: 'KiwiSaver', value: A.kiwisaver, color: '#0f766e' },
                { label: 'Student loan', value: A.studentLoan, color: '#b45309' },
              ]} />
              <table className="mt-4 w-full text-sm"><tbody className="divide-y divide-navy-100">
                <Row l={`Gross ${per}`} v={formatMoney(pp.gross)} />
                <Row l={`PAYE (tax code ${effCode}${A.ietc ? `, IETC ${formatMoney(A.ietc)} a year` : ''})`} v={`− ${formatMoney(pp.paye)}`} />
                <Row l="ACC earners’ levy (1.75 %)" v={`− ${formatMoney(pp.acc)}`} />
                {pp.kiwisaver > 0 && <Row l={`KiwiSaver (${formatPercent(ksRate, 1)})`} v={`− ${formatMoney(pp.kiwisaver)}`} />}
                {pp.studentLoan > 0 && <Row l="Student loan (12 % above the threshold)" v={`− ${formatMoney(pp.studentLoan)}`} />}
                <Row l={`Take-home ${per}`} v={formatMoney(pp.takeHome)} bold accent />
                <Row l="Take-home per year" v={formatMoney(A.takeHome)} />
                {ksRate > 0 && <Row l={`Employer KiwiSaver ${formatMoney(A.employerKsGross)} − ESCT ${formatMoney(A.esct)}`} v={formatMoney(A.employerKsNet)} />}
                {ksRate > 0 && <Row l="Government contribution (25 c per $1, up to $260.72)" v={formatMoney(A.govtContribution)} />}
                <Row l="Employer cost per year (salary + KiwiSaver)" v={formatMoney(A.employerCost)} />
              </tbody></table>
            </>)}
            <p className="mt-3 text-xs text-navy-500">Inland Revenue rates for 2026-27: 10.5 % to 39 %, ACC 1.75 % up to {formatMoney(156641)}, KiwiSaver default 3.5 %. PAYE is annualised; Inland Revenue’s tables can differ by a few cents per pay. Estimates only, see the methodology.</p>
            <div className="no-print mt-4 flex flex-wrap gap-2">
              <button type="button" onClick={copy} className="rounded-lg border border-navy-300 bg-white px-3 py-1.5 text-sm font-medium text-navy-700 hover:bg-navy-50">{copied ? 'Copied' : 'Copy result'}</button>
              <button type="button" onClick={() => window.print()} className="rounded-lg border border-navy-300 bg-white px-3 py-1.5 text-sm font-medium text-navy-700 hover:bg-navy-50">Print</button>
              {methodHref && <a href={methodHref} className="ml-auto self-center text-sm text-accent-700 hover:underline">How this is calculated</a>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
function Row({ l, v, bold = false, accent = false }: { l: string; v: string; bold?: boolean; accent?: boolean }) { return <tr className={bold ? 'font-semibold' : ''}><td className={`py-2 pr-3 ${accent ? 'text-accent-700' : 'text-navy-600'}`}>{l}</td><td className={`tabular-nums whitespace-nowrap py-2 text-right ${accent ? 'text-accent-700' : 'text-navy-900'}`}>{v}</td></tr>; }
