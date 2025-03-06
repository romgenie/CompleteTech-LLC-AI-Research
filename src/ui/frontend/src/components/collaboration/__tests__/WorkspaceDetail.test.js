import React from 'react';
import { render, screen, waitFor } from '../../../test-utils';
import WorkspaceDetail from '../WorkspaceDetail';
import collaborationService from '../../../services/collaborationService';

// Mock the collaboration service
jest.mock('../../../services/collaborationService');

// Mock react-router-dom's useParams
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ workspaceId: 'ws1' })
}));

describe('WorkspaceDetail Component', () => {
  const mockWorkspace = {
    id: 'ws1',
    name: 'AI Research Integration',
    description: 'Collaborative workspace for AI research',
    visibility: 'internal',
    tags: ['AI', 'Research'],
    created_at: '2023-10-15T10:30:00Z',
    updated_at: '2023-11-10T14:22:00Z'
  };

  const mockProjects = [
    {
      id: 'proj1',
      name: 'Knowledge Graph System',
      description: 'Development of the knowledge graph system',
      status: 'in_progress',
      contributors: 5
    }
  ];

  const mockMembers = [
    {
      id: 'user1',
      name: 'John Doe',
      role: 'Admin',
      avatar: 'JD'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    collaborationService.getWorkspace.mockResolvedValue(mockWorkspace);
    collaborationService.getProjects.mockResolvedValue(mockProjects);
    collaborationService.getWorkspaceMembers.mockResolvedValue(mockMembers);
  });

  it('shows loading state initially', () => {
    render(<WorkspaceDetail />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays workspace details after loading', async () => {
    render(<WorkspaceDetail />);

    await waitFor(() => {
      expect(screen.getByText(mockWorkspace.name)).toBeInTheDocument();
      expect(screen.getByText(mockWorkspace.description)).toBeInTheDocument();
      mockWorkspace.tags.forEach(tag => {
        expect(screen.getByText(tag)).toBeInTheDocument();
      });
    });
  });

  it('displays projects tab content', async () => {
    render(<WorkspaceDetail />);

    await waitFor(() => {
      expect(screen.getByText(mockProjects[0].name)).toBeInTheDocument();
      expect(screen.getByText(mockProjects[0].description)).toBeInTheDocument();
      expect(screen.getByText(`${mockProjects[0].contributors} contributors`)).toBeInTheDocument();
    });
  });

  it('displays members tab content', async () => {
    render(<WorkspaceDetail />);

    // Click on the Members tab
    const membersTab = await screen.findByText(/members/i);
    membersTab.click();

    await waitFor(() => {
      expect(screen.getByText(mockMembers[0].name)).toBeInTheDocument();
      expect(screen.getByText(mockMembers[0].role)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const errorMessage = 'Failed to load workspace details';
    collaborationService.getWorkspace.mockRejectedValue(new Error(errorMessage));

    render(<WorkspaceDetail />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load workspace details/i)).toBeInTheDocument();
    });
  });
});