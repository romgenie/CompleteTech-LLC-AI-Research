/**
 * Knowledge Graph entity list component
 */
import React, { useState } from 'react';
import { 
  Box, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction, 
  IconButton, 
  Typography, 
  Paper, 
  Divider, 
  Chip,
  Tooltip,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import { 
  Delete as DeleteIcon, 
  Edit as EditIcon, 
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  Link as LinkIcon,
  BarChart as BarChartIcon
} from '@mui/icons-material';
import { Entity, EntityType, EntityFilter } from '../types/knowledgeGraph.types';
import { getEntityColor } from '../utils/knowledgeGraphUtils';

interface EntityListProps {
  entities: Entity[];
  loading: boolean;
  error: Error | null;
  filter: EntityFilter;
  onFilterChange: (filter: EntityFilter) => void;
  onSelectEntity?: (entity: Entity) => void;
  onEditEntity?: (entity: Entity) => void;
  onDeleteEntity?: (id: string) => void;
  onViewGraph?: (entityId: string) => void;
  onFindPaths?: (entityId: string) => void;
  onViewStats?: (entityType?: EntityType) => void;
  readOnly?: boolean;
}

export const EntityList: React.FC<EntityListProps> = ({
  entities,
  loading,
  error,
  filter,
  onFilterChange,
  onSelectEntity,
  onEditEntity,
  onDeleteEntity,
  onViewGraph,
  onFindPaths,
  onViewStats,
  readOnly = false
}) => {
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>, entityId: string) => {
    setMenuAnchorEl(event.currentTarget);
    setSelectedEntityId(entityId);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedEntityId(null);
  };

  const handleSelectEntity = (entity: Entity) => {
    if (onSelectEntity) {
      onSelectEntity(entity);
    }
  };

  const handleEditEntity = () => {
    const entity = entities.find(e => e.id === selectedEntityId);
    if (entity && onEditEntity) {
      onEditEntity(entity);
    }
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setConfirmDeleteOpen(true);
    handleMenuClose();
  };

  const handleConfirmDelete = () => {
    if (selectedEntityId && onDeleteEntity) {
      onDeleteEntity(selectedEntityId);
    }
    setConfirmDeleteOpen(false);
  };

  const handleCancelDelete = () => {
    setConfirmDeleteOpen(false);
  };

  const handleViewGraph = () => {
    if (selectedEntityId && onViewGraph) {
      onViewGraph(selectedEntityId);
    }
    handleMenuClose();
  };

  const handleFindPaths = () => {
    if (selectedEntityId && onFindPaths) {
      onFindPaths(selectedEntityId);
    }
    handleMenuClose();
  };

  const handleViewStats = () => {
    if (onViewStats) {
      const entity = entities.find(e => e.id === selectedEntityId);
      onViewStats(entity?.type);
    }
    handleMenuClose();
  };

  const handleTypeFilterClick = (type: EntityType) => {
    onFilterChange({
      ...filter,
      type: filter.type === type ? undefined : type
    });
  };

  if (error) {
    return (
      <Box p={2}>
        <Typography color="error">Error: {error.message}</Typography>
      </Box>
    );
  }

  if (loading && entities.length === 0) {
    return (
      <Box p={2}>
        <Typography>Loading entities...</Typography>
      </Box>
    );
  }

  if (entities.length === 0) {
    return (
      <Box p={2}>
        <Typography>No entities found.</Typography>
      </Box>
    );
  }

  // Get unique entity types for filtering
  const entityTypes = Array.from(new Set(entities.map(e => e.type)));

  return (
    <Box>
      <Box p={1} sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {entityTypes.map(type => (
          <Chip
            key={type}
            label={type}
            color={filter.type === type ? 'primary' : 'default'}
            onClick={() => handleTypeFilterClick(type)}
            size="small"
            sx={{ 
              backgroundColor: filter.type !== type ? getEntityColor(type) : undefined,
              color: filter.type !== type ? 'white' : undefined,
              '&:hover': {
                opacity: 0.9
              }
            }}
          />
        ))}
        {filter.type && (
          <Chip
            label="Clear filter"
            size="small"
            onDelete={() => onFilterChange({ ...filter, type: undefined })}
          />
        )}
      </Box>
      <Divider />
      <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
        <List dense>
          {entities.map(entity => (
            <ListItem 
              key={entity.id} 
              divider
              onClick={() => handleSelectEntity(entity)}
              sx={{ 
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)'
                }
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">{entity.name}</Typography>
                    <Chip 
                      label={entity.type} 
                      size="small"
                      sx={{ 
                        backgroundColor: getEntityColor(entity.type),
                        color: 'white',
                        fontSize: '0.7rem'
                      }}
                    />
                    {entity.confidence !== undefined && (
                      <Chip 
                        label={`${Math.round(entity.confidence * 100)}%`} 
                        size="small"
                        color={entity.confidence > 0.8 ? 'success' : entity.confidence > 0.5 ? 'warning' : 'error'}
                        sx={{ fontSize: '0.7rem' }}
                      />
                    )}
                  </Box>
                }
                secondary={entity.description || 'No description'}
              />
              {!readOnly && (
                <ListItemSecondaryAction>
                  <IconButton edge="end" onClick={(e) => handleMenuOpen(e, entity.id)}>
                    <MoreVertIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              )}
            </ListItem>
          ))}
        </List>
      </Paper>
      
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleViewGraph}>
          <ListItemText primary="View Graph" />
          <VisibilityIcon fontSize="small" sx={{ ml: 1 }} />
        </MenuItem>
        <MenuItem onClick={handleFindPaths}>
          <ListItemText primary="Find Paths" />
          <LinkIcon fontSize="small" sx={{ ml: 1 }} />
        </MenuItem>
        <MenuItem onClick={handleViewStats}>
          <ListItemText primary="View Statistics" />
          <BarChartIcon fontSize="small" sx={{ ml: 1 }} />
        </MenuItem>
        <Divider />
        {onEditEntity && (
          <MenuItem onClick={handleEditEntity}>
            <ListItemText primary="Edit" />
            <EditIcon fontSize="small" sx={{ ml: 1 }} />
          </MenuItem>
        )}
        {onDeleteEntity && (
          <MenuItem onClick={handleDeleteClick}>
            <ListItemText primary="Delete" />
            <DeleteIcon fontSize="small" sx={{ ml: 1 }} color="error" />
          </MenuItem>
        )}
      </Menu>
      
      <Dialog 
        open={confirmDeleteOpen} 
        onClose={handleCancelDelete}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this entity? This action cannot be undone and will remove all relationships associated with this entity.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};