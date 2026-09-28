/** Types des mini-simulateurs (RECETTE §9.3). Chaque site décrit les siens dans `lib/mini-specs.ts`. */
export interface MiniInput { id: string; label: string; def: number; unit?: string; max?: number; decimals?: number; options?: Array<{ value: string; label: string }> }
export interface MiniOut { head: [string, string]; rows: Array<[string, string]>; note?: string }
export interface MiniSpec { title: string; cta: string; inputs: MiniInput[]; run: (v: Record<string, number>) => MiniOut }
