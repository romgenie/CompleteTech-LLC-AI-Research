import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import WorkspaceDetail from '../WorkspaceDetail';
import collaborationService from '../../../services/collaborationService';

// Mock the react-router-dom hooks
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ workspaceId: 'ws1' }),
  Link: ({ children, ...rest }) => <a {...rest}>{children}</a>
}));

// Mock the collaboration service
jest.mock('../../../services/collaborationService');

describe('WorkspaceDetail Component', () => {
  const mockWorkspace = {
    id: 'ws1',
    name: 'Research AI Integration',
    description: 'Collaborative workspace for AI research integration projects',
    visibility: 'internal',
    created_at: '2023-10-15T10:30:00Z',
    updated_at: '2023-11-10T14:22:00Z',
    tags: ['AI', 'Research', 'Integration']
  };

  const mockProjects = [
    {
      id: 'proj1',
      name: 'Knowledge Graph System',
      description: 'Development of the knowledge graph system for research integration',
      status: 'in_progress',
      last_updated: '2023-11-09T08:45:00Z',
      contributors: 5
    },
    {
      id: 'proj2',
      name: 'Research Orchestrator',
      description: 'Implementation of the research orchestration component',
      status: 'completed',
      last_updated: '2023-11-02T15:20:00Z',
      contributors: 3
    }
  ];

  const mockMembers = [
    {
      id: 'user1',
      name: 'John Doe',
      role: 'Admin',
      avatar: 'J'
    },
    {
      id: 'user2',
      name: 'Jane Smith',
      role: 'Contributor',
      avatar: 'J'
    }
  ];

  beforeEach(() => {
    // Reset mocks before each test
    jest.resetAllMocks();
    
    // Mock the service methods
    collaborationService.getWorkspace = jest.fn().mockResolvedValue(mockWorkspace);
    collaborationService.getProjects = jest.fn().mockResolvedValue(mockProjects);
    collaborationService.getWorkspaceMembers = jest.fn().mockResolvedValue(mockMembers);
  });

  it('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <WorkspaceDetail />
      </BrowserRouter>
    );
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders workspace details after loading', async () => {
    render(
      <BrowserRouter>
        <WorkspaceDetail />
      </BrowserRouter>
    );
    
    // Wait for the workspace details to load
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check if workspace name is displayed
    expect(screen.getByText('Research AI Integration')).toBeInTheDocument();
    
    // Check if description is displayed
    expect(screen.getByText('Collaborative workspace for AI research integration projects')).toBeInTheDocument();
    
    // Check if tags are displayed
    expect(screen.getByText('AI')).toBeInTheDocument();
    expect(screen.getByText('Research')).toBeInTheDocument();
    expect(screen.getByText('Integration')).toBeInTheDocument();
    
    // Check if projects tab exists
    expect(screen.getByText('Projects')).toBeInTheDocument();
    
    // Check if members tab exists
    expect(screen.getByText('Members')).toBeInTheDocument();
  });

  it('displays projects when Projects tab is active', async () => {
    render(
      <BrowserRouter>
        <WorkspaceDetail />
      </BrowserRouter>
    );
    
    // Wait for the workspace details to load
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Projects tab should be active by default
    expect(screen.getByText('Knowledge Graph System')).toBeInTheDocument();
    expect(screen.getByText('Research Orchestrator')).toBeInTheDocument();
    
    // Check project details
    expect(screen.getByText('Development of the knowledge graph system for research integration')).toBeInTheDocument();
    expect(screen.getByText('in progress')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('displays error message when loading fails', async () => {
    // Mock the service to return an error
    collaborationService.getWorkspace.mockRejectedValue(new Error('Failed to fetch workspace'));
    
    render(
      <BrowserRouter>
        <WorkspaceDetail />
      </BrowserRouter>
    );
    
    // Wait for the error to appear
    await waitFor(() => {
      expect(screen.getByText(/failed to load workspace details/i)).toBeInTheDocument();
    });
  });
});