import { Item } from '@prisma/client';

export const getItemPriorityBarcode = (item: Item) => {
  if (!item.barcodes) return null;

  // if empty, return null
  if (item.barcodes.length === 0) return null;

  // prioritize barcode of meta.type = GS1-128
  const gs1_barcode = item.barcodes.find(barcode => barcode.meta.barcode_type === 'GS1-128');
  if (gs1_barcode !== undefined) return gs1_barcode.meta.data;
  // then Code 128
  const code128_barcode = item.barcodes.find(barcode => barcode.meta.barcode_type === 'Code 128');
  if (code128_barcode !== undefined) return code128_barcode.meta.data;
  // otherwise null
  return null;
};
