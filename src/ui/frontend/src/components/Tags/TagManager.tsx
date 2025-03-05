import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import { TagInput, TagList } from '.';
import { useAllTags } from '../../services/researchService';

interface TagManagerProps {
  itemId: string;
  currentTags: string[];
  onAddTag: (itemId: string, tag: string) => void;
  onRemoveTag: (itemId: string, tag: string) => void;
  showButton?: boolean;
}

/**
 * Component for managing tags for a research item
 */
const TagManager: React.FC<TagManagerProps> = ({ 
  itemId, 
  currentTags, 
  onAddTag, 
  onRemoveTag,
  showButton = true
}) => {
  const [open, setOpen] = useState(false);
  const allTagsQuery = useAllTags();
  
  const handleAddTag = (tag: string) => {
    onAddTag(itemId, tag);
  };
  
  const handleRemoveTag = (tag: string) => {
    onRemoveTag(itemId, tag);
  };
  
  const handleOpen = () => {
    setOpen(true);
  };
  
  const handleClose = () => {
    setOpen(false);
  };
  
  // Dialog content for tag management
  const tagDialog = (
    <Dialog 
      open={open} 
      onClose={handleClose}
      aria-labelledby="tag-dialog-title"
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle id="tag-dialog-title">Manage Tags</DialogTitle>
      <DialogContent>
        <Box mb={2}>
          <Typography variant="subtitle2" gutterBottom>Add Tag</Typography>
          <TagInput 
            onAddTag={handleAddTag}
            existingTags={currentTags}
          />
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box mb={2}>
          <Typography variant="subtitle2" gutterBottom>Current Tags</Typography>
          <TagList 
            tags={currentTags}
            onDeleteTag={handleRemoveTag}
          />
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box>
          <Typography variant="subtitle2" gutterBottom>Suggested Tags</Typography>
          {allTagsQuery.isLoading ? (
            <Typography variant="body2">Loading tags...</Typography>
          ) : (
            <TagList 
              tags={allTagsQuery.tags.filter(tag => !currentTags.includes(tag))}
              onClick={handleAddTag}
            />
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
  
  // If we just want to show the tag list
  if (!showButton) {
    return (
      <Box mt={1}>
        <TagList 
          tags={currentTags}
          onDeleteTag={handleRemoveTag}
        />
      </Box>
    );
  }
  
  // Show button and inline tags
  return (
    <>
      <Box display="flex" alignItems="center" mt={1}>
        <Button 
          size="small" 
          variant="outlined" 
          onClick={handleOpen}
          sx={{ mr: 1 }}
        >
          Manage Tags
        </Button>
        <TagList 
          tags={currentTags}
          onDeleteTag={handleRemoveTag}
        />
      </Box>
      {tagDialog}
    </>
  );
};

export default TagManager;