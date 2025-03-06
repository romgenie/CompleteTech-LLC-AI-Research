import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  IconButton,
  Menu,
  MenuItem,
  Button,
  Divider
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Share as ShareIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  Settings as SettingsIcon,
  VisibilityOff as PrivateIcon,
  Public as PublicIcon,
  Business as InternalIcon,
  Folder as FolderIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  Group as GroupIcon
} from '@mui/icons-material';
import collaborationService from '../../services/collaborationService';

/**
 * Component for displaying and managing workspace details
 */
const WorkspaceDetail = () => {
  const { workspaceId } = useParams();
  
  // State
  const [workspace, setWorkspace] = useState(null);
  const [projects, setProjects] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentTab, setCurrentTab] = useState(0);
  const [menuAnchor, setMenuAnchor] = useState(null);

  // Load workspace data on mount
  useEffect(() => {
    fetchWorkspaceData();
  }, [workspaceId]);

  // Fetch all workspace related data
  const fetchWorkspaceData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch workspace details, projects, and members in parallel
      const [workspaceData, projectsData, membersData] = await Promise.all([
        collaborationService.getWorkspace(workspaceId),
        collaborationService.getProjects(workspaceId),
        collaborationService.getWorkspaceMembers(workspaceId)
      ]);

      setWorkspace(workspaceData);
      setProjects(projectsData);
      setMembers(membersData);
    } catch (err) {
      setError('Failed to load workspace details. Please try again.');
      console.error('Error fetching workspace data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Menu handlers
  const handleMenuOpen = (event) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  // Tab change handler
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  // Get visibility icon based on workspace type
  const getVisibilityIcon = () => {
    switch (workspace?.visibility) {
      case 'private':
        return <PrivateIcon fontSize="small" />;
      case 'public':
        return <PublicIcon fontSize="small" />;
      case 'internal':
      default:
        return <InternalIcon fontSize="small" />;
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
      <Alert severity="info">
        Workspace not found
      </Alert>
    );
  }

  return (
    <Box>
      {/* Workspace Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <FolderIcon 
            color="primary" 
            sx={{ 
              fontSize: 40,
              mr: 2
            }} 
          />
          
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              {workspace.name}
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph>
              {workspace.description}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                icon={getVisibilityIcon()}
                label={workspace.visibility.charAt(0).toUpperCase() + workspace.visibility.slice(1)}
                size="small"
              />
              {workspace.tags?.map(tag => (
                <Chip
                  key={tag}
                  label={tag}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>

          <Box>
            <IconButton onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
            <Menu
              anchorEl={menuAnchor}
              open={Boolean(menuAnchor)}
              onClose={handleMenuClose}
            >
              <MenuItem>
                <EditIcon fontSize="small" sx={{ mr: 1 }} /> Edit Workspace
              </MenuItem>
              <MenuItem>
                <ShareIcon fontSize="small" sx={{ mr: 1 }} /> Share
              </MenuItem>
              <MenuItem>
                <SettingsIcon fontSize="small" sx={{ mr: 1 }} /> Settings
              </MenuItem>
              <Divider />
              <MenuItem sx={{ color: 'error.main' }}>
                <DeleteIcon fontSize="small" sx={{ mr: 1 }} /> Delete
              </MenuItem>
            </Menu>
          </Box>
        </Box>
      </Paper>

      {/* Tabs Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<DescriptionIcon />} 
            iconPosition="start"
            label={`Projects (${projects.length})`} 
          />
          <Tab 
            icon={<GroupIcon />}
            iconPosition="start" 
            label={`Members (${members.length})`} 
          />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      {currentTab === 0 ? (
        <Grid container spacing={3}>
          {/* Projects List */}
          {projects.map(project => (
            <Grid item xs={12} sm={6} md={4} key={project.id}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {project.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {project.description}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip 
                    label={project.status} 
                    size="small"
                    color={project.status === 'completed' ? 'success' : 'default'}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {project.contributors} contributors
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          ))}
          
          {/* Add Project Card */}
          <Grid item xs={12} sm={6} md={4}>
            <Paper 
              sx={{ 
                p: 2, 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'action.hover',
                }
              }}
            >
              <IconButton 
                color="primary"
                sx={{ mb: 1 }}
              >
                <AddIcon />
              </IconButton>
              <Typography variant="h6">
                Add Project
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Paper sx={{ p: 3 }}>
          {/* Members List */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Team Members
            </Typography>
            <Button startIcon={<AddIcon />}>
              Add Member
            </Button>
          </Box>
          
          <List>
            {members.map(member => (
              <ListItem
                key={member.id}
                secondaryAction={
                  <IconButton edge="end">
                    <MoreVertIcon />
                  </IconButton>
                }
              >
                <ListItemAvatar>
                  <Avatar>{member.avatar}</Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={member.name}
                  secondary={member.role}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default WorkspaceDetail;