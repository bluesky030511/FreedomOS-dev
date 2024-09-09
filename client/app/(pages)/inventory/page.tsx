'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Box, Card, Grid, Stack } from '@mui/material';
import dynamic from 'next/dynamic';
import { FormProvider, useForm } from 'react-hook-form';

import { BatchBuilder } from './components/BatchBuilder';
import { InventoryContainerSkeleton } from './components/InventorySkeleton';
import { RobotContainer } from './components/RobotContainer';
import { SelectedItem } from './components/SelectedItem';
import { InventoryPlotProvider } from './context/InventoryPlotContext';
import { InventoryPlotForm } from './schema';

// dynamically load to avoid error ReferenceError: self is not defined
// it also make loading snappier
const InventoryContainer = dynamic(() => import('./components/InventoryContainer'), {
  ssr: false,
  loading: () => (
    <Card variant="outlined">
      <InventoryContainerSkeleton />
    </Card>
  ),
});

const InventoryPage = () => {
  const methods = useForm({
    resolver: zodResolver(InventoryPlotForm),
  });

  return (
    <InventoryPlotProvider>
      <FormProvider {...methods}>
        <Grid container spacing={3}>
          <Grid item xs={8}>
            <Grid container spacing={3} direction="column">
              <Grid item>
                <InventoryContainer />
              </Grid>
              <Grid item>
                <SelectedItem />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={4}>
            <Grid container spacing={3} direction="column">
              <Grid item>
                <RobotContainer />
              </Grid>
              <Grid item>
                <BatchBuilder />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </FormProvider>
    </InventoryPlotProvider>
  );
};

export default InventoryPage;
