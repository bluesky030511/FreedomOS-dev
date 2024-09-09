import { Components } from "@mui/material";
import { TypographyOptions } from "@mui/material/styles/createTypography";

export const typography: TypographyOptions = {
  fontFamily: "Switzer",
  h1: {
    fontFamily: "Switzer",
    fontWeight: 700,
    fontSize: "3rem",
    lineHeight: 1.2,
  },
  h2: {
    fontFamily: "Switzer",
    fontWeight: 700,
    fontSize: "2.5rem",
    lineHeight: 1.3,
  },
  h3: {
    fontFamily: "Switzer",
    fontWeight: 700,
    fontSize: "2rem",
    lineHeight: 1.4,
  },
  h4: {
    fontFamily: "Switzer",
    fontWeight: 700,
    fontSize: "1.75rem",
    lineHeight: 1.4,
  },
  h5: {
    fontFamily: "Switzer",
    fontWeight: 700,
    fontSize: "1.5rem",
    lineHeight: 1.5,
  },
  h6: {
    fontFamily: "Switzer",
    fontWeight: 700,
    fontSize: "1.25rem",
    lineHeight: 1.5,
  },
  subtitle1: {
    fontFamily: "Switzer",
    fontWeight: 500,
    fontSize: "1rem",
    lineHeight: 1.75,
  },
  subtitle2: {
    fontFamily: "Switzer",
    fontWeight: 500,
    fontSize: "0.875rem",
    lineHeight: 1.75,
  },
  body1: {
    fontFamily: "Switzer",
    fontWeight: 400,
    fontSize: "1rem",
    lineHeight: 1.5,
  },
  body2: {
    fontFamily: "Switzer",
    fontWeight: 400,
    fontSize: "0.875rem",
    lineHeight: 1.5,
  },
  button: {
    fontFamily: "Switzer",
    fontWeight: 600,
    fontSize: "0.875rem",
    lineHeight: 1.75,
    textTransform: "uppercase",
  },
  caption: {
    fontFamily: "Switzer",
    fontWeight: 400,
    fontSize: "0.75rem",
    lineHeight: 1.66,
  },
  overline: {
    fontFamily: "Switzer",
    fontWeight: 400,
    fontSize: "0.75rem",
    lineHeight: 2.66,
    textTransform: "uppercase",
  },
};

export const MuiTypography: Pick<Components, "MuiTypography"> = {
  MuiTypography: {
    defaultProps: {
      fontFamily: "Switzer",
      variant: "body2",
    },
  },
};
