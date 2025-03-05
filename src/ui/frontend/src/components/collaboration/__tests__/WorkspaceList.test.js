import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import WorkspaceList from '../WorkspaceList';
import collaborationService from '../../../services/collaborationService';

// Mock the collaboration service
jest.mock('../../../services/collaborationService');

describe('WorkspaceList Component', () => {
  const mockWorkspaces = [
    {
      id: 'ws1',
      name: 'Research AI Integration',
      description: 'Collaborative workspace for AI research integration projects',
      visibility: 'internal',
      created_at: '2023-10-15T10:30:00Z',
      updated_at: '2023-11-10T14:22:00Z',
      projects_count: 3,
      members_count: 5
    },
    {
      id: 'ws2',
      name: 'Paper Processing Pipeline',
      description: 'Development of the paper processing pipeline',
      visibility: 'private',
      created_at: '2023-09-20T08:45:00Z',
      updated_at: '2023-11-05T11:10:00Z',
      projects_count: 2,
      members_count: 3
    }
  ];

  beforeEach(() => {
    // Reset mocks before each test
    jest.resetAllMocks();
    
    // Mock the getWorkspaces method
    collaborationService.getWorkspaces.mockResolvedValue(mockWorkspaces);
  });

  it('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <WorkspaceList />
      </BrowserRouter>
    );
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders workspaces after loading', async () => {
    render(
      <BrowserRouter>
        <WorkspaceList />
      </BrowserRouter>
    );
    
    // Wait for the workspaces to load
    await waitFor(() => {
      expect(collaborationService.getWorkspaces).toHaveBeenCalledTimes(1);
    });
    
    // Check if workspace names are displayed
    expect(screen.getByText('Research AI Integration')).toBeInTheDocument();
    expect(screen.getByText('Paper Processing Pipeline')).toBeInTheDocument();
    
    // Check if the create button is displayed
    expect(screen.getByText('Create Workspace')).toBeInTheDocument();
  });

  it('displays error message when loading fails', async () => {
    // Mock the service to return an error
    collaborationService.getWorkspaces.mockRejectedValue(new Error('Failed to fetch workspaces'));
    
    render(
      <BrowserRouter>
        <WorkspaceList />
      </BrowserRouter>
    );
    
    // Wait for the error to appear
    await waitFor(() => {
      expect(screen.getByText(/failed to load workspaces/i)).toBeInTheDocument();
    });
  });
});