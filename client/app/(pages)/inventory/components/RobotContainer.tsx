'use client';

import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import HailIcon from '@mui/icons-material/Hail';
import LibraryAddIcon from '@mui/icons-material/LibraryAdd';
import RefreshIcon from '@mui/icons-material/Refresh';
import { Box, Button, Card, CircularProgress, IconButton, Link, Stack, Typography } from '@mui/material';
import { Item } from '@prisma/client';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useContext, useEffect } from 'react';
import toast from 'react-hot-toast';

import { getRobotInventory } from '../actions';
import { Batchable, InventoryPlotContext } from '../context/InventoryPlotContext';
import { getItemPriorityBarcode } from '@/app/(util)/item';

export const RobotContainer = () => {
  // context and hooks
  const inventoryPlotContext = useContext(InventoryPlotContext);
  const { robotBatchables, setRobotBatchables, batchableCart, setBatchableCart } = inventoryPlotContext;

  const {
    isPending,
    data: serverRobotItems,
    mutate: triggerGetRobotInventory,
  } = useMutation({
    mutationFn: () => getRobotInventory(),
    onSuccess: data => {
      // convert to batchables
      const batchables = data.map((item: Item) => {
        return {
          item,
          itemType: 'box',
        };
      }) as Batchable[];
      // set robot items
      setRobotBatchables(batchables);
    },
  });

  // helper add to batch builder
  const addToBatchBuilder = async (batchable: Batchable) => {
    // if batchable already in batchableCart, then skip with toast
    if (batchableCart.some(({ batchable: { item } }) => item.uuid === batchable.item.uuid)) {
      toast.error('Item already in batch cart');
      return;
    }
    setBatchableCart([...batchableCart, { batchable }]);
  };

  useEffect(() => {
    triggerGetRobotInventory();
  }, []);

  return (
    <Card variant="outlined">
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="start">
          <Typography variant="subtitle1" fontWeight={600}>
            Robot Inventory
          </Typography>
          <IconButton title="Refresh" onClick={() => triggerGetRobotInventory()}>
            <RefreshIcon />
          </IconButton>
        </Stack>

        <Stack spacing={1}>
          {isPending && (
            <Box display="flex" justifyContent="center" alignItems="center">
              <CircularProgress />
            </Box>
          )}

          {!isPending && !robotBatchables.length && <Typography variant="body2">No Items</Typography>}

          {!isPending &&
            robotBatchables.map((batchable, idx) => (
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">{getItemPriorityBarcode(batchable.item) || batchable.item.uuid}</Typography>
                <Stack direction="row">
                  <IconButton
                    title="Add to batch builder"
                    onClick={() => {
                      addToBatchBuilder(batchable);
                    }}
                  >
                    <LibraryAddIcon />
                  </IconButton>
                </Stack>
              </Stack>
            ))}
        </Stack>
      </Stack>
    </Card>
  );
};
