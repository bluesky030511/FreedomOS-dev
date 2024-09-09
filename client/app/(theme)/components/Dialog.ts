import { Components } from '@mui/material';

export const MuiDialog: Pick<Components, 'MuiDialog'> = {
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: '10px',
        padding: '16px',
      },
    },
  },
};
