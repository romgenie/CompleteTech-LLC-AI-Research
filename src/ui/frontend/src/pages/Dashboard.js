import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Divider,
  Chip,
  Stack,
  CircularProgress,
  Alert
} from '@mui/material';
import { 
  Add as AddIcon,
  ChevronRight as ChevronRightIcon,
  Folder as FolderIcon,
  People as PeopleIcon,
  LibraryBooks as LibraryBooksIcon,
  AccountTree as AccountTreeIcon,
  GitHub as GitHubIcon,
  Science as ScienceIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import collaborationService from '../services/collaborationService';

/**
 * Dashboard component that provides access to main application features
 */
const Dashboard = () => {
  const [recentWorkspaces, setRecentWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch recent workspaces on component mount
  useEffect(() => {
    const fetchRecentWorkspaces = async () => {
      try {
        setLoading(true);
        setError(null);

        const workspaces = await collaborationService.getWorkspaces();
        setRecentWorkspaces(workspaces.slice(0, 3)); // Show only the 3 most recent
      } catch (err) {
        setError('Failed to load recent workspaces');
        console.error('Error fetching recent workspaces:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentWorkspaces();
  }, []);

  // Featured application modules
  const featuredModules = [
    {
      title: 'Research Understanding',
      description: 'Process research papers and extract key information',
      icon: <LibraryBooksIcon fontSize="large" color="primary" />,
      link: '/research/understanding'
    },
    {
      title: 'Knowledge Graph',
      description: 'Explore interconnected research concepts',
      icon: <AccountTreeIcon fontSize="large" color="primary" />,
      link: '/knowledge-graph'
    },
    {
      title: 'Research Implementation',
      description: 'Convert research concepts into actionable code',
      icon: <ScienceIcon fontSize="large" color="primary" />,
      link: '/research/implementation'
    }
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Research Integration Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to the AI Research Integration Platform. Access your collaborative workspaces, research tools, and knowledge resources.
        </Typography>
      </Box>

      {/* Recent Workspaces Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            Recent Workspaces
          </Typography>
          <Button 
            component={RouterLink}
            to="/workspaces"
            endIcon={<ChevronRightIcon />}
          >
            View All
          </Button>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {recentWorkspaces.map(workspace => (
              <Grid item xs={12} sm={6} md={4} key={workspace.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                      <FolderIcon color="primary" sx={{ mr: 1 }} />
                      <Box>
                        <Typography variant="h6" component="h3">
                          {workspace.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Last updated: {new Date(workspace.updated_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" sx={{ mb: 1 }} noWrap>
                      {workspace.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
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
                    </Box>
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
            
            {/* Create New Workspace Card */}
            <Grid item xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', py: 2 }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <IconButton 
                    component={RouterLink}
                    to="/workspaces/new"
                    size="large"
                    sx={{ 
                      mb: 2,
                      bgcolor: 'primary.light',
                      color: 'primary.contrastText',
                      '&:hover': {
                        bgcolor: 'primary.main',
                      }
                    }}
                  >
                    <AddIcon fontSize="large" />
                  </IconButton>
                  <Typography variant="h6" component="h3">
                    Create New Workspace
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Box>

      {/* Featured Modules Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
          Featured Modules
        </Typography>

        <Grid container spacing={3}>
          {featuredModules.map((module, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                    <Box sx={{ mb: 2 }}>
                      {module.icon}
                    </Box>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {module.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {module.description}
                    </Typography>
                  </Box>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center' }}>
                  <Button 
                    size="small" 
                    component={RouterLink} 
                    to={module.link}
                  >
                    Explore
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Quick Actions Section */}
      <Box>
        <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
          Quick Actions
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              component={RouterLink}
              to="/workspaces/new"
              variant="outlined"
              startIcon={<AddIcon />}
              fullWidth
              sx={{ justifyContent: 'flex-start', py: 1.5 }}
            >
              Create Workspace
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              component={RouterLink}
              to="/research/understanding/upload"
              variant="outlined"
              startIcon={<LibraryBooksIcon />}
              fullWidth
              sx={{ justifyContent: 'flex-start', py: 1.5 }}
            >
              Process Paper
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              component={RouterLink}
              to="/knowledge-graph/search"
              variant="outlined"
              startIcon={<AccountTreeIcon />}
              fullWidth
              sx={{ justifyContent: 'flex-start', py: 1.5 }}
            >
              Search Knowledge
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              component={RouterLink}
              to="/research/implementation/new"
              variant="outlined"
              startIcon={<ScienceIcon />}
              fullWidth
              sx={{ justifyContent: 'flex-start', py: 1.5 }}
            >
              Implementation Plan
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard;