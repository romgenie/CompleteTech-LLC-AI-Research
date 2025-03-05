import React from 'react';
import { Box } from '@mui/material';
import { WorkspaceDetail } from '../components/collaboration';

/**
 * Page for displaying a specific workspace and its contents
 */
const WorkspaceDetailPage = () => {
  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <WorkspaceDetail />
    </Box>
  );
};

export default WorkspaceDetailPage;