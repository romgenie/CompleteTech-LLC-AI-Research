import React from 'react';
import { Navigate } from 'react-router-dom';

// Import collaboration components
import WorkspaceList from '../components/collaboration/WorkspaceList';
import WorkspaceDetail from '../components/collaboration/WorkspaceDetail';
import ProjectDetail from '../components/collaboration/ProjectDetail';
import CreateWorkspaceForm from '../components/collaboration/CreateWorkspaceForm';

/**
 * Routes configuration for collaboration features
 */
const collaborationRoutes = [
  {
    path: 'workspaces',
    children: [
      {
        path: '',
        element: <WorkspaceList />
      },
      {
        path: 'new',
        element: <CreateWorkspaceForm />
      },
      {
        path: ':workspaceId',
        element: <WorkspaceDetail />
      },
      {
        path: ':workspaceId/projects/:projectId',
        element: <ProjectDetail />
      }
    ]
  }
];

export default collaborationRoutes;