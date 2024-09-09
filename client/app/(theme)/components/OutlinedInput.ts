import { Components } from '@mui/material';

export const MuiOutlinedInput: Pick<Components, 'MuiOutlinedInput'> = {
  MuiOutlinedInput: {
    styleOverrides: {
      root: {
        '& input': {
          fontFamily: 'Switzer ',
          fontSize: '14px',
        },
      },
    },
  },
};
