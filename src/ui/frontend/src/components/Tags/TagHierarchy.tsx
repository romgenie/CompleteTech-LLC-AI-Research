import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Tooltip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Paper,
  Divider,
  Menu,
  MenuItem,
  alpha
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  Add,
  Delete,
  Edit,
  DragIndicator,
  Folder,
  FolderOpen,
  Label,
  ColorLens,
  Settings,
  MenuOpen,
  MoreVert
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Tag } from '../../types/research';
import { useTags, useTagHierarchy, useCreateTag, useUpdateTag, useDeleteTag, useMoveTag } from '../../services/tagsService';

interface TagNode extends Tag {
  children?: TagNode[];
  isOpen?: boolean;
}

interface TagHierarchyProps {
  onTagSelect?: (tag: Tag) => void;
  enableDragDrop?: boolean;
  enableEditing?: boolean;
  initialSelectedTagId?: string;
}

/**
 * Component for displaying and manipulating tag hierarchy
 */
const TagHierarchy: React.FC<TagHierarchyProps> = ({
  onTagSelect,
  enableDragDrop = true,
  enableEditing = true,
  initialSelectedTagId
}) => {
  const [selectedTagId, setSelectedTagId] = useState<string | null>(initialSelectedTagId || null);
  const [expandedTags, setExpandedTags] = useState<Set<string>>(new Set());
  const [hierarchicalTags, setHierarchicalTags] = useState<TagNode[]>([]);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [newTagParentId, setNewTagParentId] = useState<string | null>(null);
  const [addTagDialogOpen, setAddTagDialogOpen] = useState(false);
  const [editTagDialogOpen, setEditTagDialogOpen] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [newTagColor, setNewTagColor] = useState('#2196f3');
  const [newTagDescription, setNewTagDescription] = useState('');
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [contextMenuTag, setContextMenuTag] = useState<Tag | null>(null);

  // Get all tags
  const tagsQuery = useTags();
  // Get tag hierarchy
  const hierarchyQuery = useTagHierarchy();
  // Create tag mutation
  const createTagMutation = useCreateTag();
  // Update tag mutation
  const updateTagMutation = useUpdateTag();
  // Delete tag mutation
  const deleteTagMutation = useDeleteTag();
  // Move tag mutation
  const moveTagMutation = useMoveTag();

  // Build hierarchical structure from flat tags list
  useEffect(() => {
    // If we have the hierarchy data, use it
    if (hierarchyQuery.data && hierarchyQuery.data.length > 0) {
      const buildHierarchy = (rootTags: Tag[]): TagNode[] => {
        const allTags = tagsQuery.data || [];
        const result: TagNode[] = [];

        // Process each root tag
        for (const rootTag of rootTags) {
          const node: TagNode = {
            ...rootTag,
            isOpen: expandedTags.has(rootTag.id),
            children: []
          };

          // If this tag has children, process them
          if (rootTag.children && rootTag.children.length > 0) {
            // Find child tags
            const childTags = rootTag.children
              .map(childId => allTags.find(tag => tag.id === childId))
              .filter((tag): tag is Tag => !!tag);

            node.children = buildHierarchy(childTags);
          }

          result.push(node);
        }

        return result;
      };

      // Start with root tags (those with no parent)
      const rootTags = hierarchyQuery.data.filter(tag => !tag.parentId);
      setHierarchicalTags(buildHierarchy(rootTags));
    } 
    // Otherwise, build from flat list
    else if (tagsQuery.data) {
      const buildHierarchyFromFlatList = () => {
        const tagMap = new Map<string, TagNode>();
        const rootTags: TagNode[] = [];

        // First pass: create all tag nodes
        tagsQuery.data?.forEach(tag => {
          tagMap.set(tag.id, {
            ...tag,
            isOpen: expandedTags.has(tag.id),
            children: []
          });
        });

        // Second pass: build the hierarchy
        tagsQuery.data?.forEach(tag => {
          const node = tagMap.get(tag.id);
          if (node) {
            if (!tag.parentId) {
              // Root tag
              rootTags.push(node);
            } else {
              // Child tag
              const parentNode = tagMap.get(tag.parentId);
              if (parentNode) {
                if (!parentNode.children) {
                  parentNode.children = [];
                }
                parentNode.children.push(node);
              } else {
                // If parent doesn't exist, treat as root
                rootTags.push(node);
              }
            }
          }
        });

        return rootTags;
      };

      setHierarchicalTags(buildHierarchyFromFlatList());
    }
  }, [tagsQuery.data, hierarchyQuery.data, expandedTags]);

  // Toggle expand/collapse for a tag
  const handleToggleExpand = (tagId: string) => {
    setExpandedTags(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tagId)) {
        newSet.delete(tagId);
      } else {
        newSet.add(tagId);
      }
      return newSet;
    });
  };

  // Select a tag
  const handleSelectTag = (tag: Tag) => {
    setSelectedTagId(tag.id);
    if (onTagSelect) {
      onTagSelect(tag);
    }
  };

  // Open add tag dialog
  const handleAddTag = (parentId: string | null = null) => {
    setNewTagParentId(parentId);
    setNewTagName('');
    setNewTagColor('#2196f3');
    setNewTagDescription('');
    setAddTagDialogOpen(true);
    setMenuAnchorEl(null);
  };

  // Open edit tag dialog
  const handleEditTag = (tag: Tag) => {
    setEditingTag(tag);
    setNewTagName(tag.name);
    setNewTagColor(tag.color || '#2196f3');
    setNewTagDescription(tag.description || '');
    setEditTagDialogOpen(true);
    setMenuAnchorEl(null);
  };

  // Submit new tag
  const handleSubmitNewTag = async () => {
    if (!newTagName.trim()) return;

    try {
      await createTagMutation.mutateAsync({
        name: newTagName.trim(),
        color: newTagColor,
        description: newTagDescription.trim(),
        parentId: newTagParentId
      });
      
      setAddTagDialogOpen(false);
    } catch (error) {
      console.error('Error creating tag:', error);
    }
  };

  // Submit edited tag
  const handleSubmitEditTag = async () => {
    if (!editingTag || !newTagName.trim()) return;

    try {
      await updateTagMutation.mutateAsync({
        id: editingTag.id,
        data: {
          name: newTagName.trim(),
          color: newTagColor,
          description: newTagDescription.trim()
        }
      });
      
      setEditTagDialogOpen(false);
    } catch (error) {
      console.error('Error updating tag:', error);
    }
  };

  // Delete a tag
  const handleDeleteTag = async (tag: Tag) => {
    // Confirm with user if tag has children
    if (tag.children && tag.children.length > 0) {
      const confirmed = window.confirm(
        `This tag has ${tag.children.length} child tags. Deleting it will also delete all its children. Are you sure?`
      );
      if (!confirmed) return;
    }

    try {
      await deleteTagMutation.mutateAsync(tag.id);
      setMenuAnchorEl(null);

      // If the deleted tag was selected, clear selection
      if (selectedTagId === tag.id) {
        setSelectedTagId(null);
      }
    } catch (error) {
      console.error('Error deleting tag:', error);
    }
  };

  // Handle drag and drop
  const handleDragEnd = async (result: any) => {
    const { draggableId, destination, source } = result;

    // If dropped outside a droppable area or in the same place
    if (!destination || 
        (destination.droppableId === source.droppableId && 
         destination.index === source.index)) {
      return;
    }

    const sourceParentId = source.droppableId === 'root' ? null : source.droppableId;
    const destinationParentId = destination.droppableId === 'root' ? null : destination.droppableId;

    // If the tag was moved to a different parent
    if (sourceParentId !== destinationParentId) {
      try {
        await moveTagMutation.mutateAsync({
          tagId: draggableId,
          newParentId: destinationParentId
        });
      } catch (error) {
        console.error('Error moving tag:', error);
      }
    }
  };

  // Open context menu
  const handleOpenMenu = (event: React.MouseEvent<HTMLElement>, tag: Tag) => {
    setMenuAnchorEl(event.currentTarget);
    setContextMenuTag(tag);
  };

  // Close context menu
  const handleCloseMenu = () => {
    setMenuAnchorEl(null);
    setContextMenuTag(null);
  };

  // Render a tag node with its children
  const renderTagNode = (node: TagNode, level: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = Boolean(node.isOpen);
    
    const tagItem = (
      <ListItem
        button
        sx={{
          pl: 2 * level,
          py: 0.75,
          borderLeft: selectedTagId === node.id ? `4px solid ${node.color || '#2196f3'}` : 'none',
          bgcolor: selectedTagId === node.id 
            ? (theme) => alpha(theme.palette.primary.main, 0.08)
            : 'transparent',
          '&:hover': {
            bgcolor: (theme) => alpha(theme.palette.primary.main, 0.04)
          }
        }}
        onClick={() => handleSelectTag(node)}
      >
        <ListItemIcon sx={{ minWidth: 36 }}>
          {hasChildren ? (
            isExpanded ? <FolderOpen fontSize="small" sx={{ color: node.color }} /> : <Folder fontSize="small" sx={{ color: node.color }} />
          ) : (
            <Label fontSize="small" sx={{ color: node.color }} />
          )}
        </ListItemIcon>
        
        <ListItemText 
          primary={
            <Typography variant="body1" noWrap>
              {node.name}
            </Typography>
          }
          secondary={
            node.count !== undefined && (
              <Typography variant="caption" color="text.secondary">
                {node.count} items
              </Typography>
            )
          }
        />
        
        {hasChildren && (
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              handleToggleExpand(node.id);
            }}
          >
            {isExpanded ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
          </IconButton>
        )}
        
        {enableEditing && (
          <ListItemSecondaryAction>
            <IconButton
              size="small"
              edge="end"
              onClick={(e) => handleOpenMenu(e, node)}
            >
              <MoreVert fontSize="small" />
            </IconButton>
          </ListItemSecondaryAction>
        )}
      </ListItem>
    );

    return (
      <React.Fragment key={node.id}>
        {enableDragDrop ? (
          <Draggable draggableId={node.id} index={level}>
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
              >
                {tagItem}
              </div>
            )}
          </Draggable>
        ) : (
          tagItem
        )}

        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto">
            <List component="div" disablePadding>
              {enableDragDrop ? (
                <Droppable droppableId={node.id}>
                  {(provided) => (
                    <div ref={provided.innerRef} {...provided.droppableProps}>
                      {node.children?.map((child) => renderTagNode(child, level + 1))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              ) : (
                node.children?.map((child) => renderTagNode(child, level + 1))
              )}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  // Is loading
  const isLoading = tagsQuery.isLoading || hierarchyQuery.isLoading;

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
      >
        <Typography variant="h6">Tag Hierarchy</Typography>
        {enableEditing && (
          <Button
            startIcon={<Add />}
            size="small"
            onClick={() => handleAddTag(null)}
          >
            Add Root Tag
          </Button>
        )}
      </Box>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : hierarchicalTags.length === 0 ? (
        <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No tags available. Create your first tag to get started.
          </Typography>
          {enableEditing && (
            <Button
              variant="outlined"
              startIcon={<Add />}
              sx={{ mt: 2 }}
              onClick={() => handleAddTag(null)}
            >
              Create Tag
            </Button>
          )}
        </Paper>
      ) : (
        <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="root">
              {(provided) => (
                <List
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  component="nav"
                  dense
                >
                  {hierarchicalTags.map((node) => renderTagNode(node))}
                  {provided.placeholder}
                </List>
              )}
            </Droppable>
          </DragDropContext>
        </Paper>
      )}

      {/* Tag context menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleCloseMenu}
      >
        <MenuItem onClick={() => contextMenuTag && handleEditTag(contextMenuTag)}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>
        <MenuItem onClick={() => contextMenuTag && handleAddTag(contextMenuTag.id)}>
          <ListItemIcon>
            <Add fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Add Child" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => contextMenuTag && handleDeleteTag(contextMenuTag)}>
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText primary="Delete" />
        </MenuItem>
      </Menu>

      {/* Add tag dialog */}
      <Dialog
        open={addTagDialogOpen}
        onClose={() => setAddTagDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {newTagParentId ? 'Add Child Tag' : 'Add Root Tag'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Tag Name"
            fullWidth
            variant="outlined"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Color"
            type="color"
            fullWidth
            variant="outlined"
            value={newTagColor}
            onChange={(e) => setNewTagColor(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: (
                <Box
                  sx={{
                    width: 24,
                    height: 24,
                    borderRadius: '50%',
                    bgcolor: newTagColor,
                    mr: 1
                  }}
                />
              )
            }}
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newTagDescription}
            onChange={(e) => setNewTagDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddTagDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSubmitNewTag}
            color="primary"
            variant="contained"
            disabled={!newTagName.trim() || createTagMutation.isLoading}
          >
            {createTagMutation.isLoading ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit tag dialog */}
      <Dialog
        open={editTagDialogOpen}
        onClose={() => setEditTagDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Tag</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Tag Name"
            fullWidth
            variant="outlined"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Color"
            type="color"
            fullWidth
            variant="outlined"
            value={newTagColor}
            onChange={(e) => setNewTagColor(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: (
                <Box
                  sx={{
                    width: 24,
                    height: 24,
                    borderRadius: '50%',
                    bgcolor: newTagColor,
                    mr: 1
                  }}
                />
              )
            }}
          />
          <TextField
            margin="dense"
            label="Description (optional)"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newTagDescription}
            onChange={(e) => setNewTagDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditTagDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSubmitEditTag}
            color="primary"
            variant="contained"
            disabled={!newTagName.trim() || updateTagMutation.isLoading}
          >
            {updateTagMutation.isLoading ? <CircularProgress size={24} /> : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TagHierarchy;