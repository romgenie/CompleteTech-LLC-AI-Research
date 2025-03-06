import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Chip, 
  Box, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction, 
  IconButton, 
  FormControlLabel, 
  Radio, 
  RadioGroup, 
  Divider,
  TextField,
  Autocomplete
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonIcon from '@mui/icons-material/Person';
import GroupIcon from '@mui/icons-material/Group';

import { Tag, TagVisibility, SharedWith } from '../../types/research';
import { User } from '../../types';
import { useShareTag } from '../../services/tagsService';

// Mock user and group data
const MOCK_USERS = [
  { id: '1', username: 'admin', full_name: 'Admin User' },
  { id: '2', username: 'researcher', full_name: 'Research User' },
  { id: '3', username: 'viewer', full_name: 'View Only User' },
  { id: '4', username: 'john.doe', full_name: 'John Doe' },
  { id: '5', username: 'jane.smith', full_name: 'Jane Smith' }
];

const MOCK_GROUPS = [
  { id: 'g1', name: 'Research Team' },
  { id: 'g2', name: 'Data Science' },
  { id: 'g3', name: 'ML Engineers' },
  { id: 'g4', name: 'Administrators' }
];

interface TagSharingDialogProps {
  open: boolean;
  onClose: () => void;
  tag: Tag;
  onTagUpdated?: (updatedTag: Tag) => void;
}

/**
 * Dialog for managing tag visibility and sharing settings
 */
const TagSharingDialog: React.FC<TagSharingDialogProps> = ({
  open,
  onClose,
  tag,
  onTagUpdated
}) => {
  const [visibility, setVisibility] = useState<TagVisibility>(tag.visibility || 'private');
  const [sharedWith, setSharedWith] = useState<SharedWith[]>(tag.sharedWith || []);
  const [selectedEntityType, setSelectedEntityType] = useState<'user' | 'group'>('user');
  const [selectedEntity, setSelectedEntity] = useState<any | null>(null);
  const [selectedPermission, setSelectedPermission] = useState<'view' | 'use' | 'edit' | 'admin'>('view');
  
  const shareMutation = useShareTag();

  useEffect(() => {
    if (tag) {
      setVisibility(tag.visibility || 'private');
      setSharedWith(tag.sharedWith || []);
    }
  }, [tag]);

  const handleClose = () => {
    onClose();
  };

  const handleVisibilityChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setVisibility(event.target.value as TagVisibility);
  };

  const handleEntityTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedEntityType(event.target.value as 'user' | 'group');
    setSelectedEntity(null);
  };

  const handlePermissionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedPermission(event.target.value as 'view' | 'use' | 'edit' | 'admin');
  };

  const handleAddEntity = () => {
    if (!selectedEntity) return;
    
    const entity: SharedWith = {
      id: selectedEntity.id,
      type: selectedEntityType,
      permission: selectedPermission
    };
    
    // Check if entity already exists
    const exists = sharedWith.some(item => 
      item.id === entity.id && item.type === entity.type
    );
    
    if (!exists) {
      setSharedWith([...sharedWith, entity]);
    }
    
    // Reset selection
    setSelectedEntity(null);
  };

  const handleRemoveEntity = (entityId: string, entityType: string) => {
    setSharedWith(sharedWith.filter(entity => 
      !(entity.id === entityId && entity.type === entityType)
    ));
  };

  const handleSave = async () => {
    try {
      // Only update if visibility is 'shared'
      const updatedTagData = {
        tagId: tag.id,
        sharedWith: visibility === 'shared' ? sharedWith : []
      };
      
      const result = await shareMutation.mutateAsync(updatedTagData);
      
      if (onTagUpdated) {
        onTagUpdated({
          ...tag,
          visibility,
          sharedWith: visibility === 'shared' ? sharedWith : []
        });
      }
      
      onClose();
    } catch (error) {
      console.error('Failed to update tag sharing settings:', error);
    }
  };

  const getEntityName = (entity: SharedWith) => {
    if (entity.type === 'user') {
      const user = MOCK_USERS.find(u => u.id === entity.id);
      return user ? user.full_name : entity.id;
    } else {
      const group = MOCK_GROUPS.find(g => g.id === entity.id);
      return group ? group.name : entity.id;
    }
  };

  const getPermissionLabel = (permission: string) => {
    switch (permission) {
      case 'view': return 'View Only';
      case 'use': return 'Use Tag';
      case 'edit': return 'Edit Tag';
      case 'admin': return 'Full Control';
      default: return permission;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Tag Sharing Settings</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Tag Visibility
          </Typography>
          <RadioGroup value={visibility} onChange={handleVisibilityChange}>
            <FormControlLabel 
              value="private" 
              control={<Radio />} 
              label="Private (only you can see and use this tag)" 
            />
            <FormControlLabel 
              value="shared" 
              control={<Radio />} 
              label="Shared (specific users and groups)" 
            />
            <FormControlLabel 
              value="public" 
              control={<Radio />} 
              label="Public (visible to all users)" 
            />
          </RadioGroup>
        </Box>
        
        {visibility === 'shared' && (
          <>
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle1" gutterBottom>
              Shared With
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <RadioGroup 
                row 
                value={selectedEntityType} 
                onChange={handleEntityTypeChange}
              >
                <FormControlLabel 
                  value="user" 
                  control={<Radio />} 
                  label="Users" 
                />
                <FormControlLabel 
                  value="group" 
                  control={<Radio />} 
                  label="Groups/Teams" 
                />
              </RadioGroup>
            </Box>
            
            <Box sx={{ mb: 2, display: 'flex' }}>
              <Autocomplete
                value={selectedEntity}
                onChange={(event, newValue) => {
                  setSelectedEntity(newValue);
                }}
                options={selectedEntityType === 'user' ? MOCK_USERS : MOCK_GROUPS}
                getOptionLabel={(option) => 
                  selectedEntityType === 'user' 
                    ? `${option.full_name} (${option.username})` 
                    : option.name
                }
                sx={{ flexGrow: 1, mr: 2 }}
                renderInput={(params) => (
                  <TextField 
                    {...params} 
                    label={selectedEntityType === 'user' ? "Select User" : "Select Group"} 
                    variant="outlined"
                    size="small"
                  />
                )}
              />
              
              <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Permission</InputLabel>
                <Select
                  value={selectedPermission}
                  onChange={(e) => setSelectedPermission(e.target.value as any)}
                  label="Permission"
                >
                  <MenuItem value="view">View Only</MenuItem>
                  <MenuItem value="use">Use Tag</MenuItem>
                  <MenuItem value="edit">Edit Tag</MenuItem>
                  <MenuItem value="admin">Full Control</MenuItem>
                </Select>
              </FormControl>
              
              <Button 
                variant="contained" 
                onClick={handleAddEntity} 
                disabled={!selectedEntity}
                sx={{ ml: 1 }}
              >
                Add
              </Button>
            </Box>
            
            <List dense>
              {sharedWith.map((entity, index) => (
                <ListItem key={`${entity.type}-${entity.id}`}>
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {entity.type === 'user' ? <PersonIcon fontSize="small" sx={{ mr: 1 }} /> : <GroupIcon fontSize="small" sx={{ mr: 1 }} />}
                        {getEntityName(entity)}
                      </Box>
                    } 
                    secondary={getPermissionLabel(entity.permission)} 
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" onClick={() => handleRemoveEntity(entity.id, entity.type)}>
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
              {sharedWith.length === 0 && (
                <ListItem>
                  <ListItemText primary="No entities added yet" />
                </ListItem>
              )}
            </List>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSave} color="primary" variant="contained">
          Save Settings
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TagSharingDialog;