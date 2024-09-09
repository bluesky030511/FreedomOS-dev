import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { Button, Card, Divider, IconButton, Stack, Typography } from '@mui/material';
import { useContext } from 'react';
import toast from 'react-hot-toast';

import { BatchableCartItem, InventoryPlotContext } from '../context/InventoryPlotContext';
import { getItemPriorityBarcode } from '@/app/(util)/item';

export const SelectedItem = () => {
  // context and hooks
  const inventoryPlotContext = useContext(InventoryPlotContext);
  const { selectedItem, batchableCart, setBatchableCart } = inventoryPlotContext;

  // helpers
  const addToBatchableCart = () => {
    if (!selectedItem) return;
    if (selectedItem.itemType === 'barcode') return;

    // check if item is already in batch
    const isItemInBatch = batchableCart.some(
      ({ batchable }) => batchable.itemType === selectedItem.itemType && batchable.item.uuid === selectedItem.item.uuid,
    );
    if (isItemInBatch) {
      toast.error('Item already in batch cart');
      return;
    }

    const newBatchableCartItem: BatchableCartItem = {
      batchable: selectedItem,
    };

    setBatchableCart([...batchableCart, newBatchableCartItem]);
    toast.success('Item added to batch cart');
  };

  // constants
  const isBatchableItem = selectedItem && selectedItem.itemType === 'box' && getItemPriorityBarcode(selectedItem.item) !== null;

  return (
    <Card variant="outlined">
      <Stack direction="row">
        <Stack spacing={2}>
          <Typography variant="subtitle1" fontWeight={600}>
            Selected Item
          </Typography>

          {selectedItem?.itemType === 'barcode' && (
            <Stack>
              <Typography>
                Type: {selectedItem.item.meta.barcode_type} ({selectedItem.item.meta.data})
              </Typography>
              <Typography>Barcode UUID: {selectedItem.item.item_uuid}</Typography>
            </Stack>
          )}
          {selectedItem?.itemType === 'box' && (
            <Stack>
              {selectedItem.item.barcodes.map((barcode, idx) => (
                <Typography key={`${barcode.meta.data}-${idx}`}>
                  Barcode {idx + 1}: {barcode.meta.barcode_type} ({barcode.meta.data})
                </Typography>
              ))}
              <Typography>Item UUID: {selectedItem.item.uuid}</Typography>
              <Typography>Stack:</Typography>
              {selectedItem.item.meta.stack.map((stackItem, idx) => (
                <Typography key={`${stackItem}-${idx}`}>
                  {stackItem}{' '}
                  <IconButton onClick={() => navigator.clipboard.writeText(stackItem)}>
                    <ContentCopyIcon />
                  </IconButton>
                </Typography>
              ))}
            </Stack>
          )}
          {selectedItem?.itemType === 'empty' && (
            <Stack>
              <Typography>
                Empty UUID: {selectedItem.item.uuid}{' '}
                <IconButton onClick={() => navigator.clipboard.writeText(selectedItem.item.uuid)}>
                  <ContentCopyIcon />
                </IconButton>
              </Typography>
            </Stack>
          )}

          <Button sx={{ maxWidth: '200px' }} disabled={!isBatchableItem} onClick={addToBatchableCart}>
            Add to batch cart
          </Button>
        </Stack>

        <Divider orientation="vertical" />

        <Stack></Stack>
      </Stack>
    </Card>
  );
};
