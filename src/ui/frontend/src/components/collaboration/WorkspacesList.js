import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Button,
  Chip,
  Divider,
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { 
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Sort as SortIcon,
  GroupWork as GroupWorkIcon,
  Public as PublicIcon,
  Lock as LockIcon,
  Clear as ClearIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import collaborationService from '../../services/collaborationService';

/**
 * Component to display a list of workspaces with filtering and sorting options
 */
const WorkspacesList = ({ onCreateWorkspace }) => {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMenuAnchor, setFilterMenuAnchor] = useState(null);
  const [sortMenuAnchor, setSortMenuAnchor] = useState(null);
  const [filters, setFilters] = useState({
    visibility: {
      private: true,
      internal: true,
      public: true
    }
  });
  const [sortOption, setSortOption] = useState({
    field: 'updated_at',
    direction: 'desc'
  });

  // Fetch workspaces
  useEffect(() => {
    const fetchWorkspaces = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await collaborationService.listWorkspaces();
        setWorkspaces(data);
      } catch (err) {
        setError(err.message || 'Failed to load workspaces');
        console.error('Error fetching workspaces:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkspaces();
  }, []);

  // Filter workspaces based on search term and filters
  const filteredWorkspaces = workspaces.filter(workspace => {
    // Filter by search term
    const matchesSearch = 
      searchTerm === '' || 
      workspace.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
      (workspace.description && workspace.description.toLowerCase().includes(searchTerm.toLowerCase()));

    // Filter by visibility
    const matchesVisibility = filters.visibility[workspace.visibility];

    return matchesSearch && matchesVisibility;
  });

  // Sort workspaces
  const sortedWorkspaces = [...filteredWorkspaces].sort((a, b) => {
    const fieldA = a[sortOption.field];
    const fieldB = b[sortOption.field];

    // Special handling for dates
    if (sortOption.field === 'updated_at' || sortOption.field === 'created_at') {
      const dateA = new Date(fieldA);
      const dateB = new Date(fieldB);
      return sortOption.direction === 'asc' ? dateA - dateB : dateB - dateA;
    }

    // String comparison for other fields
    if (fieldA < fieldB) return sortOption.direction === 'asc' ? -1 : 1;
    if (fieldA > fieldB) return sortOption.direction === 'asc' ? 1 : -1;
    return 0;
  });

  // Handle search change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Handle clear search
  const handleClearSearch = () => {
    setSearchTerm('');
  };

  // Handle filter menu open
  const handleFilterMenuOpen = (event) => {
    setFilterMenuAnchor(event.currentTarget);
  };

  // Handle filter menu close
  const handleFilterMenuClose = () => {
    setFilterMenuAnchor(null);
  };

  // Handle sort menu open
  const handleSortMenuOpen = (event) => {
    setSortMenuAnchor(event.currentTarget);
  };

  // Handle sort menu close
  const handleSortMenuClose = () => {
    setSortMenuAnchor(null);
  };

  // Handle toggling visibility filter
  const handleToggleVisibilityFilter = (visibility) => {
    setFilters(prev => ({
      ...prev,
      visibility: {
        ...prev.visibility,
        [visibility]: !prev.visibility[visibility]
      }
    }));
  };

  // Handle setting sort option
  const handleSetSortOption = (field, direction) => {
    setSortOption({ field, direction });
    handleSortMenuClose();
  };

  // Get icon for workspace visibility
  const getVisibilityIcon = (visibility) => {
    switch (visibility) {
      case 'public': return <PublicIcon fontSize="small" />;
      case 'internal': return <GroupWorkIcon fontSize="small" />;
      case 'private': return <LockIcon fontSize="small" />;
      default: return <LockIcon fontSize="small" />;
    }
  };

  // Get color for workspace visibility
  const getVisibilityColor = (visibility) => {
    switch (visibility) {
      case 'public': return 'success';
      case 'internal': return 'info';
      case 'private': return 'default';
      default: return 'default';
    }
  };

  // Render filter menu
  const renderFilterMenu = () => (
    <Menu
      id="filter-menu"
      anchorEl={filterMenuAnchor}
      open={Boolean(filterMenuAnchor)}
      onClose={handleFilterMenuClose}
      PaperProps={{
        style: {
          width: 250,
        },
      }}
    >
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="subtitle2" gutterBottom>
          Filter by Visibility
        </Typography>
        <Grid container spacing={1}>
          <Grid item>
            <Chip
              label="Private"
              icon={<LockIcon />}
              color={filters.visibility.private ? 'primary' : 'default'}
              variant={filters.visibility.private ? 'filled' : 'outlined'}
              onClick={() => handleToggleVisibilityFilter('private')}
              size="small"
            />
          </Grid>
          <Grid item>
            <Chip
              label="Internal"
              icon={<GroupWorkIcon />}
              color={filters.visibility.internal ? 'primary' : 'default'}
              variant={filters.visibility.internal ? 'filled' : 'outlined'}
              onClick={() => handleToggleVisibilityFilter('internal')}
              size="small"
            />
          </Grid>
          <Grid item>
            <Chip
              label="Public"
              icon={<PublicIcon />}
              color={filters.visibility.public ? 'primary' : 'default'}
              variant={filters.visibility.public ? 'filled' : 'outlined'}
              onClick={() => handleToggleVisibilityFilter('public')}
              size="small"
            />
          </Grid>
        </Grid>
      </Box>
      <Divider sx={{ my: 1 }} />
      <MenuItem onClick={handleFilterMenuClose}>
        <Button 
          fullWidth 
          variant="outlined" 
          onClick={() => {
            setFilters({
              visibility: {
                private: true,
                internal: true,
                public: true
              }
            });
          }}
        >
          Reset Filters
        </Button>
      </MenuItem>
    </Menu>
  );

  // Render sort menu
  const renderSortMenu = () => (
    <Menu
      id="sort-menu"
      anchorEl={sortMenuAnchor}
      open={Boolean(sortMenuAnchor)}
      onClose={handleSortMenuClose}
    >
      <MenuItem onClick={() => handleSetSortOption('updated_at', 'desc')}>
        <ListItemAvatar>
          {sortOption.field === 'updated_at' && sortOption.direction === 'desc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemAvatar>
        <ListItemText>Recently Updated</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('created_at', 'desc')}>
        <ListItemAvatar>
          {sortOption.field === 'created_at' && sortOption.direction === 'desc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemAvatar>
        <ListItemText>Recently Created</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('name', 'asc')}>
        <ListItemAvatar>
          {sortOption.field === 'name' && sortOption.direction === 'asc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemAvatar>
        <ListItemText>Name (A-Z)</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('name', 'desc')}>
        <ListItemAvatar>
          {sortOption.field === 'name' && sortOption.direction === 'desc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemAvatar>
        <ListItemText>Name (Z-A)</ListItemText>
      </MenuItem>
    </Menu>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
          Workspaces
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onCreateWorkspace}
        >
          New Workspace
        </Button>
      </Box>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Collaborate with team members on research projects and implementations.
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search workspaces"
              value={searchTerm}
              onChange={handleSearchChange}
              variant="outlined"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: searchTerm && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      aria-label="clear search"
                      onClick={handleClearSearch}
                      edge="end"
                    >
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }}
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
              <Tooltip title="Filter Workspaces">
                <IconButton onClick={handleFilterMenuOpen}>
                  <FilterListIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Sort Workspaces">
                <IconButton onClick={handleSortMenuOpen}>
                  <SortIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {renderFilterMenu()}
      {renderSortMenu()}
      
      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      ) : sortedWorkspaces.length > 0 ? (
        <Paper>
          <List sx={{ width: '100%' }}>
            {sortedWorkspaces.map((workspace, index) => (
              <React.Fragment key={workspace.id}>
                <ListItem 
                  button 
                  component={RouterLink} 
                  to={`/workspaces/${workspace.id}`}
                  alignItems="flex-start"
                >
                  <ListItemAvatar>
                    <Avatar>
                      {workspace.name.charAt(0).toUpperCase()}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary={workspace.name}
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        <Typography 
                          variant="body2" 
                          color="text.secondary" 
                          component="span"
                          sx={{ display: 'block', mb: 1 }}
                        >
                          {workspace.description || 'No description'}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          <Chip
                            icon={getVisibilityIcon(workspace.visibility)}
                            label={workspace.visibility}
                            size="small"
                            color={getVisibilityColor(workspace.visibility)}
                            variant="outlined"
                          />
                          
                          {workspace.tags && workspace.tags.slice(0, 3).map(tag => (
                            <Chip
                              key={tag}
                              label={tag}
                              size="small"
                            />
                          ))}
                          
                          {workspace.tags && workspace.tags.length > 3 && (
                            <Chip
                              label={`+${workspace.tags.length - 3} more`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 2 }}>
                    {new Date(workspace.updated_at).toLocaleDateString()}
                  </Typography>
                </ListItem>
                {index < sortedWorkspaces.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            No workspaces found.
          </Typography>
          <Button 
            variant="outlined" 
            startIcon={<AddIcon />}
            onClick={onCreateWorkspace}
            sx={{ mt: 1 }}
          >
            Create a Workspace
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default WorkspacesList;