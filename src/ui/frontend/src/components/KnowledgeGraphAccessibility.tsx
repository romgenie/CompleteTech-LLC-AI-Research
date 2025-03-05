import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  FormControlLabel, 
  Switch, 
  Slider,
  Divider,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Tooltip,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  SelectChangeEvent
} from '@mui/material';
import AccessibilityIcon from '@mui/icons-material/Accessibility';
import AccessibilityNewIcon from '@mui/icons-material/AccessibilityNew';
import ColorLensIcon from '@mui/icons-material/ColorLens';
import KeyboardIcon from '@mui/icons-material/Keyboard';
import TextFormatIcon from '@mui/icons-material/TextFormat';
import ZoomInIcon from '@mui/icons-material/ZoomIn';

interface AccessibilitySettings {
  highContrastMode: boolean;
  largeNodeSize: boolean;
  showTextualAlternative: boolean;
  keyboardNavigationEnabled: boolean;
  reducedMotion: boolean;
  colorBlindMode: 'none' | 'deuteranopia' | 'protanopia' | 'tritanopia';
  minimumLabelSize: number;
  screenReaderAnnouncements: 'minimal' | 'detailed' | 'verbose';
}

interface KnowledgeGraphAccessibilityProps {
  onSettingsChange: (settings: AccessibilitySettings) => void;
  settings: AccessibilitySettings;
}

const DEFAULT_SETTINGS: AccessibilitySettings = {
  highContrastMode: false,
  largeNodeSize: false,
  showTextualAlternative: false,
  keyboardNavigationEnabled: true,
  reducedMotion: false,
  colorBlindMode: 'none',
  minimumLabelSize: 10,
  screenReaderAnnouncements: 'minimal'
};

const KnowledgeGraphAccessibility: React.FC<KnowledgeGraphAccessibilityProps> = ({
  onSettingsChange,
  settings = DEFAULT_SETTINGS
}) => {
  const [currentSettings, setCurrentSettings] = useState<AccessibilitySettings>(settings);
  
  useEffect(() => {
    onSettingsChange(currentSettings);
  }, [currentSettings, onSettingsChange]);
  
  const handleSettingChange = <K extends keyof AccessibilitySettings>(
    key: K, 
    value: AccessibilitySettings[K]
  ) => {
    setCurrentSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const resetToDefaults = () => {
    setCurrentSettings(DEFAULT_SETTINGS);
  };
  
  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" mb={2}>
        <AccessibilityIcon sx={{ mr: 1 }} color="primary" />
        <Typography variant="h5">
          Accessibility Settings
        </Typography>
      </Box>
      
      <Typography variant="body2" paragraph color="text.secondary">
        Configure accessibility options for the Knowledge Graph visualization to ensure it works well for all users.
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        These settings optimize the Knowledge Graph visualization for different needs. Changes take effect immediately.
      </Alert>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <ColorLensIcon sx={{ mr: 1 }} color="primary" fontSize="small" />
                <Typography variant="subtitle1" fontWeight="medium">
                  Visual Preferences
                </Typography>
              </Box>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={currentSettings.highContrastMode}
                    onChange={(e) => handleSettingChange('highContrastMode', e.target.checked)}
                    color="primary"
                  />
                }
                label="High Contrast Mode"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 7, mt: -1, mb: 2 }}>
                Uses strongly contrasting colors for better visibility
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={currentSettings.largeNodeSize}
                    onChange={(e) => handleSettingChange('largeNodeSize', e.target.checked)}
                    color="primary"
                  />
                }
                label="Large Node Size"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 7, mt: -1, mb: 2 }}>
                Increases the size of nodes for easier selection
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <FormControl fullWidth size="small">
                  <InputLabel id="color-blind-mode-label">Color Blind Mode</InputLabel>
                  <Select
                    labelId="color-blind-mode-label"
                    value={currentSettings.colorBlindMode}
                    label="Color Blind Mode"
                    onChange={(e: SelectChangeEvent) => handleSettingChange(
                      'colorBlindMode', 
                      e.target.value as 'none' | 'deuteranopia' | 'protanopia' | 'tritanopia'
                    )}
                  >
                    <MenuItem value="none">None</MenuItem>
                    <MenuItem value="deuteranopia">Deuteranopia (Red-Green)</MenuItem>
                    <MenuItem value="protanopia">Protanopia (Red-Green)</MenuItem>
                    <MenuItem value="tritanopia">Tritanopia (Blue-Yellow)</MenuItem>
                  </Select>
                </FormControl>
                <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                  Adjusts colors to be distinguishable with different types of color blindness
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" id="minimum-label-size-slider" gutterBottom>
                  Minimum Label Size: {currentSettings.minimumLabelSize}px
                </Typography>
                <Slider
                  value={currentSettings.minimumLabelSize}
                  onChange={(_, value) => handleSettingChange('minimumLabelSize', value as number)}
                  min={8}
                  max={24}
                  step={2}
                  valueLabelDisplay="auto"
                  aria-labelledby="minimum-label-size-slider"
                />
                <Typography variant="caption" display="block" color="text.secondary">
                  Sets the minimum size for node labels
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <AccessibilityNewIcon sx={{ mr: 1 }} color="primary" fontSize="small" />
                <Typography variant="subtitle1" fontWeight="medium">
                  Interaction & Navigation
                </Typography>
              </Box>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={currentSettings.keyboardNavigationEnabled}
                    onChange={(e) => handleSettingChange('keyboardNavigationEnabled', e.target.checked)}
                    color="primary"
                  />
                }
                label="Keyboard Navigation"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 7, mt: -1, mb: 2 }}>
                Enables navigating the graph using arrow keys and keyboard shortcuts
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={currentSettings.reducedMotion}
                    onChange={(e) => handleSettingChange('reducedMotion', e.target.checked)}
                    color="primary"
                  />
                }
                label="Reduced Motion"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 7, mt: -1, mb: 2 }}>
                Minimizes animations and transitions for users sensitive to motion
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={currentSettings.showTextualAlternative}
                    onChange={(e) => handleSettingChange('showTextualAlternative', e.target.checked)}
                    color="primary"
                  />
                }
                label="Show Textual Alternative"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 7, mt: -1, mb: 2 }}>
                Displays a text-based view of the graph alongside the visualization
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <FormControl fullWidth size="small">
                  <InputLabel id="screen-reader-announcements-label">Screen Reader Verbosity</InputLabel>
                  <Select
                    labelId="screen-reader-announcements-label"
                    value={currentSettings.screenReaderAnnouncements}
                    label="Screen Reader Verbosity"
                    onChange={(e: SelectChangeEvent) => handleSettingChange(
                      'screenReaderAnnouncements', 
                      e.target.value as 'minimal' | 'detailed' | 'verbose'
                    )}
                  >
                    <MenuItem value="minimal">Minimal (Essential Information)</MenuItem>
                    <MenuItem value="detailed">Detailed (More Context)</MenuItem>
                    <MenuItem value="verbose">Verbose (All Details)</MenuItem>
                  </Select>
                </FormControl>
                <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                  Controls how much information is announced to screen readers
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Divider sx={{ my: 3 }} />
      
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Keyboard Shortcuts
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Typography variant="body2">
                <code>←/→</code>: Navigate between nodes
              </Typography>
              <Typography variant="body2">
                <code>Home/End</code>: Jump to first/last node
              </Typography>
              <Typography variant="body2">
                <code>Enter/Space</code>: Select focused node
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Typography variant="body2">
                <code>+/-</code>: Zoom in/out
              </Typography>
              <Typography variant="body2">
                <code>0</code>: Reset zoom
              </Typography>
              <Typography variant="body2">
                <code>Esc</code>: Clear selection
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button variant="outlined" onClick={resetToDefaults} sx={{ mr: 1 }}>
          Reset to Defaults
        </Button>
        <Button variant="contained" onClick={() => onSettingsChange(currentSettings)}>
          Apply Settings
        </Button>
      </Box>
    </Paper>
  );
};

export default KnowledgeGraphAccessibility;