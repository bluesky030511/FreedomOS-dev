import { z } from 'zod';

export const InventoryPlotForm = z.object({
  side: z.enum(['left', 'right']),
  aisle: z.number().int().nonnegative(),
});
export type InventoryPlotFormType = z.infer<typeof InventoryPlotForm>;
