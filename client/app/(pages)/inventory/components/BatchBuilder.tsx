import { DndContext, DragEndEvent, KeyboardSensor, PointerSensor, closestCenter, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, arrayMove, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Button, Card, Stack, Typography } from '@mui/material';
import React, { useContext, useState } from 'react';

import { BatchableCart } from './BatchableCart';
import { BatchBuilderDialog } from './BatchBuilderDialog';
import type { Batchable, BatchableCartItem } from '../context/InventoryPlotContext';
import { InventoryPlotContext } from '../context/InventoryPlotContext';

export const BatchBuilder = () => {
  // context and hooks
  const inventoryPlotContext = useContext(InventoryPlotContext);
  const { batchableCart, setBatchableCart } = inventoryPlotContext;
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );
  const [openBuilderModal, setOpenBuilderModal] = useState(false);

  // helpers
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) return;

    const getNewOrder = (cartItems: BatchableCartItem[]) => {
      const oldIndex = cartItems.findIndex(({ batchable }) => batchable.item.uuid === active.id);
      const newIndex = cartItems.findIndex(({ batchable }) => batchable.item.uuid === over.id);
      return arrayMove<BatchableCartItem>(cartItems, oldIndex, newIndex);
    };

    if (active.id !== over?.id) {
      setBatchableCart(getNewOrder(batchableCart));
    }
  };

  const startBuilder = () => {
    setOpenBuilderModal(true);
  };
  const closeBuilder = () => {
    setOpenBuilderModal(false);
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={batchableCart.map(({ batchable }) => batchable.item.uuid)} strategy={verticalListSortingStrategy}>
        <BatchBuilderDialog open={openBuilderModal} onClose={closeBuilder} />
        <Card variant="outlined">
          <Stack spacing={2}>
            {/* Title */}
            <Typography variant="subtitle1" fontWeight={600}>
              Batch Builder
            </Typography>

            {/* Batch items */}
            <BatchableCart />

            {/* CTA button */}
            <Button onClick={startBuilder} disabled={batchableCart.length <= 0}>
              Submit batch
            </Button>
          </Stack>
        </Card>
      </SortableContext>
    </DndContext>
  );
};
