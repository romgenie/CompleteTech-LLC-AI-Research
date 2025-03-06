/**
 * Mock data for development testing
 */

// Knowledge Graph mock data
const knowledgeGraph = {
  entities: [
    { id: "entity-1", name: "GPT-4", type: "MODEL" },
    { id: "entity-2", name: "ImageNet", type: "DATASET" },
    { id: "entity-3", name: "Transformer", type: "ALGORITHM" }
  ],
  relationships: [
    { id: "rel-1", source: "entity-1", target: "entity-2", type: "TRAINED_ON" },
    { id: "rel-2", source: "entity-1", target: "entity-3", type: "IMPLEMENTS" }
  ],
  stats: {
    entityCount: 3,
    relationshipCount: 2,
    entityTypes: ["MODEL", "DATASET", "ALGORITHM"],
    relationshipTypes: ["TRAINED_ON", "IMPLEMENTS"]
  }
};

// Research results mock data
const researchResults = {
  query: "Recent advances in large language models",
  summary: "Large language models have seen significant advances in the past year.",
  sources: [
    {
      title: "Scaling Language Models",
      authors: ["Author 1", "Author 2"],
      journal: "arXiv",
      year: "2023",
      url: "https://example.com"
    }
  ],
  keyFindings: ["Finding 1", "Finding 2"],
  relatedTopics: ["Topic 1", "Topic 2"],
  generatedAt: new Date().toISOString()
};

// Implementation mock data
const implementation = {
  paper: {
    title: "Attention Is All You Need",
    authors: ["Author 1", "Author 2"],
    abstract: "Abstract",
    year: "2017",
    url: "https://example.com",
    citations: 1000
  },
  implementation: {
    status: "complete",
    completedAt: new Date().toISOString(),
    files: [
      {
        name: "transformer.py",
        description: "Main Transformer model implementation",
        lines: 450
      }
    ],
    stats: {
      totalLines: 450,
      complexity: "Medium",
      estimatedTime: "3-4 hours",
      requirementsCount: 5
    },
    sampleCode: "import torch\nimport torch.nn as nn\n\ndef sample_function():\n    return 'Hello World'"
  }
};

// Papers mock data
const papers = [
  {
    id: "paper-1",
    title: "Attention Is All You Need",
    authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    year: 2023,
    url: "https://example.com",
    abstract: "Abstract",
    status: "uploaded",
    uploaded_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "paper-2",
    title: "BERT: Pre-training of Deep Bidirectional Transformers",
    authors: ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee"],
    year: 2022,
    url: "https://example.com",
    abstract: "Abstract",
    status: "analyzed",
    uploaded_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

/**
 * Main mock data export
 */
module.exports = {
  knowledgeGraph,
  researchResults,
  implementation,
  papers
};
