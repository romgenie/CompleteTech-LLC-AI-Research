import axios from 'axios';

// Create axios instance for research implementation API
const implementationApi = axios.create({
  baseURL: '/implementation',
});

// Add request interceptor to add authentication token
implementationApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Note: Paper processing pipeline is planned for Phase 3.5 implementation.
// Papers will remain in "uploaded" status until the processing pipeline is implemented.
// Implementation requests are still possible but require manual paper information entry.

/**
 * Implementation service for interacting with the research implementation API.
 */
// Add methods needed by ImplementationPage
const implementationService = {
  /**
   * Get all implementation projects
   * 
   * @returns {Promise<Array>} - List of implementation projects
   */
  getAllProjects: async () => {
    try {
      const response = await implementationApi.get('/projects');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching implementation projects:', error);
      return [];
    }
  },

  /**
   * Get project files
   * 
   * @param {string} projectId - Project ID
   * @returns {Promise<Array>} - List of project files
   */
  getProjectFiles: async (projectId) => {
    try {
      const response = await implementationApi.get(`/projects/${projectId}/files`);
      return response.data || [];
    } catch (error) {
      console.error(`Error fetching files for project ${projectId}:`, error);
      return [];
    }
  },

  /**
   * Get file content
   * 
   * @param {string} fileId - File ID
   * @returns {Promise<Object>} - File content
   */
  getFileContent: async (fileId) => {
    try {
      const response = await implementationApi.get(`/files/${fileId}/content`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching content for file ${fileId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new implementation project
   * 
   * @param {string} paperUrl - URL to research paper
   * @returns {Promise<Object>} - Created project
   */
  createProject: async (paperUrl) => {
    try {
      const response = await implementationApi.post('/projects', { paperUrl });
      return response.data;
    } catch (error) {
      console.error('Error creating implementation project:', error);
      
      // Fall back to mock data if API fails
      // Create a new mock project based on the URL
      const mockProjects = implementationService.getMockProjects();
      const newProject = {
        id: `p${mockProjects.length + 1}`,
        title: `Implementation of ${paperUrl.split('/').pop()}`,
        status: "IN_PROGRESS",
        createdAt: new Date().toISOString(),
        currentStep: 0,
        repositoryUrl: null,
        paperAnalysis: {
          title: `Paper ${paperUrl.split('/').pop()}`,
          authors: "Authors to be determined",
          publication: "Publication to be determined",
          year: new Date().getFullYear().toString(),
          keywords: ["AI", "Research", "Implementation"],
          url: paperUrl,
          abstract: "Abstract will be available once the paper is processed.",
          contributions: [
            "Contributions will be available once the paper is analyzed."
          ]
        }
      };
      
      return newProject;
    }
  },

  /**
   * Run tests for an implementation project
   * 
   * @param {string} projectId - Project ID
   * @returns {Promise<Object>} - Test results
   */
  runTests: async (projectId) => {
    try {
      const response = await implementationApi.post(`/projects/${projectId}/tests`);
      return response.data;
    } catch (error) {
      console.error(`Error running tests for project ${projectId}:`, error);
      throw error;
    }
  },

  /**
   * Continue implementation process
   * 
   * @param {string} projectId - Project ID
   * @returns {Promise<Object>} - Updated project
   */
  continueImplementation: async (projectId) => {
    try {
      const response = await implementationApi.post(`/projects/${projectId}/continue`);
      return response.data;
    } catch (error) {
      console.error(`Error continuing implementation for project ${projectId}:`, error);
      throw error;
    }
  },

  /**
   * Generate mock implementation projects
   * 
   * @returns {Array} - Mock implementation projects
   */
  getMockProjects: () => {
    return [
      {
        id: "p1",
        title: "Implementation of Vision Transformer (ViT)",
        status: "IN_PROGRESS",
        createdAt: "2025-02-15T10:30:00Z",
        currentStep: 2,
        repositoryUrl: "https://github.com/example/vision-transformer-impl",
        paperAnalysis: {
          title: "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
          authors: "Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, et al.",
          publication: "ICLR 2021",
          year: "2021",
          keywords: ["Computer Vision", "Transformer", "Image Classification", "Attention"],
          url: "https://arxiv.org/abs/2010.11929",
          abstract: "While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. In vision, attention is either applied in conjunction with convolutional networks, or used to replace certain components of convolutional networks while keeping their overall structure in place. We show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks. When pre-trained on large amounts of data and transferred to multiple mid-sized or small image recognition benchmarks (ImageNet, CIFAR-100, VTAB, etc.), Vision Transformer (ViT) attains excellent results compared to state-of-the-art convolutional networks while requiring substantially fewer computational resources to train.",
          contributions: [
            "Introduction of Vision Transformer (ViT) that applies Transformer directly to image patches",
            "Demonstration that pre-training on large datasets can overcome inductive biases in vision models",
            "State-of-the-art performance on multiple image classification benchmarks",
            "Analysis of attention mechanisms for vision tasks"
          ]
        },
        requirements: {
          functional: [
            { description: "Implement Vision Transformer architecture as described in the paper", priority: "High" },
            { description: "Support variable input image sizes and patch dimensions", priority: "High" },
            { description: "Implement positional embeddings for image patches", priority: "Medium" },
            { description: "Provide pre-trained model loading capability", priority: "Medium" },
            { description: "Add visualization tools for attention maps", priority: "Low" }
          ],
          dependencies: {
            core: [
              { name: "PyTorch", version: ">=1.7.0" },
              { name: "torchvision", version: ">=0.8.0" },
              { name: "numpy", version: ">=1.19.0" }
            ],
            optional: [
              { name: "matplotlib", version: ">=3.3.0" },
              { name: "timm", version: ">=0.4.0" },
              { name: "einops", version: ">=0.3.0" }
            ]
          }
        }
      },
      {
        id: "p2",
        title: "Implementation of CLIP Model",
        status: "COMPLETED",
        createdAt: "2025-01-20T14:15:00Z",
        currentStep: 4,
        repositoryUrl: "https://github.com/example/clip-implementation",
        paperAnalysis: {
          title: "Learning Transferable Visual Models From Natural Language Supervision",
          authors: "Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, et al.",
          publication: "ICML 2021",
          year: "2021",
          keywords: ["Multimodal Learning", "Vision-Language", "Zero-shot Learning", "Contrastive Learning"],
          url: "https://arxiv.org/abs/2103.00020",
          abstract: "State-of-the-art computer vision systems are trained to predict a fixed set of predetermined object categories. This restricted form of supervision limits their generality and usability since additional labeled data is needed to specify any other visual concept. Learning directly from raw text about images is a promising alternative that provides greater flexibility and accessibility. We demonstrate that the simple pre-training task of predicting which caption goes with which image is an efficient and scalable way to learn SOTA image representations from scratch on a dataset of 400 million (image, text) pairs collected from the internet. After pre-training, natural language is used to reference learned visual concepts (or describe new ones) enabling zero-shot transfer of the model to downstream tasks.",
          contributions: [
            "Introduction of CLIP (Contrastive Language-Image Pre-training)",
            "Training on 400M image-text pairs for zero-shot transfer to various tasks",
            "State-of-the-art performance on various image classification datasets without task-specific training",
            "Analysis of robustness and bias in large-scale vision-language models"
          ]
        },
        requirements: {
          functional: [
            { description: "Implement CLIP architecture with image and text encoders", priority: "High" },
            { description: "Support contrastive learning between image and text embeddings", priority: "High" },
            { description: "Enable zero-shot classification using natural language", priority: "High" },
            { description: "Provide pre-trained model loading capability", priority: "Medium" },
            { description: "Implement efficient batching for large datasets", priority: "Medium" }
          ],
          dependencies: {
            core: [
              { name: "PyTorch", version: ">=1.7.1" },
              { name: "torchvision", version: ">=0.8.2" },
              { name: "transformers", version: ">=4.0.0" }
            ],
            optional: [
              { name: "ftfy", version: ">=6.0.0" },
              { name: "regex", version: ">=2021.4.4" },
              { name: "tqdm", version: ">=4.60.0" }
            ]
          }
        }
      },
      {
        id: "p3",
        title: "Implementation of Segment Anything Model (SAM)",
        status: "FAILED",
        createdAt: "2025-03-01T09:45:00Z",
        currentStep: 1,
        repositoryUrl: null,
        paperAnalysis: {
          title: "Segment Anything",
          authors: "Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, et al.",
          publication: "ICCV 2023",
          year: "2023",
          keywords: ["Image Segmentation", "Foundation Model", "Prompt Engineering", "Computer Vision"],
          url: "https://arxiv.org/abs/2304.02643",
          abstract: "We introduce the Segment Anything (SA) project: a new task, model, and dataset for image segmentation. Using our efficient model in a data collection loop, we built the largest segmentation dataset to date (by far), with over 1 billion masks on 11M licensed and privacy-respecting images. The model is designed and trained to be promptable, so it can transfer zero-shot to new image distributions and tasks. We evaluate its capabilities on numerous tasks and find that its zero-shot performance is impressive, sometimes matching or exceeding prior fully supervised results.",
          contributions: [
            "Introduction of a promptable segmentation model (SAM)",
            "Creation of SA-1B dataset with over 1 billion masks",
            "Demonstration of zero-shot transfer to various segmentation tasks",
            "Analysis of prompt engineering for segmentation"
          ]
        }
      }
    ];
  },

  // Original methods
  /**
   * Upload a research paper.
   * 
   * @param {File} file - The paper file
   * @param {Object} metadata - Paper metadata
   * @returns {Promise<Object>} - Uploaded paper information
   */
  uploadPaper: async (file, metadata = {}) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add metadata fields to form data
      Object.entries(metadata).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value);
        }
      });
      
      const response = await implementationApi.post('/papers/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Error uploading paper:', error);
      throw error;
    }
  },

  /**
   * Get uploaded papers.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} - List of papers
   */
  getPapers: async (params = {}) => {
    try {
      const response = await implementationApi.get('/papers/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching papers:', error);
      throw error;
    }
  },

  /**
   * Get a specific paper by ID.
   * 
   * @param {string} paperId - Paper ID
   * @returns {Promise<Object>} - Paper details
   */
  getPaperById: async (paperId) => {
    try {
      const response = await implementationApi.get(`/papers/${paperId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching paper ${paperId}:`, error);
      throw error;
    }
  },

  /**
   * Request an implementation for a research paper.
   * 
   * @param {Object} requestData - Implementation request data
   * @returns {Promise<Object>} - Created implementation
   */
  requestImplementation: async (requestData) => {
    try {
      const response = await implementationApi.post('/implementations/', requestData);
      return response.data;
    } catch (error) {
      console.error('Error requesting implementation:', error);
      throw error;
    }
  },

  /**
   * Get implementations.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} - List of implementations
   */
  getImplementations: async (params = {}) => {
    try {
      const response = await implementationApi.get('/implementations/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching implementations:', error);
      throw error;
    }
  },

  /**
   * Get a specific implementation by ID.
   * 
   * @param {string} implementationId - Implementation ID
   * @returns {Promise<Object>} - Implementation details
   */
  getImplementationById: async (implementationId) => {
    try {
      const response = await implementationApi.get(`/implementations/${implementationId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching implementation ${implementationId}:`, error);
      throw error;
    }
  },

  /**
   * Cancel an implementation.
   * 
   * @param {string} implementationId - Implementation ID
   * @returns {Promise<void>}
   */
  cancelImplementation: async (implementationId) => {
    try {
      await implementationApi.delete(`/implementations/${implementationId}`);
    } catch (error) {
      console.error(`Error canceling implementation ${implementationId}:`, error);
      throw error;
    }
  }
};

export default implementationService;