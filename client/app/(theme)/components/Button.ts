import { Components } from '@mui/material';

export const MuiButton: Pick<Components, 'MuiButton'> = {
  MuiButton: {
    defaultProps: {
      variant: 'contained',
    },
    styleOverrides: {
      root: {
        fontFamily: 'inherit',
        padding: '12px 24px',
        borderRadius: '100px',
        fontSize: '14px',
        textTransform: 'none',
      },
    },
  },
};
