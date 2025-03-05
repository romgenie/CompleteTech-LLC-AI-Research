import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { TagFilter } from './Tags';
import { ResearchFilterOptions } from '../types/research';

interface ResearchFilterPanelProps {
  onFilterChange: (filters: ResearchFilterOptions) => void;
  availableTags: string[];
  expanded?: boolean;
}

/**
 * Panel component for filtering research queries
 */
const ResearchFilterPanel: React.FC<ResearchFilterPanelProps> = ({
  onFilterChange,
  availableTags,
  expanded = false
}) => {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFavorites, setShowFavorites] = useState(false);
  const [fromDate, setFromDate] = useState<Date | null>(null);
  const [toDate, setToDate] = useState<Date | null>(null);
  const [isExpanded, setIsExpanded] = useState(expanded);

  // Apply filters
  const applyFilters = () => {
    onFilterChange({
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      favorites: showFavorites || undefined,
      searchTerm: searchTerm || undefined,
      dateRange: (fromDate || toDate) ? {
        from: fromDate,
        to: toDate
      } : undefined
    });
  };

  // Reset filters
  const resetFilters = () => {
    setSelectedTags([]);
    setSearchTerm('');
    setShowFavorites(false);
    setFromDate(null);
    setToDate(null);
    
    onFilterChange({});
  };

  // Handle tag selection
  const handleTagSelect = (tag: string) => {
    setSelectedTags(prev => [...prev, tag]);
  };

  // Handle tag removal
  const handleTagRemove = (tag: string) => {
    setSelectedTags(prev => prev.filter(t => t !== tag));
  };

  return (
    <Accordion 
      expanded={isExpanded} 
      onChange={() => setIsExpanded(!isExpanded)}
      elevation={3}
      sx={{ mb: 2 }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography variant="h6">Filter Results</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Box component={Paper} variant="outlined" sx={{ p: 2 }}>
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>Search Terms</Typography>
            <TextField
              fullWidth
              placeholder="Search in queries..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="small"
            />
          </Box>
          
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>Tags</Typography>
            <TagFilter
              availableTags={availableTags}
              selectedTags={selectedTags}
              onTagSelect={handleTagSelect}
              onTagRemove={handleTagRemove}
            />
          </Box>
          
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>Date Range</Typography>
            <Box display="flex" gap={2}>
              <DatePicker
                label="From"
                value={fromDate}
                onChange={setFromDate}
                slotProps={{ textField: { size: 'small', fullWidth: true } }}
              />
              <DatePicker
                label="To"
                value={toDate}
                onChange={setToDate}
                slotProps={{ textField: { size: 'small', fullWidth: true } }}
              />
            </Box>
          </Box>
          
          <Box mb={2}>
            <FormControlLabel
              control={
                <Checkbox 
                  checked={showFavorites}
                  onChange={(e) => setShowFavorites(e.target.checked)}
                />
              }
              label="Show favorites only"
            />
          </Box>
          
          <Divider sx={{ my: 2 }} />
          
          <Box display="flex" justifyContent="flex-end" gap={1}>
            <Button variant="outlined" onClick={resetFilters}>
              Reset
            </Button>
            <Button variant="contained" onClick={applyFilters}>
              Apply Filters
            </Button>
          </Box>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default ResearchFilterPanel;