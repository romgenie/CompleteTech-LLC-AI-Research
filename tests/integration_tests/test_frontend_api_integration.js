"""
Integration test for frontend components interacting with the API.

This test validates the correct interaction between:
1. Frontend React components
2. API client services
3. Backend API endpoints

The test uses React Testing Library to simulate user interactions,
MSW (Mock Service Worker) to intercept API calls, and Jest for assertions.
"""

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'
import { rest } from 'msw'
import { MemoryRouter } from 'react-router-dom'

// Import frontend components to test
import ResearchPage from '../../src/ui/frontend/src/pages/ResearchPage'
import KnowledgeGraphPage from '../../src/ui/frontend/src/pages/KnowledgeGraphPage'
import ImplementationPage from '../../src/ui/frontend/src/pages/ImplementationPage'
import { AuthProvider } from '../../src/ui/frontend/src/contexts/AuthContext'

// Mock API responses
const mockResearchResponse = {
  id: 'research_123',
  title: 'Vision Transformers',
  query: 'How do Vision Transformers work?',
  content: 'Vision Transformers (ViT) apply the transformer architecture to image processing...',
  created_at: '2023-08-15T10:30:00Z'
}

const mockEntitiesResponse = [
  { id: '1', name: 'Vision Transformer', type: 'MODEL' },
  { id: '2', name: 'ImageNet', type: 'DATASET' },
  { id: '3', name: 'Transformer', type: 'ARCHITECTURE' }
]

const mockRelationshipsResponse = [
  {
    source: { id: '1', name: 'Vision Transformer' },
    target: { id: '2', name: 'ImageNet' },
    relationship: { type: 'EVALUATED_ON', properties: { accuracy: 0.885 } }
  },
  {
    source: { id: '1', name: 'Vision Transformer' },
    target: { id: '3', name: 'Transformer' },
    relationship: { type: 'BASED_ON', properties: {} }
  }
]

const mockImplementationResponse = {
  id: 'implementation_123',
  title: 'ViT Implementation',
  model_id: '1',
  code: 'import torch\nfrom torch import nn\n\nclass VisionTransformer(nn.Module):\n    def __init__(self):\n        super().__init__()\n        # Implementation details...',
  description: 'Implementation of Vision Transformer using PyTorch'
}

// Setup MSW server to intercept API requests
const server = setupServer(
  // Research endpoints
  rest.get('/api/research/:id', (req, res, ctx) => {
    return res(ctx.json(mockResearchResponse))
  }),
  rest.post('/api/research', (req, res, ctx) => {
    return res(ctx.status(201), ctx.json({ id: 'research_123', ...req.body }))
  }),
  
  // Knowledge Graph endpoints
  rest.get('/api/knowledge-graph/entities', (req, res, ctx) => {
    return res(ctx.json(mockEntitiesResponse))
  }),
  rest.get('/api/knowledge-graph/relationships', (req, res, ctx) => {
    return res(ctx.json(mockRelationshipsResponse))
  }),
  
  // Implementation endpoints
  rest.get('/api/implementation/:id', (req, res, ctx) => {
    return res(ctx.json(mockImplementationResponse))
  }),
  rest.post('/api/implementation', (req, res, ctx) => {
    return res(ctx.status(201), ctx.json({ id: 'implementation_123', ...req.body }))
  })
)

// Start server before tests
beforeAll(() => server.listen())
// Reset after each test
afterEach(() => server.resetHandlers())
// Clean up after all tests
afterAll(() => server.close())

// Mock the D3 visualization to avoid DOM manipulation in tests
jest.mock('../../src/ui/frontend/src/components/KnowledgeGraphVisualization', () => {
  return {
    __esModule: true,
    default: () => <div data-testid="graph-visualization">Graph Visualization</div>
  }
})

// Test the Research page
describe('ResearchPage', () => {
  test('submits research query and displays results', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <ResearchPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Fill the research form
    fireEvent.change(screen.getByLabelText(/research query/i), {
      target: { value: 'How do Vision Transformers work?' }
    })
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /submit/i }))
    
    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText(/Vision Transformers \(ViT\) apply/i)).toBeInTheDocument()
    })
    
    // Verify the response is displayed correctly
    expect(screen.getByText(/Vision Transformers/i)).toBeInTheDocument()
  })
  
  test('handles API errors gracefully', async () => {
    // Override server response for this test
    server.use(
      rest.post('/api/research', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: 'Internal server error' }))
      })
    )
    
    render(
      <MemoryRouter>
        <AuthProvider>
          <ResearchPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Fill the form
    fireEvent.change(screen.getByLabelText(/research query/i), {
      target: { value: 'How do Vision Transformers work?' }
    })
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /submit/i }))
    
    // Verify error is handled and displayed
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })
  })
})

// Test the Knowledge Graph page
describe('KnowledgeGraphPage', () => {
  test('loads and displays graph data', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <KnowledgeGraphPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Wait for entities to load
    await waitFor(() => {
      expect(screen.getByText(/Vision Transformer/i)).toBeInTheDocument()
    })
    
    // Check that the graph visualization is rendered
    expect(screen.getByTestId('graph-visualization')).toBeInTheDocument()
    
    // Verify entity list is displayed
    expect(screen.getByText(/ImageNet/i)).toBeInTheDocument()
    expect(screen.getByText(/Transformer/i)).toBeInTheDocument()
  })
  
  test('filters graph data by entity type', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <KnowledgeGraphPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Wait for entities to load
    await waitFor(() => {
      expect(screen.getByText(/Vision Transformer/i)).toBeInTheDocument()
    })
    
    // Find and click the MODEL filter
    const filterButton = screen.getByRole('button', { name: /filter/i })
    fireEvent.click(filterButton)
    
    // Select MODEL type
    const modelOption = screen.getByText(/model/i)
    fireEvent.click(modelOption)
    
    // Apply filter
    const applyButton = screen.getByRole('button', { name: /apply/i })
    fireEvent.click(applyButton)
    
    // Verify only MODEL entities are shown
    await waitFor(() => {
      expect(screen.getByText(/Vision Transformer/i)).toBeInTheDocument()
      // ImageNet should be filtered out as it's a DATASET
      expect(screen.queryByText(/ImageNet/i)).not.toBeInTheDocument()
    })
  })
})

// Test the Implementation page
describe('ImplementationPage', () => {
  test('creates new implementation project', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <ImplementationPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Click "New Project" button
    fireEvent.click(screen.getByRole('button', { name: /new project/i }))
    
    // Fill the implementation form
    fireEvent.change(screen.getByLabelText(/project title/i), {
      target: { value: 'New ViT Implementation' }
    })
    
    // Select the research source (model)
    fireEvent.change(screen.getByLabelText(/select model/i), {
      target: { value: '1' } // Vision Transformer ID
    })
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /create/i }))
    
    // Wait for redirect to new implementation
    await waitFor(() => {
      expect(screen.getByText(/implementation details/i)).toBeInTheDocument()
    })
    
    // Verify code editor is populated
    expect(screen.getByText(/class VisionTransformer/i)).toBeInTheDocument()
  })
  
  test('loads existing implementation details', async () => {
    render(
      <MemoryRouter initialEntries={['/implementation/implementation_123']}>
        <AuthProvider>
          <ImplementationPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Wait for implementation to load
    await waitFor(() => {
      expect(screen.getByText(/ViT Implementation/i)).toBeInTheDocument()
    })
    
    // Verify code is displayed
    expect(screen.getByText(/import torch/i)).toBeInTheDocument()
    expect(screen.getByText(/class VisionTransformer/i)).toBeInTheDocument()
  })
})

// Test the integration between pages
describe('Cross-page integration', () => {
  test('research results can be used to create implementation', async () => {
    // Render Research page first
    const { unmount } = render(
      <MemoryRouter>
        <AuthProvider>
          <ResearchPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Fill the research form
    fireEvent.change(screen.getByLabelText(/research query/i), {
      target: { value: 'How do Vision Transformers work?' }
    })
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /submit/i }))
    
    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText(/Vision Transformers \(ViT\) apply/i)).toBeInTheDocument()
    })
    
    // Click "Implement" button
    fireEvent.click(screen.getByRole('button', { name: /implement/i }))
    
    // Clean up
    unmount()
    
    // Render Implementation page (simulating navigation)
    render(
      <MemoryRouter initialEntries={['/implementation/new?research=research_123']}>
        <AuthProvider>
          <ImplementationPage />
        </AuthProvider>
      </MemoryRouter>
    )
    
    // Verify research data is loaded into implementation form
    await waitFor(() => {
      expect(screen.getByDisplayValue(/Vision Transformers/i)).toBeInTheDocument()
    })
    
    // Verify models from the research are available for selection
    expect(screen.getByText(/Vision Transformer/i)).toBeInTheDocument()
  })
})