const collaborationService = {
  getWorkspaces: jest.fn(),
  getWorkspace: jest.fn(),
  createWorkspace: jest.fn(),
  updateWorkspace: jest.fn(),
  deleteWorkspace: jest.fn(),
  getProjects: jest.fn(),
  getWorkspaceMembers: jest.fn(),
  addWorkspaceMember: jest.fn(),
  removeWorkspaceMember: jest.fn(),
  updateWorkspaceMember: jest.fn(),
};

export default collaborationService;