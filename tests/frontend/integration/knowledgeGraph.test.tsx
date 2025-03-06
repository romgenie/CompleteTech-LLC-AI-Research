/**
 * Tests for Knowledge Graph visualization
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import KnowledgeGraphPage from '../../../src/ui/frontend/src/pages/KnowledgeGraphPage';
import { getEntities, getRelationships } from '../../../src/ui/frontend/src/services/knowledgeGraphService';

// Mock D3 hooks
jest.mock('../../../src/ui/frontend/src/hooks/useD3', () => ({
  __esModule: true,
  default: jest.fn().mockImplementation(callback => {
    // Mock ref object
    const ref = { current: document.createElement('div') };
    // Execute the callback with the ref
    callback(ref);
    // Return the ref
    return ref;
  })
}));

// Mock the knowledge graph service
jest.mock('../../../src/ui/frontend/src/services/knowledgeGraphService', () => ({
  getEntities: jest.fn(),
  getRelationships: jest.fn()
}));

// Sample test data
const mockEntities = [
  { id: '1', name: 'GPT-4', type: 'MODEL', properties: { year: 2023 } },
  { id: '2', name: 'ImageNet', type: 'DATASET', properties: {} },
  { id: '3', name: 'Vision Transformer', type: 'MODEL', properties: { year: 2020 } }
];

const mockRelationships = [
  { 
    id: 'r1', 
    type: 'TRAINED_ON', 
    source_id: '1', 
    target_id: '2',
    source_entity: { id: '1', name: 'GPT-4', type: 'MODEL' },
    target_entity: { id: '2', name: 'ImageNet', type: 'DATASET' }
  },
  { 
    id: 'r2', 
    type: 'OUTPERFORMS', 
    source_id: '1', 
    target_id: '3',
    source_entity: { id: '1', name: 'GPT-4', type: 'MODEL' },
    target_entity: { id: '3', name: 'Vision Transformer', type: 'MODEL' }
  }
];

describe('Knowledge Graph Visualization', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock successful API responses
    (getEntities as jest.Mock).mockResolvedValue({ items: mockEntities, total: mockEntities.length });
    (getRelationships as jest.Mock).mockResolvedValue({ items: mockRelationships, total: mockRelationships.length });
  });

  test('renders knowledge graph page', async () => {
    render(
      <MemoryRouter>
        <KnowledgeGraphPage />
      </MemoryRouter>
    );

    // Check that the page title is rendered
    expect(screen.getByText(/knowledge graph/i)).toBeInTheDocument();

    // Wait for entities and relationships to load
    await waitFor(() => {
      // Verify API calls were made
      expect(getEntities).toHaveBeenCalled();
      expect(getRelationships).toHaveBeenCalled();
    });
  });

  test('displays entity list', async () => {
    render(
      <MemoryRouter>
        <KnowledgeGraphPage />
      </MemoryRouter>
    );

    // Wait for entities to load and be displayed
    await waitFor(() => {
      // Check for entity names in the list
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
      expect(screen.getByText('ImageNet')).toBeInTheDocument();
      expect(screen.getByText('Vision Transformer')).toBeInTheDocument();
    });
  });

  test('displays relationship list', async () => {
    render(
      <MemoryRouter>
        <KnowledgeGraphPage />
      </MemoryRouter>
    );

    // Wait for relationships to load and be displayed
    await waitFor(() => {
      // Check for relationship types
      expect(screen.getByText(/TRAINED_ON/i)).toBeInTheDocument();
      expect(screen.getByText(/OUTPERFORMS/i)).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    (getEntities as jest.Mock).mockRejectedValue(new Error('Failed to fetch entities'));
    
    render(
      <MemoryRouter>
        <KnowledgeGraphPage />
      </MemoryRouter>
    );

    // Wait for error message to be displayed
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch entities/i)).toBeInTheDocument();
    });
  });

  test('filters entities by type', async () => {
    render(
      <MemoryRouter>
        <KnowledgeGraphPage />
      </MemoryRouter>
    );

    // Wait for entities to load
    await waitFor(() => {
      expect(getEntities).toHaveBeenCalled();
    });

    // Find and click the MODEL filter
    const modelFilter = screen.getByText(/model/i).closest('button');
    if (modelFilter) {
      modelFilter.click();

      // Only model entities should be visible
      expect(screen.getByText('GPT-4')).toBeInTheDocument();
      expect(screen.getByText('Vision Transformer')).toBeInTheDocument();
      
      // DATASET entity should not be visible in filtered view
      expect(screen.queryByText('ImageNet')).not.toBeInTheDocument();
    }
  });
});