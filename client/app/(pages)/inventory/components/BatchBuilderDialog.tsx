import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorIcon from '@mui/icons-material/Error';
import { Box, Button, Chip, CircularProgress, Dialog, DialogProps, Divider, Grid, Stack, TextField, Typography } from '@mui/material';
import { Item } from '@prisma/client';
import { useContext, useState } from 'react';
import toast from 'react-hot-toast';

import { sendBatch } from '../actions';
import { BatchableCartItem, InventoryPlotContext } from '../context/InventoryPlotContext';
import { getItemPriorityBarcode } from '@/app/(util)/item';

interface BatchBuilderDialogProps extends Omit<DialogProps, 'children'> {}
export const BatchBuilderDialog = ({ open, onClose, ...rest }: BatchBuilderDialogProps) => {
  // context and hooks
  const inventoryPlotContext = useContext(InventoryPlotContext);
  const { batchableCart, setBatchableCart, robotBatchables, setRobotBatchables } = inventoryPlotContext;
  const [destinationIds, setDestinationIds] = useState<Record<string, string>>({});

  // constants
  // disabled if all job types are not assigned
  const isDisabled = batchableCart.some(({ jobType }) => !jobType);
  const [isLoading, setIsLoading] = useState(false);

  // helper add items to robot Items
  const updateRobotItems = (batchableCart: BatchableCartItem[]) => {
    // only add batchablesCart are the fetch inventory or fetch designated
    const fetchBatchableCart = batchableCart.filter(({ jobType }) => jobType === 'FETCH_INVENTORY' || jobType === 'FETCH_DESIGNATED');
    const batchables = fetchBatchableCart.map(({ batchable }) => batchable);
    setRobotBatchables([...robotBatchables, ...batchables]);
  };

  // helper
  const updateCartItemDestination = (uuid: string, destinationId: string) => {
    const updatedCart = batchableCart.map(cartItem => {
      if (cartItem.batchable.item.uuid === uuid) {
        return { ...cartItem, destinationId };
      }
      return cartItem;
    });
    setBatchableCart(updatedCart);
  };

  // helper
  const submitBatch = async () => {
    // update all batchableCart with destinationId if jobType is store inventory or store designated
    const batchableCartWithDestination = batchableCart.map(cartItem => {
      const destinationId = destinationIds[cartItem.batchable.item.uuid];
      if (!destinationId) return cartItem;
      return { ...cartItem, destination_uuid: destinationId };
    });

    // validate that all store has their destination filled
    const hasDestinationIds = batchableCartWithDestination.every(({ jobType, destination_uuid }) => {
      if (jobType == 'STORE_INVENTORY' || jobType == 'STORE_DESIGNATED') {
        return !!destination_uuid;
      }

      return true;
    });

    if (!hasDestinationIds) {
      toast.error('Please fill in all destination IDs');
      return;
    }

    setIsLoading(true);
    setTimeout(async () => {
      const { error } = await sendBatch({ batchableCart: batchableCartWithDestination });
      if (error) {
        toast.error(`Batch failed to submit.\n${error}`);
        setIsLoading(false);
        return;
      }

      setIsLoading(false);
      setBatchableCart([]);
      toast.success('Batch submitted');

      // update items on robot
      updateRobotItems(batchableCart);

      onClose?.({}, 'escapeKeyDown');
    }, 1000);
  };

  return (
    <Dialog open={open} onClose={onClose} closeAfterTransition {...rest} fullWidth>
      <Box sx={{ width: '100%', bgcolor: 'background.paper', p: 2 }} display="flex">
        <Stack spacing={2} width="100%">
          <Typography variant="subtitle1" fontWeight={600}>
            Batch Builder
          </Typography>

          {/* Batch items */}
          <Grid container spacing={2}>
            <Grid item display="flex" justifyContent="space-between" alignItems="center" xs={4}>
              <Typography variant="body2" fontWeight="600">
                Batchable
              </Typography>
            </Grid>
            <Grid item display="flex" justifyContent="end" alignItems="center" xs={8}>
              <Typography variant="body2" fontWeight="600">
                Additional Input
              </Typography>
            </Grid>
            {batchableCart.map(({ jobType, batchable }) => (
              <>
                <Grid item display="flex" xs={4}>
                  <Stack spacing={1}>
                    <Typography>{getItemPriorityBarcode(batchable.item)}</Typography>
                    <Chip
                      color={jobType ? 'success' : 'warning'}
                      label={jobType || 'No job type assigned'}
                      icon={jobType ? <CheckCircleOutlineIcon /> : <ErrorIcon />}
                    />
                  </Stack>
                </Grid>

                <Grid item display="flex" xs={8} justifyContent="end" alignItems="end">
                  {jobType === 'STORE_INVENTORY' || jobType === 'STORE_DESIGNATED' ? (
                    <TextField
                      fullWidth
                      placeholder="Destination UUID"
                      sx={{ pl: 4 }}
                      value={destinationIds[batchable.item.uuid] || ''}
                      onChange={event => {
                        // update the batchable destination
                        const destinationId = event.target.value;
                        setDestinationIds({ ...destinationIds, [batchable.item.uuid]: destinationId });
                      }}
                    />
                  ) : (
                    <Typography variant="body2">n/a</Typography>
                  )}
                </Grid>
              </>
            ))}
          </Grid>

          <Divider />

          <Stack direction="row" justifyContent="space-between" width="100">
            <Button
              variant="outlined"
              onClick={event => {
                if (onClose) onClose(event, 'escapeKeyDown');
              }}
            >
              Cancel
            </Button>
            <Button variant="contained" onClick={submitBatch} color="error" disabled={isDisabled || isLoading}>
              <Box width="100px" display="flex" alignItems="center" justifyContent="center">
                {isLoading ? <CircularProgress sx={{ color: 'white' }} size="20px" /> : 'Submit batch'}
              </Box>
            </Button>
          </Stack>
        </Stack>
      </Box>
    </Dialog>
  );
};
