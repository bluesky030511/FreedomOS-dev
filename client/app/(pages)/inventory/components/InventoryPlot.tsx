'use client';

import BurstModeIcon from '@mui/icons-material/BurstMode';
import RefreshIcon from '@mui/icons-material/Refresh';
import { Box, CircularProgress, IconButton, Stack, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';
import { Barcode, Item } from '@prisma/client';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useContext, useEffect } from 'react';
import toast from 'react-hot-toast';
import Plot from 'react-plotly.js';

import { InventorySkeleton } from './InventorySkeleton';
import { getRender } from '../actions';
import { InventoryPlotContext } from '../context/InventoryPlotContext';
import { usePlotData } from '../hooks/usePlotData';
import { BarcodeSchema, ItemSchema } from '@/app/(api)/schema/Item';

interface InventoryPlotProps {
  side: string;
  aisle_index: number;
}
const InventoryPlot = ({ side, aisle_index }: InventoryPlotProps) => {
  // contexnt and hooks
  const { setSelectedItem } = useContext(InventoryPlotContext);
  const {
    data,
    isPending,
    mutate: triggerRender,
  } = useMutation({
    mutationFn: () => getRender({ side, aisle_index }),
  });

  const { getPlotData, getPlotImages } = usePlotData({
    data: data?.render,
    imageUrl: data?.imageUrl,
    dataSettings: {
      type: 'scatter',
      mode: 'lines',
      fill: 'toself',
      showlegend: false,
    },
  });

  useEffect(() => {
    triggerRender();
  }, [side, aisle_index]);

  if (isPending) {
    return (
      <InventorySkeleton>
        <CircularProgress />
      </InventorySkeleton>
    );
  }

  if (!data) {
    return (
      <InventorySkeleton>
        <Typography>No data</Typography>
      </InventorySkeleton>
    );
  }

  return (
    <Box>
      <Stack position="absolute" zIndex="2" direction="row">
        <IconButton onClick={() => triggerRender()}>
          <RefreshIcon />
        </IconButton>

        <IconButton onClick={() => toast.success('Auto-fixing high')}>
          <BurstModeIcon />
        </IconButton>
      </Stack>
      <Box border={`1px solid ${grey[300]}`} height="400px" width="100%" borderRadius="5px" overflow="clip" zIndex="1">
        <Plot
          onClick={event => {
            if (event.points.length > 0) {
              const itemType = event.points[0].data.labels[0]?.toString(); // box, barcode, or empty
              const pointMetadata = event.points[0].data.customdata[0] as any;
              const itemOrBarcode = pointMetadata as Item | Barcode;

              if (!itemType) {
                return;
              }
              toast.success(`Selected ${itemType}`);

              // validate to barcode
              if (itemType === 'barcode') {
                const result = BarcodeSchema.safeParse(itemOrBarcode);
                if (!result.success) return;

                setSelectedItem({ itemType, item: result.data });
              }

              // validate to item
              else if (itemType === 'empty' || itemType === 'box') {
                const result = ItemSchema.safeParse(itemOrBarcode);
                if (!result.success) return;

                setSelectedItem({ itemType, item: result.data });
              } else {
                toast.error('Invalid item type');
              }
            }
          }}
          data={getPlotData()}
          style={{ width: '100%', height: '100%' }}
          layout={{
            margin: {
              t: 40,
              b: 50,
            },
            modebar: {
              orientation: 'v',
            },
            yaxis: {
              scaleanchor: 'x',
              scaleratio: 1,
            },
            images: getPlotImages(),
            uirevision: 'true',
            autosize: true,
            dragmode: 'pan',
            showlegend: false,
          }}
          config={{
            responsive: true,
            scrollZoom: true,
            displaylogo: false,
          }}
        />
      </Box>
    </Box>
  );
};

export default InventoryPlot;
