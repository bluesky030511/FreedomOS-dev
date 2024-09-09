import { Box, Card, Skeleton, Stack, Typography } from '@mui/material';
import { grey } from '@mui/material/colors';

interface InventorySkeletonProps {
  children?: React.ReactNode;
}
export const InventorySkeleton = ({ children }: InventorySkeletonProps) => {
  return (
    <Box height="400px" width="100%" display="flex" justifyContent="center" alignItems="center" bgcolor={grey[300]} borderRadius="10px">
      {children}
    </Box>
  );
};

export const InventoryContainerSkeleton = () => {
  return (
    <Stack spacing={2}>
      <Skeleton variant="rectangular" height="32px" width="100px" sx={{ borderRadius: '1000px' }} />

      <InventorySkeleton>
        <Typography>Loading...</Typography>
      </InventorySkeleton>

      <Skeleton variant="rectangular" height="52px" sx={{ borderRadius: '1000px' }} />
      <Skeleton variant="rectangular" height="52px" sx={{ borderRadius: '1000px' }} />
    </Stack>
  );
};
