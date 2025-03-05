import React, { useState } from 'react';
import { 
  Box,
  TextField,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Typography,
  Chip,
  Paper,
  InputAdornment,
  IconButton,
  CircularProgress,
  Alert,
  Stack
} from '@mui/material';
import { 
  Add as AddIcon,
  Close as CloseIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import collaborationService from '../../services/collaborationService';

/**
 * Form component for creating new collaborative workspaces
 */
const CreateWorkspaceForm = ({ onSuccess }) => {
  const navigate = useNavigate();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    visibility: 'internal' // Default visibility
  });

  // Tags state
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');

  // Form submission state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  // Handle tag input
  const handleTagInputChange = (e) => {
    setTagInput(e.target.value);
  };

  // Add tag when Enter key is pressed
  const handleTagKeyDown = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      addTag();
    }
  };

  // Add a tag
  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags(prevTags => [...prevTags, tagInput.trim()]);
      setTagInput('');
    }
  };

  // Delete a tag
  const deleteTag = (tagToDelete) => {
    setTags(tags.filter(tag => tag !== tagToDelete));
  };

  // Form validation
  const isFormValid = () => {
    return formData.name.trim() !== '' && formData.description.trim() !== '';
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid()) return;

    try {
      setLoading(true);
      setError(null);

      const workspaceData = {
        ...formData,
        tags
      };

      // Call the service to create the workspace
      const createdWorkspace = await collaborationService.createWorkspace(workspaceData);
      
      // Handle success
      setSuccess(true);
      
      // Notify parent component if callback provided
      if (onSuccess) {
        onSuccess(createdWorkspace);
      }
      
      // Navigate to the new workspace after a brief delay
      setTimeout(() => {
        navigate(`/workspaces/${createdWorkspace.id}`);
      }, 1000);
    } catch (err) {
      setError(err.message || 'Failed to create workspace. Please try again.');
      console.error('Error creating workspace:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" component="h2" gutterBottom>
        Create New Workspace
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
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          name="name"
          label="Workspace Name"
          value={formData.name}
          onChange={handleChange}
          margin="normal"
          required
          fullWidth
          disabled={loading || success}
          error={formData.name === '' && formData.name !== undefined}
          helperText={formData.name === '' && formData.name !== undefined ? "Workspace name is required" : ""}
        />
        
        <TextField
          name="description"
          label="Description"
          value={formData.description}
          onChange={handleChange}
          margin="normal"
          required
          fullWidth
          multiline
          rows={3}
          disabled={loading || success}
          error={formData.description === '' && formData.description !== undefined}
          helperText={formData.description === '' && formData.description !== undefined ? "Description is required" : ""}
        />
        
        <FormControl component="fieldset" margin="normal" disabled={loading || success}>
          <FormLabel component="legend">Visibility</FormLabel>
          <RadioGroup
            name="visibility"
            value={formData.visibility}
            onChange={handleChange}
            sx={{ flexDirection: { xs: 'column', sm: 'row' } }}
          >
            <FormControlLabel value="private" control={<Radio />} label="Private" />
            <FormControlLabel value="internal" control={<Radio />} label="Internal" />
            <FormControlLabel value="public" control={<Radio />} label="Public" />
          </RadioGroup>
        </FormControl>
        
        <Box sx={{ mt: 3, mb: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Tags (Optional)
          </Typography>
          <TextField
            value={tagInput}
            onChange={handleTagInputChange}
            onKeyDown={handleTagKeyDown}
            placeholder="Add a tag and press Enter"
            fullWidth
            variant="outlined"
            size="small"
            disabled={loading || success}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton 
                    onClick={addTag}
                    disabled={!tagInput.trim() || loading || success}
                    edge="end"
                  >
                    <AddIcon />
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
        </Box>
        
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 3, mt: 1 }}>
          {tags.map(tag => (
            <Chip
              key={tag}
              label={tag}
              onDelete={() => deleteTag(tag)}
              disabled={loading || success}
              size="small"
            />
          ))}
          {tags.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No tags added yet
            </Typography>
          )}
        </Box>
        
        <Stack direction="row" spacing={2} justifyContent="flex-end" sx={{ mt: 3 }}>
          <Button
            type="button"
            variant="outlined"
            color="secondary"
            startIcon={<CancelIcon />}
            onClick={() => navigate('/workspaces')}
            disabled={loading || success}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            startIcon={loading ? <CircularProgress size={24} color="inherit" /> : <SaveIcon />}
            disabled={!isFormValid() || loading || success}
          >
            {loading ? 'Creating...' : 'Create Workspace'}
          </Button>
        </Stack>
      </Box>
    </Paper>
  );
};

export default CreateWorkspaceForm;