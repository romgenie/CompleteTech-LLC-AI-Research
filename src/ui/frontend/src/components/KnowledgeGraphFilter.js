import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Paper,
  Typography,
  Box,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormGroup,
  FormControlLabel,
  Checkbox,
  TextField,
  Slider,
  Button,
  Chip,
  IconButton
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';

/**
 * KnowledgeGraphFilter component for filtering graph nodes and edges
 * 
 * @component
 */
const KnowledgeGraphFilter = ({
  entities,
  relationships,
  onFilterChange,
  defaultExpanded = false
}) => {
  // Extract entity and relationship types
  const entityTypes = [...new Set(entities.map(entity => entity.type))];
  const relationshipTypes = [...new Set(relationships.map(rel => rel.type))];
  
  // Filter state
  const [filters, setFilters] = useState({
    entityTypes: entityTypes.reduce((acc, type) => ({ ...acc, [type]: true }), {}),
    relationshipTypes: relationshipTypes.reduce((acc, type) => ({ ...acc, [type]: true }), {}),
    searchTerm: '',
    confidenceThreshold: 0,
    yearRange: [2015, 2025],
    activeFilters: [] // Tracks which filters are actively applied
  });
  
  // Year range calculations
  const minYear = Math.min(...entities.map(e => Number(e.properties?.year) || 2015));
  const maxYear = Math.max(...entities.map(e => Number(e.properties?.year) || 2025));
  const [yearRange, setYearRange] = useState([minYear, maxYear]);
  
  // Apply filters to the graph data
  useEffect(() => {
    // Build active filters list for display
    const activeFilters = [];
    
    // Entity type filters
    const disabledEntityTypes = Object.entries(filters.entityTypes)
      .filter(([_, enabled]) => !enabled)
      .map(([type]) => type);
      
    if (disabledEntityTypes.length > 0) {
      activeFilters.push({
        id: 'entityTypes',
        label: `Entity Types: ${entityTypes.length - disabledEntityTypes.length}/${entityTypes.length}`,
        value: disabledEntityTypes
      });
    }
    
    // Relationship type filters
    const disabledRelationshipTypes = Object.entries(filters.relationshipTypes)
      .filter(([_, enabled]) => !enabled)
      .map(([type]) => type);
      
    if (disabledRelationshipTypes.length > 0) {
      activeFilters.push({
        id: 'relationshipTypes',
        label: `Relationship Types: ${relationshipTypes.length - disabledRelationshipTypes.length}/${relationshipTypes.length}`,
        value: disabledRelationshipTypes
      });
    }
    
    // Search term filter
    if (filters.searchTerm) {
      activeFilters.push({
        id: 'searchTerm',
        label: `Search: "${filters.searchTerm}"`,
        value: filters.searchTerm
      });
    }
    
    // Confidence threshold filter
    if (filters.confidenceThreshold > 0) {
      activeFilters.push({
        id: 'confidenceThreshold',
        label: `Min Confidence: ${filters.confidenceThreshold}`,
        value: filters.confidenceThreshold
      });
    }
    
    // Year range filter
    if (yearRange[0] > minYear || yearRange[1] < maxYear) {
      activeFilters.push({
        id: 'yearRange',
        label: `Years: ${yearRange[0]}-${yearRange[1]}`,
        value: yearRange
      });
    }
    
    setFilters(prev => ({ ...prev, activeFilters }));
    
    // Call the parent component with the filtered data
    const filteredEntities = entities.filter(entity => {
      // Entity type filter
      if (!filters.entityTypes[entity.type]) return false;
      
      // Search term filter
      if (filters.searchTerm && !entity.name.toLowerCase().includes(filters.searchTerm.toLowerCase())) {
        return false;
      }
      
      // Confidence threshold filter
      const confidence = parseFloat(entity.properties?.confidence || '0');
      if (confidence < filters.confidenceThreshold) return false;
      
      // Year range filter
      const year = parseInt(entity.properties?.year || '0');
      if (year && (year < yearRange[0] || year > yearRange[1])) return false;
      
      return true;
    });
    
    // Get IDs of filtered entities for relationship filtering
    const filteredEntityIds = filteredEntities.map(e => e.id);
    
    // Filter relationships
    const filteredRelationships = relationships.filter(rel => {
      // Relationship type filter
      if (!filters.relationshipTypes[rel.type]) return false;
      
      // Source and target must be in filtered entities
      if (!filteredEntityIds.includes(rel.source) || !filteredEntityIds.includes(rel.target)) {
        return false;
      }
      
      // Confidence threshold filter
      const confidence = parseFloat(rel.properties?.confidence || '0');
      if (confidence < filters.confidenceThreshold) return false;
      
      return true;
    });
    
    onFilterChange({
      entities: filteredEntities,
      relationships: filteredRelationships
    });
  }, [
    filters.entityTypes, 
    filters.relationshipTypes, 
    filters.searchTerm, 
    filters.confidenceThreshold,
    yearRange,
    entities,
    relationships,
    onFilterChange,
    minYear,
    maxYear
  ]);
  
  // Handle entity type filter change
  const handleEntityTypeChange = (type) => {
    setFilters(prev => ({
      ...prev,
      entityTypes: {
        ...prev.entityTypes,
        [type]: !prev.entityTypes[type]
      }
    }));
  };
  
  // Handle relationship type filter change
  const handleRelationshipTypeChange = (type) => {
    setFilters(prev => ({
      ...prev,
      relationshipTypes: {
        ...prev.relationshipTypes,
        [type]: !prev.relationshipTypes[type]
      }
    }));
  };
  
  // Handle search term change
  const handleSearchChange = (event) => {
    setFilters(prev => ({
      ...prev,
      searchTerm: event.target.value
    }));
  };
  
  // Handle confidence threshold change
  const handleConfidenceChange = (event, newValue) => {
    setFilters(prev => ({
      ...prev,
      confidenceThreshold: newValue
    }));
  };
  
  // Handle year range change
  const handleYearRangeChange = (event, newValue) => {
    setYearRange(newValue);
  };
  
  // Handle reset filters
  const handleResetFilters = () => {
    setFilters({
      entityTypes: entityTypes.reduce((acc, type) => ({ ...acc, [type]: true }), {}),
      relationshipTypes: relationshipTypes.reduce((acc, type) => ({ ...acc, [type]: true }), {}),
      searchTerm: '',
      confidenceThreshold: 0,
      activeFilters: []
    });
    setYearRange([minYear, maxYear]);
  };
  
  // Handle removing a specific filter
  const handleRemoveFilter = (filterId) => {
    if (filterId === 'entityTypes') {
      setFilters(prev => ({
        ...prev,
        entityTypes: entityTypes.reduce((acc, type) => ({ ...acc, [type]: true }), {})
      }));
    } else if (filterId === 'relationshipTypes') {
      setFilters(prev => ({
        ...prev,
        relationshipTypes: relationshipTypes.reduce((acc, type) => ({ ...acc, [type]: true }), {})
      }));
    } else if (filterId === 'searchTerm') {
      setFilters(prev => ({
        ...prev,
        searchTerm: ''
      }));
    } else if (filterId === 'confidenceThreshold') {
      setFilters(prev => ({
        ...prev,
        confidenceThreshold: 0
      }));
    } else if (filterId === 'yearRange') {
      setYearRange([minYear, maxYear]);
    }
  };
  
  // Helper function to get entity color by type
  const getEntityColor = (type) => {
    switch (type) {
      case 'MODEL':
        return '#1976d2'; // primary blue
      case 'DATASET':
        return '#9c27b0'; // purple
      case 'PAPER':
        return '#ed6c02'; // orange
      case 'AUTHOR':
        return '#2e7d32'; // green
      case 'ALGORITHM':
        return '#d32f2f'; // red
      case 'FRAMEWORK':
        return '#0288d1'; // light blue
      case 'METRIC':
        return '#ffc107'; // amber
      default:
        return '#757575'; // grey
    }
  };
  
  return (
    <Paper elevation={3} sx={{ p: 0 }}>
      {/* Filter header with active filters */}
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <FilterListIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="h2">
            Graph Filters
          </Typography>
          
          <Button 
            size="small" 
            onClick={handleResetFilters}
            disabled={filters.activeFilters.length === 0}
            sx={{ ml: 'auto' }}
          >
            Reset All
          </Button>
        </Box>
        
        {/* Active filters display */}
        {filters.activeFilters.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
            {filters.activeFilters.map(filter => (
              <Chip
                key={filter.id}
                label={filter.label}
                onDelete={() => handleRemoveFilter(filter.id)}
                size="small"
              />
            ))}
          </Box>
        )}
      </Box>
      
      <Divider />
      
      {/* Expandable filter sections */}
      <Accordion defaultExpanded={defaultExpanded}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Search & Filter Options</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {/* Search box */}
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              size="small"
              label="Search nodes"
              variant="outlined"
              value={filters.searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: <SearchIcon sx={{ color: 'action.active', mr: 1 }} />,
                endAdornment: filters.searchTerm ? (
                  <IconButton 
                    size="small" 
                    onClick={() => setFilters(prev => ({ ...prev, searchTerm: '' }))}
                    edge="end"
                  >
                    <ClearIcon fontSize="small" />
                  </IconButton>
                ) : null
              }}
            />
          </Box>
          
          {/* Entity type filters */}
          <Typography variant="subtitle2" gutterBottom>
            Entity Types
          </Typography>
          <FormGroup sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
              {entityTypes.map(type => (
                <FormControlLabel
                  key={type}
                  control={
                    <Checkbox 
                      checked={filters.entityTypes[type]} 
                      onChange={() => handleEntityTypeChange(type)}
                      size="small"
                      sx={{
                        color: getEntityColor(type),
                        '&.Mui-checked': {
                          color: getEntityColor(type),
                        },
                      }}
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2">{type}</Typography>
                      <Chip 
                        size="small" 
                        label={entities.filter(e => e.type === type).length}
                        sx={{ ml: 1, height: 20, minWidth: 30 }}
                      />
                    </Box>
                  }
                  sx={{ width: '50%', mr: 0 }}
                />
              ))}
            </Box>
          </FormGroup>
          
          {/* Relationship type filters */}
          <Typography variant="subtitle2" gutterBottom>
            Relationship Types
          </Typography>
          <FormGroup sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
              {relationshipTypes.map(type => (
                <FormControlLabel
                  key={type}
                  control={
                    <Checkbox 
                      checked={filters.relationshipTypes[type]} 
                      onChange={() => handleRelationshipTypeChange(type)}
                      size="small"
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2">{type}</Typography>
                      <Chip 
                        size="small" 
                        label={relationships.filter(r => r.type === type).length}
                        sx={{ ml: 1, height: 20, minWidth: 30 }}
                      />
                    </Box>
                  }
                  sx={{ width: '50%', mr: 0 }}
                />
              ))}
            </Box>
          </FormGroup>
          
          {/* Confidence threshold */}
          <Typography variant="subtitle2" gutterBottom>
            Minimum Confidence: {filters.confidenceThreshold}
          </Typography>
          <Box sx={{ px: 1, mb: 3 }}>
            <Slider
              value={filters.confidenceThreshold}
              onChange={handleConfidenceChange}
              step={0.05}
              min={0}
              max={1}
              valueLabelDisplay="auto"
              valueLabelFormat={value => (value * 100).toFixed(0) + '%'}
            />
          </Box>
          
          {/* Year range filter */}
          <Typography variant="subtitle2" gutterBottom>
            Year Range: {yearRange[0]} - {yearRange[1]}
          </Typography>
          <Box sx={{ px: 1, mb: 1 }}>
            <Slider
              value={yearRange}
              onChange={handleYearRangeChange}
              step={1}
              min={minYear}
              max={maxYear}
              valueLabelDisplay="auto"
              disableSwap
            />
          </Box>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

KnowledgeGraphFilter.propTypes = {
  /** Array of entity objects to filter */
  entities: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      properties: PropTypes.object
    })
  ).isRequired,
  
  /** Array of relationship objects to filter */
  relationships: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      source: PropTypes.string.isRequired,
      target: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      properties: PropTypes.object
    })
  ).isRequired,
  
  /** Callback function when filters change */
  onFilterChange: PropTypes.func.isRequired,
  
  /** Whether filter accordion is expanded by default */
  defaultExpanded: PropTypes.bool
};

export default KnowledgeGraphFilter;