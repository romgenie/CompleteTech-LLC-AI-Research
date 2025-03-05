import React, { useState } from 'react';
import { Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, 
  FormControl, InputLabel, Select, MenuItem, TextField, Typography } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { WorkspacesList } from '../components/collaboration';
import { useAuth } from '../contexts/AuthContext';
import collaborationService from '../services/collaborationService';

/**
 * Page for displaying and managing workspaces
 */
const WorkspacesPage = () => {
  const { currentUser } = useAuth();
  
  // State for create workspace dialog
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newWorkspace, setNewWorkspace] = useState({
    name: '',
    description: '',
    visibility: 'private',
    tags: ''
  });
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Handle opening create workspace dialog
  const handleOpenCreateDialog = async () => {
    try {
      // Load user's teams
      const userTeams = await collaborationService.getUserTeams();
      setTeams(userTeams);
      
      if (userTeams.length > 0) {
        setSelectedTeam(userTeams[0].id);
      }
      
      setCreateDialogOpen(true);
    } catch (err) {
      console.error('Error loading teams:', err);
      setCreateDialogOpen(true);
    }
  };
  
  // Handle create workspace submission
  const handleCreateWorkspace = async () => {
    if (!newWorkspace.name.trim()) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const workspaceData = {
        name: newWorkspace.name,
        description: newWorkspace.description,
        team_id: selectedTeam,
        visibility: newWorkspace.visibility,
        tags: newWorkspace.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      await collaborationService.createWorkspace(workspaceData);
      
      // Reset form and close dialog
      setNewWorkspace({
        name: '',
        description: '',
        visibility: 'private',
        tags: ''
      });
      setCreateDialogOpen(false);
      
      // Trigger workspace list refresh
      setRefreshTrigger(prev => prev + 1);
      
    } catch (err) {
      setError(err.message || 'Failed to create workspace');
      console.error('Error creating workspace:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <WorkspacesList 
        key={refreshTrigger} // Force re-render when refreshTrigger changes
        onCreateWorkspace={handleOpenCreateDialog}
      />
      
      {/* Create workspace dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Workspace</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Workspace Name"
            type="text"
            fullWidth
            variant="outlined"
            value={newWorkspace.name}
            onChange={(e) => setNewWorkspace({...newWorkspace, name: e.target.value})}
            sx={{ mt: 1 }}
            required
          />
          
          <TextField
            margin="dense"
            id="description"
            label="Description"
            type="text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newWorkspace.description}
            onChange={(e) => setNewWorkspace({...newWorkspace, description: e.target.value})}
            sx={{ mt: 2 }}
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel id="team-label">Team</InputLabel>
            <Select
              labelId="team-label"
              id="team"
              value={selectedTeam}
              label="Team"
              onChange={(e) => setSelectedTeam(e.target.value)}
              disabled={teams.length === 0}
            >
              {teams.length === 0 ? (
                <MenuItem value="" disabled>
                  No teams available (will create personal workspace)
                </MenuItem>
              ) : (
                teams.map(team => (
                  <MenuItem key={team.id} value={team.id}>
                    {team.name}
                  </MenuItem>
                ))
              )}
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel id="visibility-label">Visibility</InputLabel>
            <Select
              labelId="visibility-label"
              id="visibility"
              value={newWorkspace.visibility}
              label="Visibility"
              onChange={(e) => setNewWorkspace({...newWorkspace, visibility: e.target.value})}
            >
              <MenuItem value="private">Private</MenuItem>
              <MenuItem value="internal">Internal</MenuItem>
              <MenuItem value="public">Public</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            id="tags"
            label="Tags (comma separated)"
            type="text"
            fullWidth
            variant="outlined"
            value={newWorkspace.tags}
            onChange={(e) => setNewWorkspace({...newWorkspace, tags: e.target.value})}
            sx={{ mt: 2 }}
            placeholder="ai, research, collaboration"
          />
          
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateWorkspace} 
            variant="contained" 
            disabled={loading || !newWorkspace.name.trim()}
          >
            Create Workspace
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkspacesPage;