/**
 * Knowledge Graph Module Test Page
 * This page demonstrates the usage of the KnowledgeGraph module
 */
import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Divider, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  FormControlLabel,
  Switch
} from '@mui/material';
import { KnowledgeGraphModule } from './KnowledgeGraph';
import { EntityFilter } from './KnowledgeGraph/types/knowledgeGraph.types'; 
import { ModuleDisplayMode } from './_templates/BaseModule/types/base.types';

const KnowledgeGraphTest: React.FC = () => {
  // State for module configuration
  const [displayMode, setDisplayMode] = useState<ModuleDisplayMode>('list');
  const [readOnly, setReadOnly] = useState(false);
  const [showActions, setShowActions] = useState(true);
  const [showFilters, setShowFilters] = useState(true);
  const [filter, setFilter] = useState<EntityFilter>({});
  const [height, setHeight] = useState<number>(600);

  // Event handlers
  const handleDisplayModeChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setDisplayMode(event.target.value as ModuleDisplayMode);
  };

  const handleReadOnlyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setReadOnly(event.target.checked);
  };

  const handleShowActionsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setShowActions(event.target.checked);
  };

  const handleShowFiltersChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setShowFilters(event.target.checked);
  };

  const handleHeightChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setHeight(Number(event.target.value));
  };

  return (
    <Container maxWidth="lg">
      <Box my={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Knowledge Graph Module Test
        </Typography>
        
        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h6">Module Configuration</Typography>
          <Divider sx={{ my: 2 }} />
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel id="display-mode-label">Display Mode</InputLabel>
              <Select
                labelId="display-mode-label"
                value={displayMode}
                onChange={handleDisplayModeChange}
                label="Display Mode"
              >
                <MenuItem value="list">List</MenuItem>
                <MenuItem value="grid">Grid</MenuItem>
                <MenuItem value="detail">Detail</MenuItem>
                <MenuItem value="form">Form</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel id="height-label">Height</InputLabel>
              <Select
                labelId="height-label"
                value={height}
                onChange={handleHeightChange}
                label="Height"
              >
                <MenuItem value={400}>400px</MenuItem>
                <MenuItem value={600}>600px</MenuItem>
                <MenuItem value={800}>800px</MenuItem>
                <MenuItem value={1000}>1000px</MenuItem>
              </Select>
            </FormControl>
            
            <Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={readOnly}
                    onChange={handleReadOnlyChange}
                    name="readOnly"
                    color="primary"
                  />
                }
                label="Read Only"
              />
            </Box>
            
            <Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={showActions}
                    onChange={handleShowActionsChange}
                    name="showActions"
                    color="primary"
                  />
                }
                label="Show Actions"
              />
            </Box>
            
            <Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={showFilters}
                    onChange={handleShowFiltersChange}
                    name="showFilters"
                    color="primary"
                  />
                }
                label="Show Filters"
              />
            </Box>
          </Box>
        </Paper>

        <Paper sx={{ p: 0 }}>
          <KnowledgeGraphModule
            mode={displayMode}
            readOnly={readOnly}
            showActions={showActions}
            showFilters={showFilters}
            initialFilter={filter}
            height={height}
            width="100%"
            onItemSelect={(item) => console.log('Selected item:', item)}
            onItemCreate={(item) => console.log('Created item:', item)}
            onItemUpdate={(item) => console.log('Updated item:', item)}
            onItemDelete={(id) => console.log('Deleted item with id:', id)}
          />
        </Paper>
      </Box>
    </Container>
  );
};

export default KnowledgeGraphTest;