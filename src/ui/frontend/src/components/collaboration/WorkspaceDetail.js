import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondary,
  Avatar,
  Chip,
  Divider,
  TextField,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  People as PeopleIcon,
  Code as CodeIcon,
  History as HistoryIcon,
  FolderOpen as FolderIcon,
  Link as LinkIcon,
  Public as PublicIcon,
  Lock as LockIcon,
  GroupWork as GroupWorkIcon
} from '@mui/icons-material';
import { Link as RouterLink, useParams } from 'react-router-dom';
import collaborationService from '../../services/collaborationService';

// Panel for the content of each tab
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`workspace-tabpanel-${index}`}
      aria-labelledby={`workspace-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

/**
 * Component to display the details of a workspace, its projects, and members
 */
const WorkspaceDetail = () => {
  const { workspaceId } = useParams();
  const [workspace, setWorkspace] = useState(null);
  const [projects, setProjects] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  // Fetch workspace details
  useEffect(() => {
    const fetchWorkspaceDetails = async () => {
      if (!workspaceId) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // In a real app, we would use proper API calls
        // For now, we'll simulate with mock data
        const mockWorkspace = {
          id: workspaceId,
          name: "Research AI Integration",
          description: "Collaborative workspace for AI research integration projects",
          visibility: "internal",
          created_at: "2023-10-15T10:30:00Z",
          updated_at: "2023-11-10T14:22:00Z",
          tags: ["AI", "Research", "Integration"]
        };
        
        const mockProjects = [
          {
            id: "proj1",
            name: "Knowledge Graph System",
            description: "Development of the knowledge graph system for research integration",
            status: "in_progress",
            last_updated: "2023-11-09T08:45:00Z",
            contributors: 5
          },
          {
            id: "proj2",
            name: "Research Orchestrator",
            description: "Implementation of the research orchestration component",
            status: "completed",
            last_updated: "2023-11-02T15:20:00Z",
            contributors: 3
          },
          {
            id: "proj3",
            name: "Paper Processing Pipeline",
            description: "Development of the paper processing and information extraction pipeline",
            status: "planning",
            last_updated: "2023-11-10T09:15:00Z",
            contributors: 2
          }
        ];
        
        const mockMembers = [
          {
            id: "user1",
            name: "John Doe",
            role: "Admin",
            avatar: "J"
          },
          {
            id: "user2",
            name: "Jane Smith",
            role: "Contributor",
            avatar: "J"
          },
          {
            id: "user3",
            name: "Bob Johnson",
            role: "Viewer",
            avatar: "B"
          }
        ];
        
        setWorkspace(mockWorkspace);
        setProjects(mockProjects);
        setMembers(mockMembers);
      } catch (err) {
        setError(err.message || 'Failed to load workspace details');
        console.error('Error fetching workspace details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkspaceDetails();
  }, [workspaceId]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Get status chip color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'planning': return 'info';
      default: return 'default';
    }
  };

  // Get visibility icon
  const getVisibilityIcon = (visibility) => {
    switch (visibility) {
      case 'public': return <PublicIcon />;
      case 'internal': return <GroupWorkIcon />;
      case 'private': return <LockIcon />;
      default: return <LockIcon />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  if (!workspace) {
    return (
      <Alert severity="info" sx={{ mb: 3 }}>
        Workspace not found
      </Alert>
    );
  }

  return (
    <Box>
      {/* Workspace Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="h4" component="h1">
                {workspace.name}
              </Typography>
              <Chip 
                icon={getVisibilityIcon(workspace.visibility)}
                label={workspace.visibility}
                sx={{ ml: 2 }}
                variant="outlined"
              />
            </Box>
            <Typography variant="body1" color="text.secondary" paragraph>
              {workspace.description}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
              {workspace.tags && workspace.tags.map(tag => (
                <Chip key={tag} label={tag} size="small" />
              ))}
            </Box>
            <Typography variant="body2" color="text.secondary">
              Last updated: {new Date(workspace.updated_at).toLocaleDateString()}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
            <Box>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                sx={{ mr: 1 }}
              >
                Edit
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
              >
                Delete
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs for Projects and Members */}
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="workspace tabs">
            <Tab label="Projects" id="workspace-tab-0" aria-controls="workspace-tabpanel-0" />
            <Tab label="Members" id="workspace-tab-1" aria-controls="workspace-tabpanel-1" />
          </Tabs>
        </Box>
        
        {/* Projects Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">
              Projects ({projects.length})
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
            >
              New Project
            </Button>
          </Box>
          
          <Grid container spacing={3}>
            {projects.map(project => (
              <Grid item xs={12} sm={6} md={4} key={project.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {project.name}
                    </Typography>
                    <Chip 
                      label={project.status.replace('_', ' ')}
                      size="small"
                      color={getStatusColor(project.status)}
                      sx={{ mb: 2 }}
                    />
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {project.description}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">
                        Updated: {new Date(project.last_updated).toLocaleDateString()}
                      </Typography>
                      <Tooltip title={`${project.contributors} contributors`}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <PeopleIcon fontSize="small" sx={{ mr: 0.5 }} />
                          <Typography variant="caption">{project.contributors}</Typography>
                        </Box>
                      </Tooltip>
                    </Box>
                  </CardContent>
                  <Divider />
                  <CardActions>
                    <Button 
                      size="small" 
                      component={RouterLink}
                      to={`/workspaces/${workspaceId}/projects/${project.id}`}
                    >
                      View
                    </Button>
                    <Button 
                      size="small"
                      component={RouterLink}
                      to={`/workspaces/${workspaceId}/projects/${project.id}/versions`}
                      startIcon={<HistoryIcon fontSize="small" />}
                    >
                      History
                    </Button>
                    <Box sx={{ flexGrow: 1 }} />
                    <Tooltip title="Project files">
                      <IconButton size="small">
                        <FolderIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {projects.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No projects yet.
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />}
                sx={{ mt: 1 }}
              >
                Create a Project
              </Button>
            </Paper>
          )}
        </TabPanel>
        
        {/* Members Tab */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">
              Members ({members.length})
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
            >
              Add Member
            </Button>
          </Box>
          
          <Paper>
            <List>
              {members.map((member, index) => (
                <React.Fragment key={member.id}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar>{member.avatar}</Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={member.name}
                      secondary={member.role}
                    />
                    <Tooltip title="Edit role">
                      <IconButton edge="end" aria-label="edit">
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItem>
                  {index < members.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
          
          {members.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No members yet.
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />}
                sx={{ mt: 1 }}
              >
                Add a Member
              </Button>
            </Paper>
          )}
        </TabPanel>
      </Box>
    </Box>
  );
};

export default WorkspaceDetail;