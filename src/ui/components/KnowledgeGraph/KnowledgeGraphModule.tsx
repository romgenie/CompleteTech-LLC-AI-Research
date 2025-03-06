/**
 * Knowledge Graph Module
 * Main component that ties together all Knowledge Graph functionality
 */
import React, { useState, useCallback, useEffect } from 'react';
import { 
  Box, 
  Tabs, 
  Tab, 
  Paper, 
  Typography, 
  CircularProgress, 
  Alert,
  Button,
  Snackbar
} from '@mui/material';
import { Entity, EntityFilter, Relationship, GraphData, GraphVisualizationOptions, EntityType } from './types/knowledgeGraph.types';
import { ModuleDisplayMode, BaseModuleProps } from '../_templates/BaseModule/types/base.types';
import { useKnowledgeGraph } from './hooks/useKnowledgeGraph';
import { EntityList } from './components/EntityList';
import { EntityCard } from './components/EntityCard';
import { EntityDetail } from './components/EntityDetail';
import { EntityForm } from './components/EntityForm';
import { GraphVisualization } from './components/GraphVisualization';
import { PathFinder } from './components/PathFinder';
import { GraphStats } from './components/GraphStats';

interface KnowledgeGraphModuleProps extends BaseModuleProps<Entity, EntityFilter> {
  graphOptions?: GraphVisualizationOptions;
  showGraphTools?: boolean;
  enablePathfinding?: boolean;
  enableStats?: boolean;
}

export const KnowledgeGraphModule: React.FC<KnowledgeGraphModuleProps> = ({
  mode = 'list',
  initialFilter = {},
  onItemSelect,
  onItemCreate,
  onItemUpdate,
  onItemDelete,
  readOnly = false,
  height = 600,
  width = '100%',
  showActions = true,
  showFilters = true,
  customActions,
  graphOptions,
  showGraphTools = true,
  enablePathfinding = true,
  enableStats = true,
  // Component overrides
  filterComponent,
  listComponent,
  cardComponent,
  detailComponent,
  formComponent,
  emptyComponent,
  errorComponent,
  loadingComponent
}) => {
  // State
  const [displayMode, setDisplayMode] = useState<ModuleDisplayMode>(mode);
  const [filter, setFilter] = useState<EntityFilter>(initialFilter);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [notification, setNotification] = useState<{message: string, severity: 'success' | 'error' | 'info' | 'warning'} | null>(null);

  // Initialize knowledge graph hook
  const {
    entities,
    relationships,
    graphData,
    graphStatistics,
    loading,
    error,
    actions
  } = useKnowledgeGraph(filter);

  // Update filter
  const handleFilterChange = useCallback((newFilter: EntityFilter) => {
    setFilter(newFilter);
  }, []);

  // Handle entity selection
  const handleSelectEntity = useCallback((entity: Entity) => {
    setSelectedEntity(entity);
    setDisplayMode('detail');
    
    if (onItemSelect) {
      onItemSelect(entity);
    }
  }, [onItemSelect]);

  // Handle entity creation
  const handleCreateEntity = useCallback(async (entityData: Omit<Entity, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      const newEntity = await actions.createEntity(entityData);
      setNotification({
        message: `Entity "${newEntity.name}" created successfully`,
        severity: 'success'
      });
      
      if (onItemCreate) {
        onItemCreate(newEntity);
      }
      
      setDisplayMode('list');
      return newEntity;
    } catch (error) {
      setNotification({
        message: `Failed to create entity: ${error instanceof Error ? error.message : 'Unknown error'}`,
        severity: 'error'
      });
      throw error;
    }
  }, [actions, onItemCreate]);

  // Handle entity update
  const handleUpdateEntity = useCallback(async (id: string, entityData: Partial<Entity>) => {
    try {
      const updatedEntity = await actions.updateEntity(id, entityData);
      setNotification({
        message: `Entity "${updatedEntity.name}" updated successfully`,
        severity: 'success'
      });
      
      if (onItemUpdate) {
        onItemUpdate(updatedEntity);
      }
      
      if (selectedEntity?.id === id) {
        setSelectedEntity(updatedEntity);
      }
      
      return updatedEntity;
    } catch (error) {
      setNotification({
        message: `Failed to update entity: ${error instanceof Error ? error.message : 'Unknown error'}`,
        severity: 'error'
      });
      throw error;
    }
  }, [actions, onItemUpdate, selectedEntity]);

  // Handle entity deletion
  const handleDeleteEntity = useCallback(async (id: string) => {
    try {
      await actions.deleteEntity(id);
      setNotification({
        message: 'Entity deleted successfully',
        severity: 'success'
      });
      
      if (onItemDelete) {
        onItemDelete(id);
      }
      
      if (selectedEntity?.id === id) {
        setSelectedEntity(null);
        setDisplayMode('list');
      }
    } catch (error) {
      setNotification({
        message: `Failed to delete entity: ${error instanceof Error ? error.message : 'Unknown error'}`,
        severity: 'error'
      });
    }
  }, [actions, onItemDelete, selectedEntity]);

  // Handle view graph action
  const handleViewGraph = useCallback((entityId: string) => {
    actions.fetchGraphFromEntity(entityId);
    setActiveTab(1); // Switch to graph tab
  }, [actions]);

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification(null);
  };

  // Set display mode based on prop changes
  useEffect(() => {
    setDisplayMode(mode);
  }, [mode]);

  // Update filter when initialFilter changes
  useEffect(() => {
    setFilter(initialFilter);
  }, [initialFilter]);

  // Render different components based on display mode
  const renderContent = () => {
    if (error) {
      return (
        <Box p={2}>
          <Alert severity="error">{error.message}</Alert>
        </Box>
      );
    }

    if (loading && !entities.length) {
      return (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100%',
            width: '100%',
          }}
        >
          <CircularProgress />
        </Box>
      );
    }

    switch (displayMode) {
      case 'list':
        return (
          <Box>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Entities" />
              <Tab label="Graph" />
              {enableStats && <Tab label="Statistics" />}
            </Tabs>
            <Box py={2}>
              {activeTab === 0 && (
                <EntityList
                  entities={entities}
                  loading={loading}
                  error={error}
                  filter={filter}
                  onFilterChange={handleFilterChange}
                  onSelectEntity={handleSelectEntity}
                  onEditEntity={readOnly ? undefined : (entity) => {
                    setSelectedEntity(entity);
                    setDisplayMode('form');
                  }}
                  onDeleteEntity={readOnly ? undefined : handleDeleteEntity}
                  onViewGraph={handleViewGraph}
                  readOnly={readOnly}
                />
              )}
              {activeTab === 1 && (
                <GraphVisualization
                  graphData={graphData || { entities, relationships }}
                  loading={loading}
                  error={error}
                  options={graphOptions}
                  onSelectEntity={handleSelectEntity}
                  readOnly={readOnly}
                />
              )}
              {activeTab === 2 && enableStats && (
                <GraphStats
                  statistics={graphStatistics}
                  loading={loading}
                  error={error}
                  onTypeClick={(type) => setFilter({ ...filter, type })}
                />
              )}
            </Box>
          </Box>
        );
      
      case 'detail':
        return (
          <EntityDetail
            entity={selectedEntity}
            loading={loading}
            error={error}
            onEdit={readOnly ? undefined : () => setDisplayMode('form')}
            onDelete={readOnly ? undefined : selectedEntity ? () => handleDeleteEntity(selectedEntity.id) : undefined}
            readOnly={readOnly}
            onBack={() => setDisplayMode('list')}
          />
        );
      
      case 'form':
        return (
          <EntityForm
            item={selectedEntity}
            onSubmit={async (data) => {
              if (selectedEntity) {
                await handleUpdateEntity(selectedEntity.id, data);
              } else {
                await handleCreateEntity(data as Omit<Entity, 'id' | 'createdAt' | 'updatedAt'>);
              }
              setDisplayMode(selectedEntity ? 'detail' : 'list');
            }}
            onCancel={() => setDisplayMode(selectedEntity ? 'detail' : 'list')}
            loading={loading}
            error={error}
          />
        );
      
      default:
        return <Typography>Invalid display mode</Typography>;
    }
  };

  return (
    <Box
      sx={{
        height,
        width,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {showActions && displayMode === 'list' && (
        <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="h6">Knowledge Graph</Typography>
          <Box>
            {!readOnly && (
              <Button 
                variant="contained" 
                color="primary" 
                onClick={() => {
                  setSelectedEntity(null);
                  setDisplayMode('form');
                }}
              >
                Add Entity
              </Button>
            )}
            {customActions}
          </Box>
        </Box>
      )}
      
      <Paper 
        variant="outlined" 
        sx={{ 
          flex: 1, 
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {renderContent()}
      </Paper>
      
      <Snackbar
        open={!!notification}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {notification && (
          <Alert onClose={handleCloseNotification} severity={notification.severity}>
            {notification.message}
          </Alert>
        )}
      </Snackbar>
    </Box>
  );
};