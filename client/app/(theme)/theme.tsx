import { ThemeOptions, createTheme } from "@mui/material/styles";

import {
  ComponentTheme as components,
  TypographyTheme as typography,
} from "./components";

export const themeOptions: ThemeOptions = { ...typography, ...components };

export const theme = createTheme(themeOptions);
