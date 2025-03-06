/**
 * Knowledge Graph entity form component (stub implementation)
 */
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Typography, 
  Alert, 
  CircularProgress,
  Grid,
  Divider,
  Paper,
  IconButton
} from '@mui/material';
import { ArrowBack, Save, Cancel, Add, Delete } from '@mui/icons-material';
import { Entity, EntityType } from '../types/knowledgeGraph.types';

interface EntityFormProps {
  item?: Entity;
  onSubmit: (data: Partial<Entity>) => void;
  onCancel?: () => void;
  loading?: boolean;
  error?: Error | null;
}

export const EntityForm: React.FC<EntityFormProps> = ({
  item,
  onSubmit,
  onCancel,
  loading = false,
  error = null
}) => {
  const [name, setName] = useState('');
  const [type, setType] = useState<EntityType>('MODEL');
  const [description, setDescription] = useState('');
  const [properties, setProperties] = useState<Record<string, any>>({});
  const [newPropertyKey, setNewPropertyKey] = useState('');
  const [newPropertyValue, setNewPropertyValue] = useState('');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Initialize form with item data when available
  useEffect(() => {
    if (item) {
      setName(item.name || '');
      setType(item.type || 'MODEL');
      setDescription(item.description || '');
      setProperties(item.properties || {});
    }
  }, [item]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!name.trim()) {
      errors.name = 'Name is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    const formData: Partial<Entity> = {
      name,
      type,
      description: description || undefined,
      properties,
    };
    
    onSubmit(formData);
  };

  const addProperty = () => {
    if (newPropertyKey.trim() && newPropertyValue.trim()) {
      setProperties(prev => ({
        ...prev,
        [newPropertyKey]: newPropertyValue
      }));
      setNewPropertyKey('');
      setNewPropertyValue('');
    }
  };

  const removeProperty = (key: string) => {
    setProperties(prev => {
      const newProps = { ...prev };
      delete newProps[key];
      return newProps;
    });
  };

  const entityTypes: EntityType[] = [
    'MODEL', 
    'ALGORITHM', 
    'DATASET', 
    'PAPER', 
    'AUTHOR', 
    'METHOD',
    'FINDING',
    'METRIC',
    'CODE',
    'CONCEPT',
    'FRAMEWORK'
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Typography variant="h5" component="h2" gutterBottom>
        {item ? 'Edit Entity' : 'Create New Entity'}
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error.message}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={8}>
            <TextField
              label="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              required
              error={!!formErrors.name}
              helperText={formErrors.name}
              sx={{ mb: 2 }}
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="entity-type-label">Type</InputLabel>
              <Select
                labelId="entity-type-label"
                value={type}
                onChange={(e) => setType(e.target.value as EntityType)}
                label="Type"
              >
                {entityTypes.map(type => (
                  <MenuItem key={type} value={type}>{type}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Properties</Typography>
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              {Object.entries(properties).map(([key, value]) => (
                <Box key={key} sx={{ display: 'flex', mb: 1 }}>
                  <TextField
                    label="Property"
                    value={key}
                    disabled
                    size="small"
                    sx={{ mr: 1, flexBasis: '30%' }}
                  />
                  <TextField
                    label="Value"
                    value={value}
                    disabled
                    size="small"
                    sx={{ flexGrow: 1 }}
                  />
                  <IconButton 
                    color="error" 
                    onClick={() => removeProperty(key)}
                    sx={{ ml: 1 }}
                  >
                    <Delete />
                  </IconButton>
                </Box>
              ))}
              
              <Box sx={{ display: 'flex', mt: 2 }}>
                <TextField
                  label="New Property"
                  value={newPropertyKey}
                  onChange={(e) => setNewPropertyKey(e.target.value)}
                  size="small"
                  sx={{ mr: 1, flexBasis: '30%' }}
                />
                <TextField
                  label="Value"
                  value={newPropertyValue}
                  onChange={(e) => setNewPropertyValue(e.target.value)}
                  size="small"
                  sx={{ flexGrow: 1 }}
                />
                <Button 
                  variant="contained" 
                  onClick={addProperty}
                  startIcon={<Add />}
                  disabled={!newPropertyKey.trim() || !newPropertyValue.trim()}
                  sx={{ ml: 1 }}
                >
                  Add
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
          {onCancel && (
            <Button 
              variant="outlined" 
              onClick={onCancel}
              startIcon={<Cancel />}
              sx={{ mr: 1 }}
            >
              Cancel
            </Button>
          )}
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            startIcon={<Save />}
            disabled={loading}
          >
            {item ? 'Save Changes' : 'Create Entity'}
          </Button>
        </Box>
      </form>
    </Box>
  );
};