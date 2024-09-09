import { CssBaseline } from "@mui/material";
import { grey } from "@mui/material/colors";
import { ReactNode } from "react";

import { MuiProvider } from "./provider";
import { AppShell } from "@/app/(components)/AppShell";

const PagesLayout = async ({ children }: { children: ReactNode }) => {
  return (
    <MuiProvider>
      <CssBaseline />
      <body style={{ background: grey[200] }}>
        <AppShell>{children}</AppShell>
      </body>
    </MuiProvider>
  );
};
export default PagesLayout;
