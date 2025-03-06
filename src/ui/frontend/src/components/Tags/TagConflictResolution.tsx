import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  List, 
  ListItem, 
  ListItemText, 
  Radio, 
  RadioGroup, 
  FormControlLabel, 
  Button, 
  Divider, 
  Chip, 
  Alert, 
  CircularProgress
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import MergeIcon from '@mui/icons-material/Merge';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import EditIcon from '@mui/icons-material/Edit';
import CallSplitIcon from '@mui/icons-material/CallSplit';

import { TagConflict, TagConflictOption } from '../../types/research';
import { useTagConflicts, useResolveTagConflict } from '../../services/tagsService';

interface TagConflictResolutionProps {
  onResolved?: () => void;
}

/**
 * Component for resolving tag conflicts
 */
const TagConflictResolution: React.FC<TagConflictResolutionProps> = ({ onResolved }) => {
  const { data: conflicts = [], isLoading, refetch } = useTagConflicts();
  const [selectedOptions, setSelectedOptions] = useState<Record<string, string>>({});
  const resolveMutation = useResolveTagConflict();

  const handleOptionChange = (conflictId: string, optionId: string) => {
    setSelectedOptions({
      ...selectedOptions,
      [conflictId]: optionId
    });
  };

  const handleResolve = async (conflictId: string) => {
    if (!selectedOptions[conflictId]) return;
    
    try {
      await resolveMutation.mutateAsync({
        conflictId,
        selectedOptionId: selectedOptions[conflictId]
      });
      
      // Refetch conflicts after resolution
      refetch();
      
      if (onResolved) {
        onResolved();
      }
    } catch (error) {
      console.error('Failed to resolve conflict:', error);
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'merge': return <MergeIcon />;
      case 'move': return <SwapHorizIcon />;
      case 'rename': return <EditIcon />;
      case 'split': return <CallSplitIcon />;
      default: return null;
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (conflicts.length === 0) {
    return (
      <Alert severity="success" sx={{ mt: 2 }}>
        No tag conflicts to resolve.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <WarningIcon color="warning" sx={{ mr: 1 }} />
        Tag Conflicts to Resolve
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        The following tag conflicts need your attention. Resolving these conflicts will help maintain 
        a consistent taxonomy and improve search and organization capabilities.
      </Typography>
      
      {conflicts.map((conflict) => (
        <Card key={conflict.id} variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              {conflict.description}
            </Typography>
            
            <Chip 
              label={conflict.conflictType.replace(/^\w/, c => c.toUpperCase())}
              color="warning"
              size="small"
              sx={{ mb: 2 }}
            />
            
            <Divider sx={{ my: 2 }} />
            
            <RadioGroup
              value={selectedOptions[conflict.id] || ''}
              onChange={(e) => handleOptionChange(conflict.id, e.target.value)}
            >
              {conflict.options.map((option) => (
                <Box key={option.id} sx={{ mb: 2 }}>
                  <FormControlLabel
                    value={option.id}
                    control={<Radio />}
                    label={
                      <Box>
                        <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center' }}>
                          {getActionIcon(option.action)}
                          <Box component="span" sx={{ ml: 1 }}>{option.description}</Box>
                        </Typography>
                        <Box sx={{ mt: 1, ml: 4 }}>
                          <Chip 
                            size="small" 
                            label={`Action: ${option.action}`} 
                            variant="outlined"
                            sx={{ mr: 1 }}
                          />
                          <Chip 
                            size="small" 
                            label={`Affects ${option.tagIds.length} tag(s)`} 
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    }
                  />
                </Box>
              ))}
            </RadioGroup>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button
                variant="contained"
                color="primary"
                disabled={!selectedOptions[conflict.id]}
                onClick={() => handleResolve(conflict.id)}
              >
                Resolve Conflict
              </Button>
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default TagConflictResolution;