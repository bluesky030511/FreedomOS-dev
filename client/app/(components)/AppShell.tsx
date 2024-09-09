'use client';

import { ComputerDesktopIcon, StarIcon, EnvelopeIcon } from '@heroicons/react/24/outline';
import MenuIcon from '@mui/icons-material/Menu';
import {
  AppBar,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material';
import Link from 'next/link';
import { ReactNode, useState } from 'react';
import { Toaster } from 'react-hot-toast';

const drawerContent = (
  <div>
    <Toolbar>
      <Typography variant="h5" fontWeight="800">
        FREEDOM
      </Typography>
      <Typography variant="h5" fontWeight="300">
        OS
      </Typography>
    </Toolbar>

    <Divider />
    <List>
      {[
        { text: 'Inventory', path: '/inventory', icon: <ComputerDesktopIcon /> },
        { text: 'Starred', path: '/starred', icon: <StarIcon /> },
        { text: 'Send email', path: '/send-email', icon: <EnvelopeIcon /> },
      ].map(({ text, path, icon }) => (
        <ListItem key={text} disablePadding>
          <Link href={path} passHref legacyBehavior>
            <ListItemButton component="a" sx={{ textDecoration: 'none', color: 'inherit' }}>
              <ListItemIcon sx={{ minWidth: '1rem' }}>
                <Box width="1rem" height="1rem" mr={1}>
                  {icon}
                </Box>
              </ListItemIcon>
              <ListItemText primary={text} />
            </ListItemButton>
          </Link>
        </ListItem>
      ))}
    </List>
    <Divider />
  </div>
);

export const AppShell = ({ children }: { children: ReactNode }) => {
  const [openDrawer, setOpenDrawer] = useState(false);

  return (
    <Box sx={{ display: 'flex' }}>
      {/* React hot toast */}
      <Toaster position="bottom-right" />

      {/* side drawer */}
      <Box component="nav" sx={{ width: { md: '240px' }, flexShrink: { md: 0 } }} aria-label="mailbox folders">
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          variant="temporary"
          open={openDrawer}
          onClose={() => setOpenDrawer(!openDrawer)}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: '240px',
            },
          }}
        >
          {drawerContent}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: '240px',
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box width="100%">
        <AppBar position="sticky" sx={{ top: 0 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={() => setOpenDrawer(!openDrawer)}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              Inventory
            </Typography>
          </Toolbar>
        </AppBar>

        <Stack width="100%" p={{ xs: 1, sm: 3 }}>
          {children}
        </Stack>
      </Box>
    </Box>
  );
};
