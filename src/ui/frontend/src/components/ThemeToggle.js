import React from 'react';
import { 
  IconButton, 
  Box, 
  Tooltip,
  FormControlLabel,
  Switch,
  Typography,
  Divider,
  MenuItem,
  Menu
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import ContrastIcon from '@mui/icons-material/Contrast';
import SettingsIcon from '@mui/icons-material/Settings';
import { useTheme, THEME_MODES } from '../contexts/ThemeContext';

/**
 * A component for changing theme settings (dark mode and high contrast mode)
 * Provides a simple toggle button and an expanded menu
 */
const ThemeToggle = ({ showLabels = true }) => {
  const { 
    isDarkMode, 
    toggleDarkMode, 
    isHighContrast,
    toggleHighContrast,
    themeMode,
    setThemeMode
  } = useTheme();

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleModeSelect = (mode) => {
    setThemeMode(mode);
    handleClose();
  };

  return (
    <Box>
      {/* Main toggle button */}
      <Tooltip title="Theme settings">
        <IconButton
          onClick={handleClick}
          color="inherit"
          aria-label="Theme settings"
          aria-controls={open ? 'theme-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
        >
          <SettingsIcon />
        </IconButton>
      </Tooltip>

      {/* Theme settings menu */}
      <Menu
        id="theme-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'theme-button',
          dense: true,
          sx: { minWidth: 220 }
        }}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Theme Settings
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={isDarkMode}
                onChange={toggleDarkMode}
                inputProps={{
                  'aria-label': 'Dark mode toggle',
                }}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {isDarkMode ? <Brightness4Icon sx={{ mr: 1 }} /> : <Brightness7Icon sx={{ mr: 1 }} />}
                <Typography variant="body2">{isDarkMode ? 'Dark Mode' : 'Light Mode'}</Typography>
              </Box>
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={isHighContrast}
                onChange={toggleHighContrast}
                inputProps={{
                  'aria-label': 'High contrast mode toggle',
                }}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ContrastIcon sx={{ mr: 1 }} />
                <Typography variant="body2">High Contrast</Typography>
              </Box>
            }
          />
        </Box>
        
        <Divider />
        
        <MenuItem 
          onClick={() => handleModeSelect(THEME_MODES.LIGHT)}
          selected={themeMode === THEME_MODES.LIGHT}
        >
          <Brightness7Icon sx={{ mr: 1 }} />
          <Typography variant="body2">Standard Light</Typography>
        </MenuItem>
        
        <MenuItem 
          onClick={() => handleModeSelect(THEME_MODES.DARK)}
          selected={themeMode === THEME_MODES.DARK}
        >
          <Brightness4Icon sx={{ mr: 1 }} />
          <Typography variant="body2">Standard Dark</Typography>
        </MenuItem>
        
        <MenuItem 
          onClick={() => handleModeSelect(THEME_MODES.HIGH_CONTRAST_LIGHT)}
          selected={themeMode === THEME_MODES.HIGH_CONTRAST_LIGHT}
        >
          <ContrastIcon sx={{ mr: 1 }} />
          <Typography variant="body2">High Contrast Light</Typography>
        </MenuItem>
        
        <MenuItem 
          onClick={() => handleModeSelect(THEME_MODES.HIGH_CONTRAST_DARK)}
          selected={themeMode === THEME_MODES.HIGH_CONTRAST_DARK}
        >
          <ContrastIcon sx={{ mr: 1 }} />
          <Typography variant="body2">High Contrast Dark</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ThemeToggle;