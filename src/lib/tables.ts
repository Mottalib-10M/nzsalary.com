/** Exemples chiffrés : toujours produits par le moteur (RECETTE §4). */
import { compute, type Code, type Period } from './engine/nz';
import P from '../data/params-2026.json';
export { P };
export const ex = (gross: number, o: { code?: Code; ks?: number; sl?: boolean; period?: Period } = {}) => compute({ gross, code: o.code ?? 'M', kiwisaver: o.ks ?? 0.035, studentLoan: o.sl ?? false, period: o.period ?? 'annual' });
