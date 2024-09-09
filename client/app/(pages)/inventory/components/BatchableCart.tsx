import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import DeleteIcon from '@mui/icons-material/Delete';
import Delete from '@mui/icons-material/Delete';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import Edit from '@mui/icons-material/Edit';
import InventoryIcon from '@mui/icons-material/Inventory';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { Box, Card, Chip, CircularProgress, IconButton, Link, Popover, Stack, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';
import { Item } from '@prisma/client';
import { useQuery } from '@tanstack/react-query';
import { useContext, useState } from 'react';

import { getJobTranslationTypes } from '../actions';
import { BatchableCartItem, InventoryPlotContext } from '../context/InventoryPlotContext';
import { getItemPriorityBarcode } from '@/app/(util)/item';

export const BatchableCart = () => {
  // context and hooks
  const { batchableCart, setBatchableCart, updateCartItem, deleteCartItem } = useContext(InventoryPlotContext);
  const { isLoading, data: genericJobTypes } = useQuery({
    queryKey: ['todos'],
    queryFn: () => getJobTranslationTypes(),
  });

  return (
    <>
      {/* Batch items */}
      <Stack spacing={1} p={1} bgcolor={grey[100]}>
        {batchableCart.map(cartItem => (
          <SortableItem
            key={cartItem.batchable.item.uuid}
            cartItem={cartItem}
            genericJobTypes={genericJobTypes?.sort()}
            updateCartItem={updateCartItem}
            deleteCartItem={deleteCartItem}
          />
        ))}
        {batchableCart.length === 0 && (
          <Typography variant="caption" color={grey[500]} textAlign="center">
            No items in batch
          </Typography>
        )}
      </Stack>
    </>
  );
};

interface SortableItemProps {
  cartItem: BatchableCartItem;
  genericJobTypes?: string[];
  updateCartItem: (newCartItem: BatchableCartItem) => void;
  deleteCartItem: (batchable: BatchableCartItem) => void;
}
export const SortableItem = ({ cartItem, genericJobTypes, updateCartItem, deleteCartItem }: SortableItemProps) => {
  // context and hooks
  const { destinationId, batchable, jobType } = cartItem;
  const { item } = batchable;
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: item.uuid });
  const [popperAnchor, setPopperAnchor] = useState<HTMLElement | null>(null);
  const isPopperOpen = Boolean(popperAnchor);

  // constants
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  // helpers
  const updateJobType = (newJobType: string) => {
    // if the job type is store, then we need to set the destinationId
    const newCartItem = { ...cartItem, jobType: newJobType };
    updateCartItem(newCartItem);
    closePopper();
  };

  // helper: delete batchable
  const removeSortable = (cartItem: BatchableCartItem) => {
    deleteCartItem(cartItem);
  };

  const openPopper = (event: React.MouseEvent<HTMLAnchorElement>) => {
    setPopperAnchor(event.currentTarget);
  };

  const closePopper = () => {
    setPopperAnchor(null);
  };

  const getDestinationRender = (item: Item) => {
    if (jobType === 'FETCH_INVENTORY' || jobType === 'FETCH_DESIGNATED') {
      return (
        <>
          <Box component={InventoryIcon} color={grey[600]} />
          <Typography textOverflow="ellipsis" overflow="hidden" whiteSpace="nowrap">
            {getItemPriorityBarcode(item)}
          </Typography>
          <Box component={ArrowRightAltIcon} color={grey[600]} />
          <Typography textOverflow="ellipsis" overflow="hidden" whiteSpace="nowrap">
            Robot
          </Typography>
        </>
      );
    }

    if (jobType === 'STORE_INVENTORY' || jobType === 'STORE_DESIGNATED') {
      return (
        <>
          <Box component={SmartToyIcon} color={grey[600]} />
          <Typography textOverflow="ellipsis" overflow="hidden" whiteSpace="nowrap">
            {getItemPriorityBarcode(item)}
          </Typography>
          <Box component={ArrowRightAltIcon} color={grey[600]} />
          <Typography textOverflow="ellipsis" overflow="hidden" whiteSpace="nowrap">
            Inventory
          </Typography>
        </>
      );
    }

    return (
      <Typography textOverflow="ellipsis" overflow="hidden" whiteSpace="nowrap">
        {getItemPriorityBarcode(item)}
      </Typography>
    );
  };

  return (
    <Card ref={setNodeRef} style={style} sx={{ borderRadius: '4px', display: 'flex' }} variant="outlined">
      <Stack width="100%" spacing={1}>
        <Stack justifyContent="space-between" direction="row" alignItems="center">
          <Stack direction="row" alignItems="center" spacing={1}>
            {getDestinationRender(item)}
          </Stack>

          <Box {...attributes} {...listeners} sx={{ cursor: 'grab' }} component={DragIndicatorIcon} />
        </Stack>

        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box width="fit-content">
            <Box onClick={openPopper} href="#" component={Link}>
              <Chip
                color={cartItem.jobType ? 'success' : 'default'}
                variant="outlined"
                label={
                  <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
                    <Typography color={cartItem.jobType ? 'success' : grey[400]} fontWeight={cartItem.jobType ? 600 : 400}>
                      {cartItem.jobType ? cartItem.jobType : 'No job type assigned'}
                    </Typography>
                    <Box component={Edit} height="16px" />
                  </Stack>
                }
              />
            </Box>
          </Box>
          <IconButton sx={{ mr: -1 }} onClick={() => removeSortable(cartItem)}>
            <DeleteIcon />
          </IconButton>
        </Stack>
      </Stack>

      {/* Popper */}
      <Popover
        open={isPopperOpen}
        anchorEl={popperAnchor}
        onClose={closePopper}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
      >
        {genericJobTypes ? (
          <Stack spacing={1}>
            {genericJobTypes.map((jobType, idx) => (
              <Chip
                sx={{ width: 'fit-content' }}
                label={jobType}
                icon={<AddCircleOutlineIcon />}
                color="secondary"
                onClick={() => {
                  updateJobType(jobType);
                }}
                key={idx}
              />
            ))}
          </Stack>
        ) : (
          <CircularProgress />
        )}
      </Popover>
    </Card>
  );
};
