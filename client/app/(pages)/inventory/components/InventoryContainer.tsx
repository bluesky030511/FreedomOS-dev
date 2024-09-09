'use client';

import { Box, Button, Card, FormControl, MenuItem, Select, Stack, TextField, Typography } from '@mui/material';
import { useRouter, useSearchParams } from 'next/navigation';
import { useContext } from 'react';
import { Controller, SubmitHandler, useFormContext } from 'react-hook-form';
import { NumericFormat } from 'react-number-format';

import InventoryPlot from './InventoryPlot';
import { InventorySkeleton } from './InventorySkeleton';
import { InventoryPlotContext } from '../context/InventoryPlotContext';
import { InventoryPlotForm, InventoryPlotFormType } from '../schema';

const InventoryContainer = () => {
  // context and hooks
  const { selectedItem, setSelectedItem } = useContext(InventoryPlotContext);
  const searchParams = useSearchParams();
  const querySide = searchParams.get('side');
  const queryAisle = searchParams.get('aisle');
  const router = useRouter();

  const {
    watch,
    control,
    handleSubmit,
    formState: { errors },
  } = useFormContext<InventoryPlotFormType>();

  // helper
  const updateInventoryPlot: SubmitHandler<InventoryPlotFormType> = async data => {
    router.push(`/inventory?side=${data.side}&aisle=${data.aisle}`);
  };

  // constants
  const validateQuery = InventoryPlotForm.safeParse({
    side: querySide,
    aisle: queryAisle ? parseInt(queryAisle, 10) : undefined,
  });

  return (
    <Card variant="outlined">
      <Stack spacing={2}>
        <Typography variant="subtitle1" fontWeight={600}>
          Inventory
        </Typography>

        <Stack spacing={2}>
          {validateQuery.success ? (
            <InventoryPlot side={validateQuery.data.side} aisle_index={validateQuery.data.aisle} />
          ) : (
            <InventorySkeleton>
              <Typography>Invalid Query</Typography>
            </InventorySkeleton>
          )}

          <Stack direction="row" spacing={1}>
            <Box display="flex" flex="1">
              <FormControl fullWidth>
                <Controller
                  name="side"
                  control={control}
                  defaultValue={validateQuery.data?.side || 'right'}
                  render={({ field }) => (
                    <Select {...field} error={!!errors['side']}>
                      <MenuItem value="left">Left</MenuItem>
                      <MenuItem value="right">Right</MenuItem>
                    </Select>
                  )}
                />
              </FormControl>
            </Box>
            <Box display="flex" flex="1">
              <FormControl fullWidth>
                <Controller
                  name="aisle"
                  control={control}
                  defaultValue={validateQuery.data?.aisle || 0}
                  render={({
                    field: { name, onChange, onBlur, value, ref }, // don't register twice
                  }) => (
                    <NumericFormat
                      getInputRef={ref}
                      name={name}
                      value={value}
                      onBlur={onBlur}
                      customInput={TextField}
                      onValueChange={input => {
                        onChange(input.floatValue);
                      }}
                      error={!!errors['aisle']}
                    />
                  )}
                />
              </FormControl>
            </Box>
          </Stack>

          <Button color="primary" sx={{ maxWidth: '200px' }} onClick={handleSubmit(updateInventoryPlot)}>
            Update
          </Button>
        </Stack>
      </Stack>
    </Card>
  );
};
export default InventoryContainer;
