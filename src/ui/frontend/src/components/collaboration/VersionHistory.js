import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, List, ListItem, ListItemIcon,
  ListItemText, ListItemSecondaryAction, IconButton,
  Chip, Divider, Button, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, FormControl,
  FormLabel, Select, MenuItem, CircularProgress,
  Alert, Tabs, Tab, Tooltip, Collapse
} from '@mui/material';
import { 
  Timeline as TimelineIcon,
  ForkRight as BranchIcon, 
  Merge as MergeIcon,
  Visibility as ViewIcon,
  Compare as CompareIcon,
  FileDownload as DownloadIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as ApprovedIcon,
  PendingActions as PendingIcon,
  Create as CreateIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';
import collaborationService from '../../services/collaborationService';

/**
 * Component for displaying project version history
 */
const VersionHistory = ({ projectId }) => {
  const [versions, setVersions] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [compareVersion, setCompareVersion] = useState(null);
  const [expandedVersions, setExpandedVersions] = useState({});
  
  // Dialog states
  const [branchDialogOpen, setBranchDialogOpen] = useState(false);
  const [newBranchName, setNewBranchName] = useState('');
  const [newBranchDescription, setNewBranchDescription] = useState('');
  const [branchBaseVersion, setBranchBaseVersion] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  // Merge dialog states
  const [mergeDialogOpen, setMergeDialogOpen] = useState(false);
  const [sourceBranch, setSourceBranch] = useState('');
  const [targetBranch, setTargetBranch] = useState('main');
  const [mergeTitle, setMergeTitle] = useState('');
  const [mergeDescription, setMergeDescription] = useState('');

  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);

  // Load versions on component mount
  useEffect(() => {
    const fetchVersionData = async () => {
      try {
        setLoading(true);
        
        // Get all versions
        const versionsData = await collaborationService.getProjectVersions(projectId);
        setVersions(versionsData);
        
        // Get all branches
        const branchesData = await collaborationService.getProjectBranches(projectId);
        setBranches(branchesData);
        
        // Automatically select latest version
        if (versionsData.length > 0) {
          const mainVersions = versionsData.filter(v => v.branch_name === 'main');
          if (mainVersions.length > 0) {
            setSelectedVersion(mainVersions[0]);
          } else {
            setSelectedVersion(versionsData[0]);
          }
        }
        
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load version history');
        console.error('Error loading version history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchVersionData();
  }, [projectId]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Handle creating a new branch
  const handleCreateBranch = async () => {
    if (!newBranchName.trim() || !branchBaseVersion) {
      return;
    }
    
    try {
      setSubmitting(true);
      
      const newBranch = await collaborationService.createBranch(projectId, {
        name: newBranchName,
        description: newBranchDescription,
        created_from_version_id: branchBaseVersion.id
      });
      
      // Update branches list
      setBranches([...branches, newBranch]);
      
      // Reset form and close dialog
      setNewBranchName('');
      setNewBranchDescription('');
      setBranchBaseVersion(null);
      setBranchDialogOpen(false);
      
    } catch (err) {
      console.error('Error creating branch:', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  // Handle creating a merge request
  const handleCreateMergeRequest = async () => {
    if (!sourceBranch || !targetBranch || !mergeTitle.trim()) {
      return;
    }
    
    try {
      setSubmitting(true);
      
      const mergeRequest = await collaborationService.createMergeRequest(projectId, {
        title: mergeTitle,
        description: mergeDescription,
        source_branch: sourceBranch,
        target_branch: targetBranch
      });
      
      // Navigate to merge request page
      navigate(`/projects/${projectId}/merge-requests/${mergeRequest.id}`);
      
    } catch (err) {
      console.error('Error creating merge request:', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  // Handle toggling version details expansion
  const toggleVersionExpand = (versionId) => {
    setExpandedVersions({
      ...expandedVersions,
      [versionId]: !expandedVersions[versionId]
    });
  };
  
  // Filter versions by branch name for branch tab
  const getVersionsByBranch = (branchName) => {
    return versions.filter(v => v.branch_name === branchName);
  };
  
  // Get chip for version status
  const getStatusChip = (status) => {
    switch(status) {
      case 'APPROVED':
        return <Chip size="small" icon={<ApprovedIcon />} label="Approved" color="success" />;
      case 'PENDING':
        return <Chip size="small" icon={<PendingIcon />} label="Pending" color="warning" />;
      default:
        return <Chip size="small" label={status} />;
    }
  };

  // If loading, show a loading indicator
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // If there's an error, show an error message
  if (error) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography color="error">{error}</Typography>
        <Button 
          variant="text" 
          sx={{ mt: 2 }} 
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h1">
          Version History
        </Typography>
        
        <Box>
          <Button 
            variant="outlined" 
            startIcon={<BranchIcon />}
            onClick={() => setBranchDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Branch
          </Button>
          
          <Button 
            variant="outlined" 
            startIcon={<MergeIcon />}
            onClick={() => setMergeDialogOpen(true)}
          >
            Merge Request
          </Button>
        </Box>
      </Box>
      
      {/* Tabs for different views */}
      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab icon={<TimelineIcon />} iconPosition="start" label="Timeline" />
        <Tab icon={<BranchIcon />} iconPosition="start" label="Branches" />
      </Tabs>
      
      {/* Timeline tab */}
      {tabValue === 0 && (
        <List>
          {versions.length === 0 ? (
            <Box sx={{ py: 3, textAlign: 'center' }}>
              <Typography>No versions available for this project.</Typography>
            </Box>
          ) : (
            versions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).map((version) => (
              <React.Fragment key={version.id}>
                <ListItem 
                  sx={{ 
                    bgcolor: selectedVersion?.id === version.id ? 'action.selected' : 'inherit',
                    borderLeft: `3px solid ${version.branch_name === 'main' ? '#1976d2' : '#9c27b0'}`,
                    pl: 2
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="subtitle1" component="span">
                          {version.name} 
                        </Typography>
                        <Typography variant="body2" component="span" color="text.secondary" sx={{ ml: 1 }}>
                          (v{version.version_number})
                        </Typography>
                        <Chip 
                          size="small" 
                          label={version.branch_name} 
                          color={version.branch_name === 'main' ? 'primary' : 'secondary'}
                          sx={{ ml: 1 }}
                        />
                        {version.status !== 'DRAFT' && (
                          <Box sx={{ ml: 1 }}>
                            {getStatusChip(version.status)}
                          </Box>
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {formatDistanceToNow(new Date(version.created_at), { addSuffix: true })} by {version.created_by_name || 'Unknown User'}
                        </Typography>
                        
                        {version.description && (
                          <Typography variant="body2" sx={{ mt: 0.5 }}>
                            {version.description}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <IconButton edge="end" onClick={() => toggleVersionExpand(version.id)}>
                      {expandedVersions[version.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                    <IconButton edge="end" onClick={() => setSelectedVersion(version)}>
                      <ViewIcon />
                    </IconButton>
                    <IconButton 
                      edge="end" 
                      onClick={() => setCompareVersion(compareVersion?.id === version.id ? null : version)}
                      color={compareVersion?.id === version.id ? 'primary' : 'default'}
                    >
                      <CompareIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
                
                {/* Expanded version details */}
                <Collapse in={expandedVersions[version.id]} timeout="auto" unmountOnExit>
                  <Box sx={{ pl: 4, pr: 2, py: 1, bgcolor: 'background.paper' }}>
                    {version.changes && version.changes.length > 0 ? (
                      <List dense disablePadding>
                        {version.changes.map((change, idx) => (
                          <ListItem key={idx}>
                            <ListItemText
                              primary={`${change.type}: ${change.path}`}
                              secondary={change.before && change.after ? 'Modified content' : change.after ? 'Added new content' : 'Removed content'}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No detailed changes available.
                      </Typography>
                    )}
                  </Box>
                </Collapse>
                
                <Divider variant="inset" component="li" />
              </React.Fragment>
            ))
          )}
        </List>
      )}
      
      {/* Branches tab */}
      {tabValue === 1 && (
        <Box>
          {branches.length === 0 ? (
            <Box sx={{ py: 3, textAlign: 'center' }}>
              <Typography>No branches available for this project.</Typography>
              <Button 
                variant="text" 
                startIcon={<BranchIcon />} 
                sx={{ mt: 2 }} 
                onClick={() => setBranchDialogOpen(true)}
              >
                Create your first branch
              </Button>
            </Box>
          ) : (
            branches.map((branch) => (
              <Box key={branch.id} sx={{ mb: 3 }}>
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  bgcolor: 'background.paper', 
                  p: 2, 
                  borderRadius: 1
                }}>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <BranchIcon color={branch.name === 'main' ? 'primary' : 'secondary'} sx={{ mr: 1 }} />
                      <Typography variant="h6">
                        {branch.name}
                      </Typography>
                      {branch.status === 'merged' && (
                        <Chip 
                          size="small" 
                          label="Merged" 
                          icon={<MergeIcon />} 
                          color="success" 
                          sx={{ ml: 1 }}
                        />
                      )}
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary">
                      Created {formatDistanceToNow(new Date(branch.created_at), { addSuffix: true })} by {branch.created_by_name || 'Unknown User'}
                    </Typography>
                    
                    {branch.description && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {branch.description}
                      </Typography>
                    )}
                  </Box>
                  
                  {branch.status !== 'merged' && branch.name !== 'main' && (
                    <Button 
                      variant="outlined" 
                      startIcon={<MergeIcon />}
                      onClick={() => {
                        setSourceBranch(branch.name);
                        setTargetBranch('main');
                        setMergeTitle(`Merge ${branch.name} into main`);
                        setMergeDialogOpen(true);
                      }}
                    >
                      Merge
                    </Button>
                  )}
                </Box>
                
                {/* Branch versions */}
                <List dense sx={{ ml: 4, mt: 1 }}>
                  {getVersionsByBranch(branch.name).map((version) => (
                    <ListItem key={version.id}>
                      <ListItemIcon>
                        <CreateIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${version.name} (v${version.version_number})`}
                        secondary={formatDistanceToNow(new Date(version.created_at), { addSuffix: true })}
                      />
                      <ListItemSecondaryAction>
                        <IconButton edge="end" size="small" onClick={() => setSelectedVersion(version)}>
                          <ViewIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Box>
            ))
          )}
        </Box>
      )}
      
      {/* Create Branch Dialog */}
      <Dialog open={branchDialogOpen} onClose={() => setBranchDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Branch</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="branch-name"
            label="Branch Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newBranchName}
            onChange={(e) => setNewBranchName(e.target.value)}
            sx={{ mb: 2, mt: 1 }}
            helperText="Use lowercase letters, numbers, and hyphens"
          />
          
          <TextField
            margin="dense"
            id="branch-description"
            label="Description (optional)"
            type="text"
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            value={newBranchDescription}
            onChange={(e) => setNewBranchDescription(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth margin="normal">
            <FormLabel id="base-version-label">Base Version</FormLabel>
            <Select
              labelId="base-version-label"
              id="base-version"
              value={branchBaseVersion?.id || ''}
              onChange={(e) => {
                const selectedId = e.target.value;
                const selected = versions.find(v => v.id === selectedId);
                setBranchBaseVersion(selected);
              }}
              displayEmpty
            >
              <MenuItem value="" disabled>Select a base version</MenuItem>
              {versions.map(version => (
                <MenuItem key={version.id} value={version.id}>
                  {version.name} (v{version.version_number}) - {version.branch_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBranchDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateBranch} 
            variant="contained" 
            disabled={submitting || !newBranchName.trim() || !branchBaseVersion}
          >
            {submitting ? <CircularProgress size={24} /> : 'Create Branch'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Merge Request Dialog */}
      <Dialog open={mergeDialogOpen} onClose={() => setMergeDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Merge Request</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <FormLabel id="source-branch-label">Source Branch</FormLabel>
            <Select
              labelId="source-branch-label"
              id="source-branch"
              value={sourceBranch}
              onChange={(e) => setSourceBranch(e.target.value)}
              displayEmpty
            >
              <MenuItem value="" disabled>Select source branch</MenuItem>
              {branches
                .filter(branch => branch.name !== 'main' && branch.status !== 'merged')
                .map(branch => (
                  <MenuItem key={branch.id} value={branch.name}>
                    {branch.name}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <FormLabel id="target-branch-label">Target Branch</FormLabel>
            <Select
              labelId="target-branch-label"
              id="target-branch"
              value={targetBranch}
              onChange={(e) => setTargetBranch(e.target.value)}
              displayEmpty
            >
              <MenuItem value="" disabled>Select target branch</MenuItem>
              {branches
                .filter(branch => branch.name !== sourceBranch)
                .map(branch => (
                  <MenuItem key={branch.id} value={branch.name}>
                    {branch.name}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            id="merge-title"
            label="Title"
            type="text"
            fullWidth
            variant="outlined"
            value={mergeTitle}
            onChange={(e) => setMergeTitle(e.target.value)}
            sx={{ mb: 2, mt: 2 }}
          />
          
          <TextField
            margin="dense"
            id="merge-description"
            label="Description"
            type="text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={mergeDescription}
            onChange={(e) => setMergeDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMergeDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateMergeRequest} 
            variant="contained" 
            disabled={submitting || !sourceBranch || !targetBranch || !mergeTitle.trim()}
          >
            {submitting ? <CircularProgress size={24} /> : 'Create Merge Request'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Version comparison */}
      {selectedVersion && compareVersion && (
        <Box sx={{ mt: 3, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            Comparing Versions
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="subtitle2">
                {selectedVersion.name} (v{selectedVersion.version_number})
              </Typography>
              <Chip 
                size="small" 
                label={selectedVersion.branch_name} 
                color="primary" 
                sx={{ mt: 0.5 }}
              />
            </Box>
            
            <CompareIcon sx={{ mx: 2 }} />
            
            <Box>
              <Typography variant="subtitle2">
                {compareVersion.name} (v{compareVersion.version_number})
              </Typography>
              <Chip 
                size="small" 
                label={compareVersion.branch_name} 
                color="secondary" 
                sx={{ mt: 0.5 }}
              />
            </Box>
          </Box>
          
          <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1 }}>
            <Typography variant="subtitle1" gutterBottom>
              Changes Summary
            </Typography>
            
            <Typography>
              This would display a visual diff of changes between the two versions.
            </Typography>
            
            <Button 
              variant="outlined" 
              startIcon={<DownloadIcon />}
              sx={{ mt: 2 }}
            >
              Download Diff
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default VersionHistory;