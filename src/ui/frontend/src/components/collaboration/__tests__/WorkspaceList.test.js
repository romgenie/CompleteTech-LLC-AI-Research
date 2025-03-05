import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../test-utils';
import userEvent from '@testing-library/user-event';
import WorkspaceList from '../WorkspaceList';
import collaborationService from '../../../services/collaborationService';

// Mock the collaboration service
jest.mock('../../../services/collaborationService');

describe('WorkspaceList Component', () => {
  const mockWorkspaces = [
    {
      id: 'ws1',
      name: 'AI Research Integration',
      description: 'Main research workspace',
      visibility: 'internal',
      members_count: 5,
      projects_count: 3,
      updated_at: '2023-11-10T14:22:00Z'
    },
    {
      id: 'ws2',
      name: 'Knowledge Graph System',
      description: 'Knowledge graph development',
      visibility: 'private',
      members_count: 3,
      projects_count: 2,
      updated_at: '2023-11-09T10:15:00Z'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    collaborationService.getWorkspaces.mockResolvedValue(mockWorkspaces);
  });

  it('renders loading state initially', () => {
    render(<WorkspaceList />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays workspaces after loading', async () => {
    render(<WorkspaceList />);

    await waitFor(() => {
      mockWorkspaces.forEach(workspace => {
        expect(screen.getByText(workspace.name)).toBeInTheDocument();
      });
    });
  });

  it('filters workspaces by search query', async () => {
    render(<WorkspaceList />);

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search workspaces/i);
    await userEvent.type(searchInput, 'graph');

    expect(screen.queryByText('AI Research Integration')).not.toBeInTheDocument();
    expect(screen.getByText('Knowledge Graph System')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    const errorMessage = 'Failed to load workspaces';
    collaborationService.getWorkspaces.mockRejectedValue(new Error(errorMessage));

    render(<WorkspaceList />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load workspaces/i)).toBeInTheDocument();
    });
  });
});