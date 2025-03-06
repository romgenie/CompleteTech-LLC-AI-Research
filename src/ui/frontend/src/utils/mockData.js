/**
 * Mock data utilities for the application
 * Provides fallback data when backend services are unavailable
 */

/**
 * Generate random entities for knowledge graph visualization
 * @param {number} count - Number of entities to generate
 * @returns {Array} - Array of entity objects
 */
export const generateMockEntities = (count = 20) => {
  const entityTypes = ['MODEL', 'DATASET', 'PAPER', 'AUTHOR', 'ALGORITHM', 'FRAMEWORK', 'METRIC'];
  const models = ['GPT-4', 'LLaMA', 'BERT', 'T5', 'Falcon', 'CLIP', 'Claude', 'Mistral', 'Gemini'];
  const datasets = ['ImageNet', 'MNIST', 'CIFAR-10', 'MS-COCO', 'WikiText', 'SQuAD', 'GLUE', 'C4'];
  const algorithms = ['Transformer', 'ResNet', 'LSTM', 'GAN', 'Diffusion', 'MoE', 'RL', 'Attention'];
  const frameworks = ['PyTorch', 'TensorFlow', 'JAX', 'Keras', 'Hugging Face', 'MXNet', 'FastAI'];
  const authors = ['Hinton', 'LeCun', 'Bengio', 'Sutskever', 'Dean', 'Ng', 'Schmidhuber', 'Goodfellow'];
  
  const entities = [];
  
  for (let i = 0; i < count; i++) {
    const typeIndex = Math.floor(Math.random() * entityTypes.length);
    const type = entityTypes[typeIndex];
    
    let name;
    switch (type) {
      case 'MODEL':
        name = models[Math.floor(Math.random() * models.length)];
        break;
      case 'DATASET':
        name = datasets[Math.floor(Math.random() * datasets.length)];
        break;
      case 'ALGORITHM':
        name = algorithms[Math.floor(Math.random() * algorithms.length)];
        break;
      case 'FRAMEWORK':
        name = frameworks[Math.floor(Math.random() * frameworks.length)];
        break;
      case 'AUTHOR':
        name = authors[Math.floor(Math.random() * authors.length)];
        break;
      default:
        name = `Entity ${i}`;
    }
    
    entities.push({
      id: `entity-${i}`,
      name,
      type,
      properties: {
        description: `This is a mock ${type.toLowerCase()}`,
        year: 2020 + Math.floor(Math.random() * 5),
        confidence: Math.random().toFixed(2)
      }
    });
  }
  
  return entities;
};

/**
 * Generate mock relationships between entities
 * @param {Array} entities - Array of entity objects
 * @param {number} count - Number of relationships to generate
 * @returns {Array} - Array of relationship objects
 */
export const generateMockRelationships = (entities, count = 30) => {
  const relationshipTypes = [
    'TRAINED_ON', 'CITES', 'AUTHORED_BY', 'IMPLEMENTS', 'BASED_ON', 
    'OUTPERFORMS', 'USES', 'EVALUATED_ON', 'PART_OF', 'DEVELOPED_BY'
  ];
  
  const relationships = [];
  
  for (let i = 0; i < count; i++) {
    const sourceIndex = Math.floor(Math.random() * entities.length);
    let targetIndex;
    
    // Ensure target is different from source
    do {
      targetIndex = Math.floor(Math.random() * entities.length);
    } while (targetIndex === sourceIndex);
    
    const relationshipType = relationshipTypes[Math.floor(Math.random() * relationshipTypes.length)];
    
    relationships.push({
      id: `relationship-${i}`,
      source: entities[sourceIndex].id,
      target: entities[targetIndex].id,
      type: relationshipType,
      properties: {
        confidence: Math.random().toFixed(2),
        year: 2020 + Math.floor(Math.random() * 5)
      }
    });
  }
  
  return relationships;
};

/**
 * Generate a mock knowledge graph
 * @param {number} entityCount - Number of entities
 * @param {number} relationshipCount - Number of relationships
 * @returns {Object} - Knowledge graph object with entities and relationships
 */
export const generateMockKnowledgeGraph = (entityCount = 20, relationshipCount = 30) => {
  const entities = generateMockEntities(entityCount);
  const relationships = generateMockRelationships(entities, relationshipCount);
  
  return {
    entities,
    relationships
  };
};

/**
 * Generate mock research results
 * @returns {Object} - Research results object
 */
export const generateMockResearchResults = () => {
  return {
    query: "Recent advances in large language models",
    summary: "Large language models have seen significant advances in the past year, with models like GPT-4, Claude, and LLaMA pushing the boundaries of natural language understanding and generation. Key improvements include increased context length, multimodal capabilities, and better reasoning. These models are being applied across various domains including scientific research, content creation, and programming assistance.",
    sources: [
      {
        title: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher",
        authors: ["Jack W. Rae", "Sebastian Borgeaud", "et al."],
        url: "https://arxiv.org/abs/2112.11446",
        year: 2022,
        confidence: 0.95
      },
      {
        title: "Training language models to follow instructions with human feedback",
        authors: ["Long Ouyang", "Jeff Wu", "et al."],
        url: "https://arxiv.org/abs/2203.02155",
        year: 2022,
        confidence: 0.92
      },
      {
        title: "LLaMA: Open and Efficient Foundation Language Models",
        authors: ["Hugo Touvron", "Thibaut Lavril", "et al."],
        url: "https://arxiv.org/abs/2302.13971",
        year: 2023,
        confidence: 0.98
      }
    ],
    sections: [
      {
        title: "Introduction",
        content: "Large language models (LLMs) have emerged as powerful tools for natural language processing tasks. Recent advances have focused on scaling model size, improving training methodologies, and enhancing inference capabilities. This report examines key developments in the field over the past year."
      },
      {
        title: "Scaling Trends",
        content: "The trend of scaling language models continues, with models reaching trillions of parameters. However, research also shows that efficient scaling with high-quality data and architectural improvements can yield comparable performance with smaller models. Mixture of Experts (MoE) architectures have gained popularity for creating computationally efficient large models."
      },
      {
        title: "Training Methodologies",
        content: "Reinforcement Learning from Human Feedback (RLHF) has become a standard approach for aligning language models with human preferences. Constitutional AI methods aim to improve safety without relying on human feedback for every scenario. Continued pre-training and instruction tuning remain effective for adapting models to specific domains."
      },
      {
        title: "Multimodal Capabilities",
        content: "Recent models have expanded beyond text to include image understanding, audio processing, and even video analysis. Vision-language models like GPT-4V and Claude 3 Opus can analyze complex images and reason about visual content. These capabilities enable new applications in document understanding, visual reasoning, and multimodal content generation."
      },
      {
        title: "Reasoning and Tool Use",
        content: "LLMs have demonstrated improved reasoning capabilities through techniques like chain-of-thought prompting and self-consistency. Models can now use external tools, such as calculators, web browsers, and code interpreters, extending their capabilities beyond their trained knowledge. This represents a shift toward LLMs as orchestrators of other specialized systems."
      }
    ],
    relatedTopics: [
      "RLHF techniques",
      "Mixture of Experts architecture",
      "Multimodal language models",
      "Tool use in LLMs",
      "Alignment and safety research"
    ],
    entityGraph: generateMockKnowledgeGraph(10, 15)
  };
};

/**
 * Generate mock paper implementation data
 * @returns {Object} - Paper implementation object
 */
export const generateMockImplementation = () => {
  return {
    paper: {
      title: "Attention Is All You Need",
      authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Łukasz Kaiser", "Illia Polosukhin"],
      abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
      year: 2017,
      url: "https://arxiv.org/abs/1706.03762",
      status: "Implemented"
    },
    implementation: {
      language: "Python",
      framework: "PyTorch",
      files: [
        {
          name: "transformer.py",
          description: "Core implementation of the Transformer architecture",
          lines: 320
        },
        {
          name: "attention.py",
          description: "Multi-head attention mechanism implementation",
          lines: 150
        },
        {
          name: "model.py",
          description: "Full model with encoder and decoder stacks",
          lines: 280
        },
        {
          name: "train.py",
          description: "Training script with optimizer and learning rate scheduler",
          lines: 200
        },
        {
          name: "utils.py",
          description: "Utility functions for data processing and evaluation",
          lines: 175
        }
      ],
      stats: {
        totalLines: 1125,
        complexity: "Medium",
        estimatedTime: "3-4 hours",
        requirementsCount: 5
      },
      sampleCode: "import torch\nimport torch.nn as nn\nimport math\n\nclass MultiHeadAttention(nn.Module):\n    def __init__(self, d_model, num_heads):\n        super(MultiHeadAttention, self).__init__()\n        assert d_model % num_heads == 0"
    }
  };
};

/**
 * Generate mock papers data
 * @param {number} count - Number of papers to generate
 * @returns {Array} - Array of paper objects
 */
export const generateMockPapers = (count = 10) => {
  const paperTitles = [
    "Attention Is All You Need",
    "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    "GPT-3: Language Models are Few-Shot Learners",
    "Deep Residual Learning for Image Recognition",
    "Adam: A Method for Stochastic Optimization",
    "Dropout: A Simple Way to Prevent Neural Networks from Overfitting",
    "ImageNet Classification with Deep Convolutional Neural Networks",
    "Very Deep Convolutional Networks for Large-Scale Image Recognition",
    "Sequence to Sequence Learning with Neural Networks",
    "Generative Adversarial Networks",
    "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift",
    "DALL·E: Creating Images from Text",
    "Transformers: State-of-the-Art Natural Language Processing"
  ];
  
  const authors = [
    ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
    ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
    ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
    ["Diederik P. Kingma", "Jimmy Ba"],
    ["Nitish Srivastava", "Geoffrey Hinton", "Alex Krizhevsky"],
    ["Alex Krizhevsky", "Ilya Sutskever", "Geoffrey E. Hinton"],
    ["Karen Simonyan", "Andrew Zisserman"],
    ["Ilya Sutskever", "Oriol Vinyals", "Quoc V. Le"],
    ["Ian J. Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza"],
    ["Sergey Ioffe", "Christian Szegedy"],
    ["Aditya Ramesh", "Mikhail Pavlov", "Gabriel Goh"],
    ["Thomas Wolf", "Lysandre Debut", "Victor Sanh"]
  ];
  
  const paperStatuses = [
    "uploaded",
    "queued",
    "processing",
    "extracting_entities",
    "extracting_relationships",
    "building_knowledge_graph",
    "analyzed",
    "implementation_ready",
    "implemented"
  ];
  
  const papers = [];
  
  for (let i = 0; i < count; i++) {
    const titleIndex = i % paperTitles.length;
    const authorIndex = i % authors.length;
    const statusIndex = Math.floor(Math.random() * paperStatuses.length);
    
    papers.push({
      id: "paper-" + i,
      title: paperTitles[titleIndex],
      authors: authors[authorIndex],
      year: 2015 + Math.floor(Math.random() * 8),
      url: "https://arxiv.org/abs/1234." + (5678 + i),
      abstract: "This is a mock abstract for a research paper...",
      status: paperStatuses[statusIndex],
      uploaded_at: new Date(Date.now() - Math.random() * 10000000000).toISOString(),
      updated_at: new Date(Date.now() - Math.random() * 1000000000).toISOString()
    });
  }
  
  return papers;
};

/**
 * Main mock data export
 */
export const mockData = {
  knowledgeGraph: generateMockKnowledgeGraph(),
  researchResults: generateMockResearchResults(),
  implementation: generateMockImplementation(),
  papers: generateMockPapers()
};

export default mockData;