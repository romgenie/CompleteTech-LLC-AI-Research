import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
  Button,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Search as SearchIcon,
  AccountTree as GraphIcon,
  Code as CodeIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { NotificationCenter } from './index';
import ThemeToggle from './ThemeToggle';

// Drawer width for desktop
const drawerWidth = 240;

/**
 * Main layout component with navigation drawer and app bar.
 * 
 * @returns {React.ReactElement} Layout component
 */
function Layout() {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { themeMode, isDarkMode } = useTheme();
  // Use the Material-UI hook for breakpoint checking
  const isMobile = useMediaQuery((theme) => theme.breakpoints.down('md'));

  // Navigation items
  const navItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Research', icon: <SearchIcon />, path: '/research' },
    { text: 'Knowledge Graph', icon: <GraphIcon />, path: '/knowledge-graph' },
    { text: 'Implementation', icon: <CodeIcon />, path: '/implementation' },
  ];

  const handleDrawerToggle = () => {
    setMobileDrawerOpen(!mobileDrawerOpen);
  };

  const handleNavClick = (path) => {
    navigate(path);
    if (isMobile) {
      setMobileDrawerOpen(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Content for the drawer
  const drawerContent = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          AI Research
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavClick(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        {/* Theme settings in drawer */}
        <ListItem>
          <ThemeToggle showLabels={true} />
        </ListItem>
        <Divider />
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {navItems.find(item => item.path === location.pathname)?.text || 'AI Research Integration'}
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {currentUser?.username}
          </Typography>
          
          {/* Theme Toggle */}
          <Box sx={{ mr: 2 }}>
            <ThemeToggle />
          </Box>
          
          {/* Notification Center */}
          <Box sx={{ mr: 2 }}>
            <NotificationCenter maxNotifications={15} />
          </Box>
          
          <Button color="inherit" onClick={handleLogout} sx={{ display: { xs: 'none', sm: 'block' } }}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer - Mobile (temporary) */}
      <Drawer
        variant="temporary"
        open={mobileDrawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* Navigation Drawer - Desktop (permanent) */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
        open
      >
        {drawerContent}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { xs: '100%', md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          mt: '64px', // AppBar height
          overflow: 'auto',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}

export default Layout;