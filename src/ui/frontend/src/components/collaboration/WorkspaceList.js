import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  Stack,
  TextField,
  InputAdornment,
  MenuItem,
  Menu
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  Folder as FolderIcon,
  People as PeopleIcon,
  AccountTree as AccountTreeIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import collaborationService from '../../services/collaborationService';

/**
 * Component for displaying and managing workspaces
 */
const WorkspaceList = () => {
  // State
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchor, setFilterAnchor] = useState(null);
  const [sortAnchor, setSortAnchor] = useState(null);
  const [filter, setFilter] = useState('all'); // all, private, internal, public
  const [sortBy, setSortBy] = useState('updated'); // updated, name, created

  // Load workspaces on component mount
  useEffect(() => {
    fetchWorkspaces();
  }, []);

  // Fetch workspaces from API
  const fetchWorkspaces = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await collaborationService.getWorkspaces();
      setWorkspaces(data);
    } catch (err) {
      setError('Failed to load workspaces. Please try again.');
      console.error('Error fetching workspaces:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter handlers
  const handleFilterOpen = (event) => {
    setFilterAnchor(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchor(null);
  };

  const handleFilterSelect = (value) => {
    setFilter(value);
    handleFilterClose();
  };

  // Sort handlers
  const handleSortOpen = (event) => {
    setSortAnchor(event.currentTarget);
  };

  const handleSortClose = () => {
    setSortAnchor(null);
  };

  const handleSortSelect = (value) => {
    setSortBy(value);
    handleSortClose();
  };

  // Filter workspaces based on search query and visibility filter
  const filteredWorkspaces = workspaces
    .filter(workspace => {
      const matchesSearch = workspace.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        workspace.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filter === 'all' || workspace.visibility === filter;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'created':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'updated':
        default:
          return new Date(b.updated_at) - new Date(a.updated_at);
      }
    });

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Workspaces
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your research workspaces and collaborate with team members
        </Typography>
      </Box>

      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Toolbar */}
      <Stack 
        direction={{ xs: 'column', sm: 'row' }} 
        spacing={2} 
        sx={{ mb: 3 }}
        alignItems="center"
        justifyContent="space-between"
      >
        <TextField
          placeholder="Search workspaces..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ flex: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        
        <Box>
          <Button
            onClick={handleFilterOpen}
            startIcon={<FilterIcon />}
            sx={{ mr: 1 }}
          >
            {filter === 'all' ? 'All' : filter.charAt(0).toUpperCase() + filter.slice(1)}
          </Button>
          <Menu
            anchorEl={filterAnchor}
            open={Boolean(filterAnchor)}
            onClose={handleFilterClose}
          >
            <MenuItem onClick={() => handleFilterSelect('all')}>All</MenuItem>
            <MenuItem onClick={() => handleFilterSelect('private')}>Private</MenuItem>
            <MenuItem onClick={() => handleFilterSelect('internal')}>Internal</MenuItem>
            <MenuItem onClick={() => handleFilterSelect('public')}>Public</MenuItem>
          </Menu>

          <Button
            onClick={handleSortOpen}
            startIcon={<SortIcon />}
            sx={{ mr: 1 }}
          >
            Sort by: {sortBy.charAt(0).toUpperCase() + sortBy.slice(1)}
          </Button>
          <Menu
            anchorEl={sortAnchor}
            open={Boolean(sortAnchor)}
            onClose={handleSortClose}
          >
            <MenuItem onClick={() => handleSortSelect('updated')}>Last Updated</MenuItem>
            <MenuItem onClick={() => handleSortSelect('created')}>Created Date</MenuItem>
            <MenuItem onClick={() => handleSortSelect('name')}>Name</MenuItem>
          </Menu>

          <Button
            component={RouterLink}
            to="/workspaces/new"
            variant="contained"
            startIcon={<AddIcon />}
          >
            Create Workspace
          </Button>
        </Box>
      </Stack>

      {/* Workspace grid */}
      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredWorkspaces.map(workspace => (
            <Grid item xs={12} sm={6} md={4} key={workspace.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                    <FolderIcon color="primary" sx={{ mr: 1 }} />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" component="h3">
                        {workspace.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Last updated: {new Date(workspace.updated_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <IconButton size="small">
                      <MoreVertIcon />
                    </IconButton>
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 2 }} noWrap>
                    {workspace.description}
                  </Typography>
                  
                  <Stack direction="row" spacing={1}>
                    <Chip 
                      icon={<PeopleIcon />} 
                      label={`${workspace.members_count} members`}
                      size="small"
                      variant="outlined"
                    />
                    <Chip 
                      icon={<AccountTreeIcon />}
                      label={`${workspace.projects_count} projects`}
                      size="small"
                      variant="outlined"
                    />
                  </Stack>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    component={RouterLink}
                    to={`/workspaces/${workspace.id}`}
                  >
                    Open
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}

          {/* Create workspace card */}
          <Grid item xs={12} sm={6} md={4}>
            <Card 
              component={RouterLink} 
              to="/workspaces/new"
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                p: 3,
                textDecoration: 'none',
                color: 'inherit',
                bgcolor: 'background.default',
                '&:hover': {
                  bgcolor: 'action.hover',
                }
              }}
            >
              <IconButton 
                sx={{ 
                  mb: 2,
                  bgcolor: 'primary.light',
                  color: 'primary.contrastText',
                  '&:hover': {
                    bgcolor: 'primary.main',
                  }
                }}
              >
                <AddIcon />
              </IconButton>
              <Typography variant="h6" component="h3" align="center">
                Create New Workspace
              </Typography>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default WorkspaceList;