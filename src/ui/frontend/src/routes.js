import { Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import WorkspaceList from './components/collaboration/WorkspaceList';
import WorkspaceDetail from './components/collaboration/WorkspaceDetail';
import CreateWorkspaceForm from './components/collaboration/CreateWorkspaceForm';
import NotFound from './pages/NotFound';

const routes = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { path: '/', element: <Navigate to="/workspaces" /> },
      { path: '/workspaces', element: <WorkspaceList /> },
      { path: '/workspaces/new', element: <CreateWorkspaceForm /> },
      { path: '/workspaces/:workspaceId', element: <WorkspaceDetail /> },
      { path: '*', element: <NotFound /> }
    ]
  }
];

export default routes;