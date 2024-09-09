import { Components } from "@mui/material";

export const MuiCssBaseline: Pick<Components, "MuiCssBaseline"> = {
  MuiCssBaseline: {
    styleOverrides: `
    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 100;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 100;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 200;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 200;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 300;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 300;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 400;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 400;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 500;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 500;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 600;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 600;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 700;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 700;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 800;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 800;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    @font-face {
      font-family: 'Switzer';
      font-style: normal;
      font-weight: 900;
      src: url('/fonts/Switzer-Variable.ttf') format('truetype');
    }

    @font-face {
      font-family: 'Switzer';
      font-style: italic;
      font-weight: 900;
      src: url('/fonts/Switzer-VariableItalic.ttf') format("truetype");
    }

    * {
      font-family: 'Switzer', sans-serif;
    }
  `,
  },
};
