import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Link, useParams } from 'react-router-dom';
import { ArrowBack } from '@mui/icons-material';
import { VersionHistory } from '../components/collaboration';

/**
 * Page for displaying project version history
 */
const ProjectVersionsPage = () => {
  const { projectId, workspaceId } = useParams();

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Button
        component={Link}
        to={`/workspaces/${workspaceId}/projects/${projectId}`}
        startIcon={<ArrowBack />}
        sx={{ mb: 3 }}
      >
        Back to Project
      </Button>
      
      <VersionHistory projectId={projectId} />
    </Box>
  );
};

export default ProjectVersionsPage;