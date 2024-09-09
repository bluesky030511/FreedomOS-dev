import { ThemeOptions } from '@mui/material';

import { MuiButton } from './Button';
import { MuiCard } from './Card';
import { MuiCssBaseline } from './CssBaseline';
import { MuiDialog } from './Dialog';
import { MuiOutlinedInput } from './OutlinedInput';
import { MuiPopover } from './Popover';
import { MuiSkeleton } from './Skeleton';
import { MuiTypography, typography } from './Typography';

export const ComponentTheme: Pick<ThemeOptions, 'components'> = {
  components: {
    ...MuiCard,
    ...MuiSkeleton,
    ...MuiButton,
    ...MuiDialog,
    ...MuiOutlinedInput,
    ...MuiPopover,

    ...MuiCssBaseline,
    ...MuiTypography,
  },
};

export const TypographyTheme = typography;
