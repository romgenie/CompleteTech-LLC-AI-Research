import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import CreateWorkspaceForm from '../CreateWorkspaceForm';
import collaborationService from '../../../services/collaborationService';

// Mock the navigation hook
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

// Mock the collaboration service
jest.mock('../../../services/collaborationService');

describe('CreateWorkspaceForm Component', () => {
  const mockCreatedWorkspace = {
    id: 'new-ws-id',
    name: 'New Test Workspace',
    description: 'This is a test workspace',
    visibility: 'internal',
    tags: ['Test', 'Workspace'],
    created_at: '2023-11-15T12:00:00Z',
    updated_at: '2023-11-15T12:00:00Z'
  };

  beforeEach(() => {
    // Reset mocks before each test
    jest.resetAllMocks();
    
    // Mock the createWorkspace method
    collaborationService.createWorkspace = jest.fn().mockResolvedValue(mockCreatedWorkspace);
  });

  it('renders form elements correctly', () => {
    render(
      <BrowserRouter>
        <CreateWorkspaceForm />
      </BrowserRouter>
    );
    
    // Check if form title is displayed
    expect(screen.getByText('Create New Workspace')).toBeInTheDocument();
    
    // Check if form fields are present
    expect(screen.getByLabelText(/Workspace Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    
    // Check if radio buttons for visibility are present
    expect(screen.getByLabelText(/Private/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Internal/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Public/i)).toBeInTheDocument();
    
    // Check if buttons are present
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Create Workspace')).toBeInTheDocument();
  });

  it('validates form fields correctly', async () => {
    render(
      <BrowserRouter>
        <CreateWorkspaceForm />
      </BrowserRouter>
    );
    
    // Try to submit without filling required fields
    const submitButton = screen.getByText('Create Workspace');
    
    // Submit button should be disabled initially
    expect(submitButton).toBeDisabled();
    
    // Fill in workspace name only
    await userEvent.type(screen.getByLabelText(/Workspace Name/i), 'Test Workspace');
    
    // Submit button should still be disabled
    expect(submitButton).toBeDisabled();
    
    // Fill in description as well
    await userEvent.type(screen.getByLabelText(/Description/i), 'This is a test workspace description');
    
    // Now submit button should be enabled
    expect(submitButton).not.toBeDisabled();
  });

  it('handles tag input correctly', async () => {
    render(
      <BrowserRouter>
        <CreateWorkspaceForm />
      </BrowserRouter>
    );
    
    // Initial state should show no tags
    expect(screen.getByText('No tags added yet')).toBeInTheDocument();
    
    // Add a tag
    const tagInput = screen.getByPlaceholderText('Add a tag and press Enter');
    await userEvent.type(tagInput, 'TestTag{enter}');
    
    // Check if tag is displayed
    expect(screen.getByText('TestTag')).toBeInTheDocument();
    expect(screen.queryByText('No tags added yet')).not.toBeInTheDocument();
    
    // Add another tag
    await userEvent.type(tagInput, 'AnotherTag{enter}');
    
    // Check if both tags are displayed
    expect(screen.getByText('TestTag')).toBeInTheDocument();
    expect(screen.getByText('AnotherTag')).toBeInTheDocument();
    
    // Delete a tag
    const deleteButtons = screen.getAllByRole('button');
    const deleteTagButton = Array.from(deleteButtons).find(
      button => button.parentElement && button.parentElement.textContent === 'TestTag'
    );
    fireEvent.click(deleteTagButton);
    
    // Check if tag is deleted
    expect(screen.queryByText('TestTag')).not.toBeInTheDocument();
    expect(screen.getByText('AnotherTag')).toBeInTheDocument();
  });

  it('submits form data correctly', async () => {
    render(
      <BrowserRouter>
        <CreateWorkspaceForm />
      </BrowserRouter>
    );
    
    // Fill in workspace name
    await userEvent.type(screen.getByLabelText(/Workspace Name/i), 'Test Workspace');
    
    // Fill in description
    await userEvent.type(screen.getByLabelText(/Description/i), 'This is a test workspace description');
    
    // Change visibility
    await userEvent.click(screen.getByLabelText(/Public/i));
    
    // Add tags
    const tagInput = screen.getByPlaceholderText('Add a tag and press Enter');
    await userEvent.type(tagInput, 'Tag1{enter}');
    await userEvent.type(tagInput, 'Tag2{enter}');
    
    // Submit the form
    await userEvent.click(screen.getByText('Create Workspace'));
    
    // Check if service was called with correct data
    expect(collaborationService.createWorkspace).toHaveBeenCalledWith({
      name: 'Test Workspace',
      description: 'This is a test workspace description',
      visibility: 'public',
      tags: ['Tag1', 'Tag2']
    });
    
    // Check if success message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Workspace created successfully/i)).toBeInTheDocument();
    });
  });

  it('handles form submission errors', async () => {
    // Mock the service to return an error
    collaborationService.createWorkspace.mockRejectedValue(new Error('Failed to create workspace'));
    
    render(
      <BrowserRouter>
        <CreateWorkspaceForm />
      </BrowserRouter>
    );
    
    // Fill in required fields
    await userEvent.type(screen.getByLabelText(/Workspace Name/i), 'Test Workspace');
    await userEvent.type(screen.getByLabelText(/Description/i), 'This is a description');
    
    // Submit the form
    await userEvent.click(screen.getByText('Create Workspace'));
    
    // Check if error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Failed to create workspace/i)).toBeInTheDocument();
    });
  });
});