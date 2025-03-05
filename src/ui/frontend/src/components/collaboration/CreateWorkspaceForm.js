import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  FormLabel,
  FormControlLabel,
  RadioGroup,
  Radio,
  Stack,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  VisibilityOff as PrivateIcon,
  Public as PublicIcon,
  Business as InternalIcon,
} from '@mui/icons-material';
import collaborationService from '../../services/collaborationService';

/**
 * Form component for creating new workspaces
 */
const CreateWorkspaceForm = () => {
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    visibility: 'private',
    tags: []
  });
  
  // UI state
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle tag input
  const handleTagInputKeyDown = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!formData.tags.includes(tagInput.trim())) {
        setFormData(prev => ({
          ...prev,
          tags: [...prev.tags, tagInput.trim()]
        }));
      }
      setTagInput('');
    }
  };

  // Remove tag
  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  // Form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      // Create workspace
      const workspace = await collaborationService.createWorkspace(formData);
      
      setSuccess(true);
      
      // Redirect to the new workspace after a brief delay
      setTimeout(() => {
        navigate(`/workspaces/${workspace.id}`);
      }, 1500);
    } catch (err) {
      setError(err.message);
      console.error('Error creating workspace:', err);
    } finally {
      setLoading(false);
    }
  };

  // Check if form is valid
  const isValid = formData.name.trim() && formData.description.trim();

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Create New Workspace
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Create a workspace to collaborate on research projects with your team
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Workspace created successfully! Redirecting...
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            {/* Workspace Name */}
            <TextField
              label="Workspace Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              fullWidth
            />

            {/* Description */}
            <TextField
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              multiline
              rows={3}
              fullWidth
            />

            {/* Visibility */}
            <FormControl>
              <FormLabel>Visibility</FormLabel>
              <RadioGroup
                name="visibility"
                value={formData.visibility}
                onChange={handleChange}
                row
              >
                <FormControlLabel
                  value="private"
                  control={<Radio />}
                  label={
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <PrivateIcon fontSize="small" />
                      <span>Private</span>
                    </Stack>
                  }
                />
                <FormControlLabel
                  value="internal"
                  control={<Radio />}
                  label={
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <InternalIcon fontSize="small" />
                      <span>Internal</span>
                    </Stack>
                  }
                />
                <FormControlLabel
                  value="public"
                  control={<Radio />}
                  label={
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <PublicIcon fontSize="small" />
                      <span>Public</span>
                    </Stack>
                  }
                />
              </RadioGroup>
            </FormControl>

            {/* Tags */}
            <Box>
              <TextField
                label="Tags"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleTagInputKeyDown}
                placeholder="Add a tag and press Enter"
                fullWidth
                helperText="Press Enter to add a tag"
              />
              
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.tags.length > 0 ? (
                  formData.tags.map(tag => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => handleRemoveTag(tag)}
                      size="small"
                    />
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No tags added yet
                  </Typography>
                )}
              </Box>
            </Box>

            {/* Actions */}
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                type="button"
                onClick={() => navigate('/workspaces')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={!isValid || loading}
                startIcon={loading && <CircularProgress size={20} />}
              >
                Create Workspace
              </Button>
            </Box>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
};

export default CreateWorkspaceForm;