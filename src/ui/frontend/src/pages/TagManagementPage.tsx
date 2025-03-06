import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Button, 
  Divider,
  Container,
  Grid,
  IconButton,
  Tooltip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ShareIcon from '@mui/icons-material/Share';
import WarningIcon from '@mui/icons-material/Warning';
import InsightsIcon from '@mui/icons-material/Insights';
import DiscoverIcon from '@mui/icons-material/Explore';

import { useTags } from '../services/tagsService';
import { Tag } from '../types/research';
import { TagHierarchy } from '../components/Tags/TagHierarchy';
import TagDiscovery from '../components/Tags/TagDiscovery';
import TagSharingDialog from '../components/Tags/TagSharingDialog';
import TagConflictResolution from '../components/Tags/TagConflictResolution';
import TagAnalytics from '../components/Tags/TagAnalytics';

/**
 * Page for managing tags and taxonomies
 */
const TagManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('hierarchy');
  const [selectedTagId, setSelectedTagId] = useState<string | undefined>();
  const [sharingDialogOpen, setSharingDialogOpen] = useState<boolean>(false);
  
  const { data: tags, isLoading, refetch } = useTags();
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveTab(newValue);
  };
  
  const handleTagSelect = (tag: Tag) => {
    setSelectedTagId(tag.id);
  };
  
  const handleShareTag = () => {
    setSharingDialogOpen(true);
  };
  
  const handleCloseShareDialog = () => {
    setSharingDialogOpen(false);
  };
  
  const handleTagUpdated = (updatedTag: Tag) => {
    refetch();
  };
  
  const selectedTag = selectedTagId && tags ? 
    tags.find(tag => tag.id === selectedTagId) : undefined;
  
  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" gutterBottom>
        Tag Management
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="tag management tabs">
            <Tab label="Hierarchy" value="hierarchy" />
            <Tab label="Discovery" value="discovery" />
            <Tab label="Conflicts" value="conflicts" />
            <Tab label="Analytics" value="analytics" />
          </Tabs>
          
          <Box>
            {selectedTagId && (
              <Tooltip title="Share Tag">
                <IconButton onClick={handleShareTag} sx={{ mr: 1 }}>
                  <ShareIcon />
                </IconButton>
              </Tooltip>
            )}
            <Button 
              variant="contained" 
              startIcon={<AddIcon />}
              sx={{ ml: 1 }}
            >
              New Tag
            </Button>
          </Box>
        </Box>
        
        <Divider />
        
        <Box sx={{ mt: 3 }}>
          {/* Hierarchy View */}
          {activeTab === 'hierarchy' && (
            <TagHierarchy tags={tags || []} onSelectTag={handleTagSelect} selectedTagId={selectedTagId} />
          )}
          
          {/* Discovery View */}
          {activeTab === 'discovery' && (
            <TagDiscovery onTagSelect={handleTagSelect} selectedTagIds={selectedTagId ? [selectedTagId] : []} />
          )}
          
          {/* Conflicts View */}
          {activeTab === 'conflicts' && (
            <TagConflictResolution onResolved={() => refetch()} />
          )}
          
          {/* Analytics View */}
          {activeTab === 'analytics' && (
            <TagAnalytics tagId={selectedTagId} />
          )}
        </Box>
      </Paper>
      
      {/* Tag Sharing Dialog */}
      {selectedTag && (
        <TagSharingDialog 
          open={sharingDialogOpen} 
          onClose={handleCloseShareDialog} 
          tag={selectedTag}
          onTagUpdated={handleTagUpdated}
        />
      )}
    </Container>
  );
};

export default TagManagementPage;