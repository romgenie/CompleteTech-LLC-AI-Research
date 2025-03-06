/**
 * Knowledge Graph path finder component (stub implementation)
 */
import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  Divider, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Chip,
  Grid,
  Alert,
  CircularProgress,
  IconButton
} from '@mui/material';
import { Search, ExpandMore, ExpandLess } from '@mui/icons-material';
import { Entity, Path, PathQuery, RelationshipType } from '../types/knowledgeGraph.types';

interface PathFinderProps {
  onFindPaths: (query: PathQuery) => Promise<Path[]>;
  entities: Entity[];
  loading: boolean;
  error: Error | null;
  onSelectEntity?: (entity: Entity) => void;
}

export const PathFinder: React.FC<PathFinderProps> = ({
  onFindPaths,
  entities,
  loading,
  error,
  onSelectEntity
}) => {
  const [sourceId, setSourceId] = useState<string>('');
  const [targetId, setTargetId] = useState<string>('');
  const [maxDepth, setMaxDepth] = useState<number>(3);
  const [algorithm, setAlgorithm] = useState<'shortestPath' | 'allPaths' | 'weightedPath'>('shortestPath');
  const [relationshipTypes, setRelationshipTypes] = useState<RelationshipType[]>([]);
  const [bidirectional, setBidirectional] = useState<boolean>(true);
  const [paths, setPaths] = useState<Path[]>([]);
  const [expandedPaths, setExpandedPaths] = useState<Record<number, boolean>>({});
  const [searching, setSearching] = useState<boolean>(false);
  const [searchError, setSearchError] = useState<Error | null>(null);

  const handleSearch = async () => {
    if (!sourceId || !targetId) {
      return;
    }
    
    setSearching(true);
    setSearchError(null);
    
    try {
      const query: PathQuery = {
        sourceId,
        targetId,
        maxDepth,
        relationshipTypes: relationshipTypes.length > 0 ? relationshipTypes : undefined,
        bidirectional,
        algorithm
      };
      
      const results = await onFindPaths(query);
      setPaths(results);
      
      // Initialize all paths as collapsed
      const newExpandedPaths: Record<number, boolean> = {};
      results.forEach((_, index) => {
        newExpandedPaths[index] = false;
      });
      setExpandedPaths(newExpandedPaths);
    } catch (err) {
      setSearchError(err instanceof Error ? err : new Error('Failed to find paths'));
    } finally {
      setSearching(false);
    }
  };

  const togglePathExpansion = (pathIndex: number) => {
    setExpandedPaths(prev => ({
      ...prev,
      [pathIndex]: !prev[pathIndex]
    }));
  };

  const getEntityById = (id: string): Entity | undefined => {
    return entities.find(entity => entity.id === id);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">{error.message}</Alert>
      </Box>
    );
  }

  const relationshipTypeOptions: RelationshipType[] = [
    'CREATED_BY',
    'USES',
    'IMPLEMENTS',
    'TRAINED_ON',
    'EVALUATED_ON',
    'CITES',
    'OUTPERFORMS',
    'PART_OF',
    'RELATED_TO',
    'EXTENDS'
  ];

  return (
    <Box p={2}>
      <Typography variant="h5" component="h2" gutterBottom>
        Path Finder
      </Typography>
      
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="source-entity-label">Source Entity</InputLabel>
              <Select
                labelId="source-entity-label"
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value as string)}
                label="Source Entity"
              >
                <MenuItem value="">
                  <em>Select a source entity</em>
                </MenuItem>
                {entities.map(entity => (
                  <MenuItem key={entity.id} value={entity.id}>
                    {entity.name} ({entity.type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel id="target-entity-label">Target Entity</InputLabel>
              <Select
                labelId="target-entity-label"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value as string)}
                label="Target Entity"
              >
                <MenuItem value="">
                  <em>Select a target entity</em>
                </MenuItem>
                {entities.map(entity => (
                  <MenuItem key={entity.id} value={entity.id}>
                    {entity.name} ({entity.type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              label="Max Depth"
              type="number"
              value={maxDepth}
              onChange={(e) => setMaxDepth(Number(e.target.value))}
              inputProps={{ min: 1, max: 10 }}
              fullWidth
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="algorithm-label">Algorithm</InputLabel>
              <Select
                labelId="algorithm-label"
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value as any)}
                label="Algorithm"
              >
                <MenuItem value="shortestPath">Shortest Path</MenuItem>
                <MenuItem value="allPaths">All Paths</MenuItem>
                <MenuItem value="weightedPath">Weighted Path</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={6}>
            <FormControl fullWidth>
              <InputLabel id="relationship-types-label">Relationship Types</InputLabel>
              <Select
                labelId="relationship-types-label"
                multiple
                value={relationshipTypes}
                onChange={(e) => setRelationshipTypes(e.target.value as RelationshipType[])}
                label="Relationship Types"
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(selected as RelationshipType[]).map((value) => (
                      <Chip key={value} label={value} size="small" />
                    ))}
                  </Box>
                )}
              >
                {relationshipTypeOptions.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSearch}
                disabled={!sourceId || !targetId || searching}
                startIcon={<Search />}
              >
                Find Paths
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {searchError && (
        <Alert severity="error" sx={{ mb: 2 }}>{searchError.message}</Alert>
      )}
      
      {searching ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : paths.length > 0 ? (
        <Paper variant="outlined">
          <Typography variant="h6" sx={{ p: 2 }}>
            Found {paths.length} path{paths.length !== 1 ? 's' : ''}
          </Typography>
          <List>
            {paths.map((path, pathIndex) => (
              <React.Fragment key={pathIndex}>
                <ListItem
                  button
                  onClick={() => togglePathExpansion(pathIndex)}
                >
                  <ListItemText
                    primary={`Path ${pathIndex + 1} (Length: ${path.length}${path.score ? `, Score: ${path.score.toFixed(2)}` : ''})`}
                    secondary={`${getEntityById(path.entities[0]?.id)?.name} → ${getEntityById(path.entities[path.entities.length - 1]?.id)?.name}`}
                  />
                  <IconButton edge="end">
                    {expandedPaths[pathIndex] ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </ListItem>
                
                {expandedPaths[pathIndex] && (
                  <Box sx={{ px: 2, pb: 2 }}>
                    <Typography variant="subtitle2">Entities in path:</Typography>
                    <List dense>
                      {path.entities.map((entity, index) => (
                        <ListItem 
                          key={index}
                          button={!!onSelectEntity}
                          onClick={() => onSelectEntity && onSelectEntity(entity)}
                        >
                          <ListItemText 
                            primary={entity.name} 
                            secondary={entity.type} 
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </Paper>
      ) : (
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography color="text.secondary">
            No paths found. Try adjusting your search criteria.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};