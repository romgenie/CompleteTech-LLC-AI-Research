import React from 'react';
import { render, screen, fireEvent, waitFor, cleanup } from '../../../test-utils';
import userEvent from '@testing-library/user-event';
import CreateWorkspaceForm from '../CreateWorkspaceForm';
import collaborationService from '../../../services/collaborationService';

// Mock the collaboration service and router
jest.mock('../../../services/collaborationService');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

describe('CreateWorkspaceForm Component', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    collaborationService.createWorkspace.mockResolvedValue({ 
      id: 'new-workspace-1'
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('renders the form with all required fields', () => {
    render(<CreateWorkspaceForm />);
    
    expect(screen.getByLabelText(/workspace name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/visibility/i)).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<CreateWorkspaceForm />);
    
    const submitButton = screen.getByText(/create workspace/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(collaborationService.createWorkspace).not.toHaveBeenCalled();
    });
  }, 5000);

  it('submits the form with valid data', async () => {
    render(<CreateWorkspaceForm />);
    
    const nameInput = screen.getByLabelText(/workspace name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    
    await userEvent.type(nameInput, 'Test Workspace');
    await userEvent.type(descriptionInput, 'Test Description');

    const submitButton = screen.getByText(/create workspace/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(collaborationService.createWorkspace).toHaveBeenCalledWith({
        name: 'Test Workspace',
        description: 'Test Description',
        visibility: 'private',
        tags: []
      });
    }, { timeout: 3000 });
  }, 5000);

  it('shows success message after successful submission', async () => {
    render(<CreateWorkspaceForm />);
    
    const nameInput = screen.getByLabelText(/workspace name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    
    await userEvent.type(nameInput, 'Test Workspace');
    await userEvent.type(descriptionInput, 'Test Description');

    const submitButton = screen.getByText(/create workspace/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/workspace created successfully/i)).toBeInTheDocument();
    }, { timeout: 3000 });
  }, 5000);

  it('handles API errors gracefully', async () => {
    const errorMessage = 'Failed to create workspace';
    collaborationService.createWorkspace.mockRejectedValue(new Error(errorMessage));

    render(<CreateWorkspaceForm />);
    
    const nameInput = screen.getByLabelText(/workspace name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    
    await userEvent.type(nameInput, 'Test Workspace');
    await userEvent.type(descriptionInput, 'Test Description');

    const submitButton = screen.getByText(/create workspace/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    }, { timeout: 3000 });
  }, 5000);
});