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
  Avatar,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  IconButton,
  Card,
  CardContent,
  CardActions,
  Tooltip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  LinearProgress
} from '@mui/material';
import { 
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  Add as AddIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Folder as FolderIcon,
  Comment as CommentIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
  InsertDriveFile as FileIcon,
  Link as LinkIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { useParams, Link as RouterLink } from 'react-router-dom';
import collaborationService from '../../services/collaborationService';

// Panel for the content of each tab
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
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
 * Component to display the details of a specific project
 */
const ProjectDetail = () => {
  const { workspaceId, projectId } = useParams();
  const [project, setProject] = useState(null);
  const [contributors, setContributors] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // Fetch project details
  useEffect(() => {
    const fetchProjectDetails = async () => {
      if (!workspaceId || !projectId) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // In a real app, we would use proper API calls
        // For now, we'll simulate with mock data
        const mockProject = {
          id: projectId,
          name: "Knowledge Graph System",
          description: "Development of the knowledge graph system for research integration. This system will store and organize research information in a graph structure that allows for complex querying and knowledge discovery.",
          status: "in_progress",
          created_at: "2023-10-18T09:20:00Z",
          updated_at: "2023-11-09T08:45:00Z",
          tags: ["Graph Database", "Knowledge Representation", "Research"],
          workspace_id: workspaceId,
          completion_percentage: 65,
          deadline: "2023-12-15T00:00:00Z"
        };
        
        const mockContributors = [
          {
            id: "user1",
            name: "John Doe",
            role: "Project Lead",
            avatar: "J",
            contributions: 18
          },
          {
            id: "user2",
            name: "Jane Smith",
            role: "Developer",
            avatar: "J",
            contributions: 12
          },
          {
            id: "user4",
            name: "Alice Johnson",
            role: "Knowledge Engineer",
            avatar: "A",
            contributions: 7
          }
        ];
        
        const mockTasks = [
          {
            id: "task1",
            title: "Design Database Schema",
            description: "Create the schema for the knowledge graph database",
            status: "completed",
            assignee: "Jane Smith",
            due_date: "2023-11-02T00:00:00Z"
          },
          {
            id: "task2",
            title: "Implement Graph Query API",
            description: "Develop the API for querying the knowledge graph",
            status: "in_progress",
            assignee: "John Doe",
            due_date: "2023-11-20T00:00:00Z"
          },
          {
            id: "task3",
            title: "Create Visualization Component",
            description: "Develop the visualization component for the knowledge graph",
            status: "not_started",
            assignee: null,
            due_date: "2023-12-10T00:00:00Z"
          }
        ];
        
        const mockResources = [
          {
            id: "res1",
            name: "Knowledge Graph Design Doc.pdf",
            type: "document",
            size: "1.2 MB",
            last_updated: "2023-10-20T14:30:00Z",
            uploaded_by: "John Doe"
          },
          {
            id: "res2",
            name: "Database Schema Diagram.png",
            type: "image",
            size: "450 KB",
            last_updated: "2023-10-25T10:15:00Z",
            uploaded_by: "Jane Smith"
          },
          {
            id: "res3",
            name: "https://github.com/example/knowledge-graph-repos",
            type: "link",
            last_updated: "2023-11-01T09:00:00Z",
            uploaded_by: "John Doe"
          }
        ];
        
        setProject(mockProject);
        setContributors(mockContributors);
        setTasks(mockTasks);
        setResources(mockResources);
      } catch (err) {
        setError(err.message || 'Failed to load project details');
        console.error('Error fetching project details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProjectDetails();
  }, [workspaceId, projectId]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Handle delete dialog
  const handleOpenDeleteDialog = () => {
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
  };

  // Handle delete project
  const handleDeleteProject = () => {
    // Add deletion logic here
    setDeleteDialogOpen(false);
    // Navigate back to workspace after deletion
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'not_started': return 'default';
      case 'blocked': return 'error';
      default: return 'default';
    }
  };

  // Get resource icon
  const getResourceIcon = (type) => {
    switch (type) {
      case 'document': return <DescriptionIcon />;
      case 'image': return <FileIcon />;
      case 'link': return <LinkIcon />;
      default: return <FileIcon />;
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

  if (!project) {
    return (
      <Alert severity="info" sx={{ mb: 3 }}>
        Project not found
      </Alert>
    );
  }

  const daysUntilDeadline = () => {
    if (!project.deadline) return null;
    const deadline = new Date(project.deadline);
    const today = new Date();
    const diffTime = deadline - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const deadlineDays = daysUntilDeadline();

  return (
    <Box>
      {/* Project Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="h4" component="h1">
                {project.name}
              </Typography>
              <Chip 
                label={project.status.replace('_', ' ')}
                color={getStatusColor(project.status)}
                sx={{ ml: 2 }}
              />
            </Box>
            <Typography variant="body1" color="text.secondary" paragraph>
              {project.description}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
              {project.tags && project.tags.map(tag => (
                <Chip key={tag} label={tag} size="small" />
              ))}
            </Box>
            
            {project.completion_percentage !== undefined && (
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Progress</Typography>
                  <Typography variant="body2">{project.completion_percentage}%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={project.completion_percentage} 
                  sx={{ mt: 1 }}
                />
              </Box>
            )}
            
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Created
                </Typography>
                <Typography variant="body2">
                  {new Date(project.created_at).toLocaleDateString()}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Last Updated
                </Typography>
                <Typography variant="body2">
                  {new Date(project.updated_at).toLocaleDateString()}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary">
                  Contributors
                </Typography>
                <Typography variant="body2">
                  {contributors.length}
                </Typography>
              </Grid>
              {project.deadline && (
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Deadline
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2">
                      {new Date(project.deadline).toLocaleDateString()}
                    </Typography>
                    {deadlineDays > 0 && deadlineDays <= 7 ? (
                      <Chip 
                        label={`${deadlineDays} days`}
                        color="warning"
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    ) : null}
                  </Box>
                </Grid>
              )}
            </Grid>
          </Grid>
          
          <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' }, flexDirection: 'column', alignItems: { xs: 'flex-start', md: 'flex-end' } }}>
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
                onClick={handleOpenDeleteDialog}
              >
                Delete
              </Button>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Button
                component={RouterLink}
                to={`/workspaces/${workspaceId}`}
                variant="text"
                size="small"
              >
                Back to Workspace
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs for Overview, Tasks, Resources and Contributors */}
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="project tabs">
            <Tab label="Tasks" id="project-tab-0" aria-controls="project-tabpanel-0" />
            <Tab label="Resources" id="project-tab-1" aria-controls="project-tabpanel-1" />
            <Tab label="Contributors" id="project-tab-2" aria-controls="project-tabpanel-2" />
          </Tabs>
        </Box>
        
        {/* Tasks Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">
              Tasks ({tasks.length})
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
            >
              Add Task
            </Button>
          </Box>
          
          <Grid container spacing={2}>
            {tasks.map(task => (
              <Grid item xs={12} sm={6} md={4} key={task.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="h6" component="h3">
                        {task.title}
                      </Typography>
                      <Chip 
                        label={task.status.replace('_', ' ')}
                        color={getStatusColor(task.status)}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {task.description}
                    </Typography>
                    {task.assignee && (
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Assignee:</strong> {task.assignee}
                      </Typography>
                    )}
                    {task.due_date && (
                      <Typography variant="body2">
                        <strong>Due Date:</strong> {new Date(task.due_date).toLocaleDateString()}
                      </Typography>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button size="small">Edit</Button>
                    <Button size="small" color="error">Delete</Button>
                    {task.status !== 'completed' && (
                      <Button size="small" color="success">Mark as Complete</Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {tasks.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No tasks yet.
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />}
                sx={{ mt: 1 }}
              >
                Add a Task
              </Button>
            </Paper>
          )}
        </TabPanel>
        
        {/* Resources Tab */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">
              Resources ({resources.length})
            </Typography>
            <Box>
              <Button
                variant="contained"
                color="primary"
                startIcon={<UploadIcon />}
                sx={{ mr: 1 }}
              >
                Upload
              </Button>
              <Button
                variant="outlined"
                startIcon={<LinkIcon />}
              >
                Add Link
              </Button>
            </Box>
          </Box>
          
          <Paper>
            <List>
              {resources.map((resource, index) => (
                <React.Fragment key={resource.id}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar>
                        {getResourceIcon(resource.type)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={resource.name}
                      secondary={
                        <>
                          {resource.type !== 'link' && resource.size && `${resource.size} · `}
                          {`Updated ${new Date(resource.last_updated).toLocaleDateString()} by ${resource.uploaded_by}`}
                        </>
                      }
                    />
                    {resource.type !== 'link' && (
                      <Tooltip title="Download">
                        <IconButton edge="end" aria-label="download">
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Delete">
                      <IconButton edge="end" aria-label="delete" sx={{ ml: 1 }}>
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItem>
                  {index < resources.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
          
          {resources.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No resources yet.
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<UploadIcon />}
                sx={{ mt: 1, mr: 1 }}
              >
                Upload a File
              </Button>
              <Button 
                variant="outlined" 
                startIcon={<LinkIcon />}
                sx={{ mt: 1 }}
              >
                Add a Link
              </Button>
            </Paper>
          )}
        </TabPanel>
        
        {/* Contributors Tab */}
        <TabPanel value={tabValue} index={2}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6">
              Contributors ({contributors.length})
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
            >
              Add Contributor
            </Button>
          </Box>
          
          <Grid container spacing={2}>
            {contributors.map(contributor => (
              <Grid item xs={12} sm={6} md={4} key={contributor.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ mr: 2 }}>{contributor.avatar}</Avatar>
                      <Box>
                        <Typography variant="h6">{contributor.name}</Typography>
                        <Typography variant="body2" color="text.secondary">{contributor.role}</Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2">
                      <strong>Contributions:</strong> {contributor.contributions}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">View Profile</Button>
                    <Button size="small">Change Role</Button>
                    <Button size="small" color="error">Remove</Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {contributors.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No contributors yet.
              </Typography>
              <Button 
                variant="outlined" 
                startIcon={<AddIcon />}
                sx={{ mt: 1 }}
              >
                Add a Contributor
              </Button>
            </Paper>
          )}
        </TabPanel>
      </Box>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          Delete Project
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete this project? This action cannot be undone.
            All project data, including tasks, resources, and contributions will be permanently lost.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteProject} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProjectDetail;