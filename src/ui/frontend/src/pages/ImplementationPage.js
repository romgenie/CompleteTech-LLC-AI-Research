import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Chip,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Tabs,
  Tab,
  Card,
  CardContent
} from '@mui/material';
import {
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  InsertDriveFile as InsertDriveFileIcon,
  GitHub as GitHubIcon
} from '@mui/icons-material';
import implementationService from '../services/implementationService';

// Panel for the content of each tab
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`implementation-tabpanel-${index}`}
      aria-labelledby={`implementation-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ImplementationPage = () => {
  const [implementationProjects, setImplementationProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paperUrl, setPaperUrl] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [testResults, setTestResults] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    'Paper Analysis', 
    'Implementation Planning', 
    'Code Generation', 
    'Testing', 
    'Verification'
  ];

  useEffect(() => {
    // Fetch all implementation projects on component mount
    fetchImplementationProjects();
  }, []);

  useEffect(() => {
    // When selectedProject changes, fetch its files
    if (selectedProject) {
      fetchProjectFiles(selectedProject.id);
      setActiveStep(selectedProject.currentStep || 0);
    }
  }, [selectedProject]);

  const fetchImplementationProjects = async () => {
    setLoading(true);
    try {
      const data = await implementationService.getAllProjects();
      setImplementationProjects(data);
    } catch (err) {
      console.error('Error fetching implementation projects:', err);
      
      // Use mock data for demonstration
      const mockProjects = implementationService.getMockProjects();
      setImplementationProjects(mockProjects);
      
      setError('Using mock data for demonstration. In production, this would call the actual API.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectFiles = async (projectId) => {
    setLoading(true);
    try {
      const data = await implementationService.getProjectFiles(projectId);
      setProjectFiles(data);
      setSelectedFile(null);
      setFileContent('');
    } catch (err) {
      console.error('Error fetching project files:', err);
      
      // Use mock data for demonstration
      const mockFiles = [
        { id: "f1", name: "model.py", path: "src/model.py" },
        { id: "f2", name: "utils.py", path: "src/utils.py" },
        { id: "f3", name: "train.py", path: "src/train.py" },
        { id: "f4", name: "dataset.py", path: "src/dataset.py" },
        { id: "f5", name: "config.yaml", path: "config.yaml" },
        { id: "f6", name: "requirements.txt", path: "requirements.txt" },
        { id: "f7", name: "README.md", path: "README.md" }
      ];
      
      setProjectFiles(mockFiles);
      setSelectedFile(null);
      setFileContent('');
      
      setError('Using mock file data for demonstration');
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (fileId) => {
    setLoading(true);
    try {
      const data = await implementationService.getFileContent(fileId);
      setFileContent(data.content);
    } catch (err) {
      console.error('Error fetching file content:', err);
      
      // Use mock file content based on file ID
      let mockContent = '';
      
      if (fileId === 'f1') {
        mockContent = `import torch
import torch.nn as nn
import torch.nn.functional as F

class TransformerModel(nn.Module):
    """Implementation of the paper architecture"""
    
    def __init__(self, input_dim, hidden_dim, num_heads, num_layers, dropout=0.1):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Linear(input_dim, hidden_dim)
        self.transformer_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(hidden_dim, num_heads, 4*hidden_dim, dropout),
            num_layers
        )
        self.output_layer = nn.Linear(hidden_dim, input_dim)
        
    def forward(self, x):
        """Forward pass of the model"""
        x = self.embedding(x)
        x = self.transformer_encoder(x)
        return self.output_layer(x)
`;
      } else if (fileId === 'f2') {
        mockContent = `import torch
import numpy as np
import random
import os
from typing import List, Tuple, Dict, Any

def set_seed(seed: int) -> None:
    """Set random seed for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        
def save_checkpoint(model, optimizer, epoch, path):
    """Save model checkpoint to file"""
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'epoch': epoch,
    }, path)
    
def load_checkpoint(model, optimizer, path):
    """Load model checkpoint from file"""
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return model, optimizer, checkpoint['epoch']
`;
      } else if (fileId === 'f7') {
        mockContent = `# Implementation of Vision Transformer (ViT)

This repository contains a PyTorch implementation of the Vision Transformer (ViT) model as described in the paper "[An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929)".

## Features

- Faithful implementation of the Vision Transformer architecture
- Support for different input image sizes and patch dimensions
- Pre-trained model loading capabilities
- Visualization tools for attention maps

## Installation

\`\`\`
pip install -r requirements.txt
\`\`\`

## Usage

\`\`\`python
from model import VisionTransformer

# Create model
model = VisionTransformer(
    img_size=224,
    patch_size=16,
    num_classes=1000,
    dim=768,
    depth=12,
    heads=12,
    mlp_dim=3072
)

# Load pre-trained weights
model.load_from_checkpoint('path/to/checkpoint.pth')

# Make predictions
predictions = model(images)
\`\`\`

## Citation

\`\`\`
@article{dosovitskiy2020image,
  title={An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale},
  author={Dosovitskiy, Alexey and Beyer, Lucas and Kolesnikov, Alexander and others},
  journal={ICLR},
  year={2021}
}
\`\`\`
`;
      } else {
        mockContent = `// Mock content for file ${fileId}
// This would contain the actual implementation code`;
      }
      
      setFileContent(mockContent);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!paperUrl.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await implementationService.createProject(paperUrl);
      setImplementationProjects(prev => [...prev, data]);
      setPaperUrl('');
    } catch (err) {
      setError('Failed to create project. Please check the paper URL and try again.');
      console.error('Project creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProject = (project) => {
    setSelectedProject(project);
    setTabValue(0);
  };

  const handleSelectFile = (file) => {
    setSelectedFile(file);
    fetchFileContent(file.id);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleRunTests = async () => {
    if (!selectedProject) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await implementationService.runTests(selectedProject.id);
      setTestResults(data);
    } catch (err) {
      setError('Failed to run tests');
      console.error('Test error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleContinueImplementation = async () => {
    if (!selectedProject) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await implementationService.continueImplementation(selectedProject.id);
      
      // Update the project with new information
      setSelectedProject(prev => ({
        ...prev,
        currentStep: data.currentStep,
        status: data.status
      }));
      
      // If new files were created, refresh the file list
      if (data.filesChanged) {
        fetchProjectFiles(selectedProject.id);
      }
      
      setActiveStep(data.currentStep);
    } catch (err) {
      setError('Failed to continue implementation');
      console.error('Implementation continuation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Research Implementation System
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Automatically implement AI research papers and verify their results.
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              New Implementation
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Paper URL (arXiv, DOI, etc.)"
                  variant="outlined"
                  value={paperUrl}
                  onChange={(e) => setPaperUrl(e.target.value)}
                  placeholder="e.g., https://arxiv.org/abs/2203.15556"
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={handleCreateProject}
                  disabled={loading || !paperUrl.trim()}
                >
                  Create Project
                </Button>
              </Grid>
            </Grid>
          </Paper>
          <Paper variant="outlined" sx={{ height: '65vh', overflowY: 'auto' }}>
            <Typography variant="h6" sx={{ p: 2, pb: 1 }}>
              Projects
            </Typography>
            {loading && !selectedProject ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : implementationProjects.length > 0 ? (
              <List>
                {implementationProjects.map((project) => (
                  <React.Fragment key={project.id}>
                    <ListItem 
                      button 
                      onClick={() => handleSelectProject(project)}
                      selected={selectedProject && selectedProject.id === project.id}
                    >
                      <ListItemText 
                        primary={project.title} 
                        secondary={
                          <Box mt={0.5}>
                            <Chip 
                              label={project.status} 
                              size="small" 
                              color={
                                project.status === 'COMPLETED' ? 'success' :
                                project.status === 'FAILED' ? 'error' :
                                project.status === 'IN_PROGRESS' ? 'primary' : 'default'
                              }
                              sx={{ mr: 1, mb: 0.5 }}
                            />
                            <Typography variant="caption" display="block" color="text.secondary">
                              {new Date(project.createdAt).toLocaleDateString()}
                            </Typography>
                          </Box>
                        } 
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box p={3} textAlign="center">
                <Typography variant="body1" color="text.secondary">
                  No implementation projects yet. Create a new one to get started.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={9}>
          {selectedProject ? (
            <>
              <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Box>
                    <Typography variant="h5">{selectedProject.title}</Typography>
                    <Box display="flex" alignItems="center" mt={1}>
                      <Chip 
                        label={selectedProject.status} 
                        size="small" 
                        color={
                          selectedProject.status === 'COMPLETED' ? 'success' :
                          selectedProject.status === 'FAILED' ? 'error' :
                          selectedProject.status === 'IN_PROGRESS' ? 'primary' : 'default'
                        }
                        sx={{ mr: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        Created: {new Date(selectedProject.createdAt).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Button 
                      variant="outlined" 
                      startIcon={<GitHubIcon />}
                      sx={{ mr: 1 }}
                      onClick={() => window.open(selectedProject.repositoryUrl, '_blank')}
                      disabled={!selectedProject.repositoryUrl}
                    >
                      GitHub
                    </Button>
                    <Button 
                      variant="contained" 
                      startIcon={<PlayArrowIcon />}
                      onClick={handleContinueImplementation}
                      disabled={loading || selectedProject.status === 'COMPLETED'}
                    >
                      Continue
                    </Button>
                  </Box>
                </Box>

                <Stepper activeStep={activeStep} alternativeLabel sx={{ mt: 3 }}>
                  {steps.map((label) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Paper>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="implementation tabs">
                  <Tab label="Files" id="implementation-tab-0" aria-controls="implementation-tabpanel-0" />
                  <Tab label="Tests" id="implementation-tab-1" aria-controls="implementation-tabpanel-1" />
                  <Tab label="Paper Analysis" id="implementation-tab-2" aria-controls="implementation-tabpanel-2" />
                  <Tab label="Requirements" id="implementation-tab-3" aria-controls="implementation-tabpanel-3" />
                </Tabs>
              </Box>
              <Box sx={{ height: '60vh' }}>
                <TabPanel value={tabValue} index={0}>
                  <Grid container spacing={3} sx={{ height: '100%' }}>
                    <Grid item xs={12} md={3}>
                      <Paper variant="outlined" sx={{ height: '55vh', overflowY: 'auto' }}>
                        {loading && !selectedFile ? (
                          <Box display="flex" justifyContent="center" p={3}>
                            <CircularProgress />
                          </Box>
                        ) : projectFiles.length > 0 ? (
                          <List dense>
                            {projectFiles.map((file) => (
                              <ListItem 
                                button 
                                key={file.id}
                                onClick={() => handleSelectFile(file)}
                                selected={selectedFile && selectedFile.id === file.id}
                              >
                                <InsertDriveFileIcon fontSize="small" sx={{ mr: 1, color: 'action.active' }} />
                                <ListItemText 
                                  primary={file.name} 
                                  secondary={file.path} 
                                />
                              </ListItem>
                            ))}
                          </List>
                        ) : (
                          <Box p={3} textAlign="center">
                            <Typography variant="body2" color="text.secondary">
                              No files available yet.
                            </Typography>
                          </Box>
                        )}
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={9}>
                      <Paper 
                        variant="outlined" 
                        sx={{ 
                          height: '55vh', 
                          p: 2, 
                          backgroundColor: '#1e1e1e',
                          fontFamily: 'Consolas, monospace',
                          color: '#d4d4d4',
                          overflowY: 'auto'
                        }}
                      >
                        {loading && selectedFile ? (
                          <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                            <CircularProgress sx={{ color: 'white' }} />
                          </Box>
                        ) : selectedFile ? (
                          <pre style={{ margin: 0 }}>
                            {fileContent}
                          </pre>
                        ) : (
                          <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height="100%">
                            <CodeIcon sx={{ fontSize: 60, color: '#555', mb: 2 }} />
                            <Typography variant="body1" color="#888">
                              Select a file to view its content
                            </Typography>
                          </Box>
                        )}
                      </Paper>
                    </Grid>
                  </Grid>
                </TabPanel>
                <TabPanel value={tabValue} index={1}>
                  <Box display="flex" justifyContent="flex-end" mb={2}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<PlayArrowIcon />}
                      onClick={handleRunTests}
                      disabled={loading || selectedProject.status !== 'COMPLETED'}
                    >
                      Run Tests
                    </Button>
                  </Box>
                  {loading ? (
                    <Box display="flex" justifyContent="center" p={3}>
                      <CircularProgress />
                    </Box>
                  ) : testResults ? (
                    <Box>
                      <Alert 
                        severity={testResults.success ? "success" : "error"} 
                        sx={{ mb: 3 }}
                        icon={testResults.success ? <CheckCircleIcon /> : <ErrorIcon />}
                      >
                        {testResults.success ? "All tests passed successfully!" : "Some tests failed."}
                      </Alert>
                      
                      <Typography variant="h6" gutterBottom>
                        Test Results
                      </Typography>
                      {testResults.tests.map((test, index) => (
                        <Accordion key={index} defaultExpanded={!test.passed}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box display="flex" alignItems="center" width="100%">
                              {test.passed ? (
                                <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                              ) : (
                                <ErrorIcon sx={{ color: 'error.main', mr: 1 }} />
                              )}
                              <Typography>{test.name}</Typography>
                              <Box flexGrow={1} />
                              <Chip 
                                label={test.passed ? "Passed" : "Failed"} 
                                color={test.passed ? "success" : "error"} 
                                size="small" 
                              />
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              Duration: {test.duration}ms
                            </Typography>
                            {test.output && (
                              <Paper 
                                variant="outlined" 
                                sx={{ 
                                  p: 2, 
                                  backgroundColor: '#f5f5f5', 
                                  fontFamily: 'monospace',
                                  maxHeight: '200px',
                                  overflowY: 'auto'
                                }}
                              >
                                <pre style={{ margin: 0 }}>
                                  {test.output}
                                </pre>
                              </Paper>
                            )}
                          </AccordionDetails>
                        </Accordion>
                      ))}
                    </Box>
                  ) : (
                    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height="40vh">
                      <PlayArrowIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="h6" color="text.secondary">
                        No test results available
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        Run tests to see results here
                      </Typography>
                    </Box>
                  )}
                </TabPanel>
                <TabPanel value={tabValue} index={2}>
                  {selectedProject.paperAnalysis ? (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Paper Information
                      </Typography>
                      <Grid container spacing={3} mb={3}>
                        <Grid item xs={12} md={6}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="subtitle2" color="text.secondary">
                                Title
                              </Typography>
                              <Typography variant="body1" gutterBottom>
                                {selectedProject.paperAnalysis.title}
                              </Typography>
                              <Typography variant="subtitle2" color="text.secondary" mt={2}>
                                Authors
                              </Typography>
                              <Typography variant="body1" gutterBottom>
                                {selectedProject.paperAnalysis.authors}
                              </Typography>
                              <Typography variant="subtitle2" color="text.secondary" mt={2}>
                                Publication
                              </Typography>
                              <Typography variant="body1">
                                {selectedProject.paperAnalysis.publication}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="subtitle2" color="text.secondary">
                                Year
                              </Typography>
                              <Typography variant="body1" gutterBottom>
                                {selectedProject.paperAnalysis.year}
                              </Typography>
                              <Typography variant="subtitle2" color="text.secondary" mt={2}>
                                Keywords
                              </Typography>
                              <Box mt={1}>
                                {selectedProject.paperAnalysis.keywords.map((keyword, idx) => (
                                  <Chip key={idx} label={keyword} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                                ))}
                              </Box>
                              <Typography variant="subtitle2" color="text.secondary" mt={2}>
                                URL
                              </Typography>
                              <Typography variant="body1">
                                <a href={selectedProject.paperAnalysis.url} target="_blank" rel="noopener noreferrer">
                                  {selectedProject.paperAnalysis.url}
                                </a>
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      </Grid>

                      <Typography variant="h6" gutterBottom>
                        Abstract
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                        <Typography variant="body1">
                          {selectedProject.paperAnalysis.abstract}
                        </Typography>
                      </Paper>

                      <Typography variant="h6" gutterBottom>
                        Key Contributions
                      </Typography>
                      <List>
                        {selectedProject.paperAnalysis.contributions.map((contribution, idx) => (
                          <ListItem key={idx}>
                            <ListItemText primary={contribution} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  ) : (
                    <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                      <Typography variant="body1" color="text.secondary">
                        Paper analysis will be available once the paper is processed.
                      </Typography>
                    </Box>
                  )}
                </TabPanel>
                <TabPanel value={tabValue} index={3}>
                  {selectedProject.requirements ? (
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="h6" gutterBottom>
                          Functional Requirements
                        </Typography>
                        <List>
                          {selectedProject.requirements.functional.map((req, idx) => (
                            <ListItem key={idx}>
                              <ListItemText 
                                primary={req.description} 
                                secondary={`Priority: ${req.priority}`} 
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="h6" gutterBottom>
                          Dependencies
                        </Typography>
                        <Box mb={3}>
                          <Typography variant="subtitle2" gutterBottom>
                            Core Libraries
                          </Typography>
                          <Box>
                            {selectedProject.requirements.dependencies.core.map((dep, idx) => (
                              <Chip 
                                key={idx} 
                                label={`${dep.name} ${dep.version}`} 
                                size="small" 
                                sx={{ mr: 0.5, mb: 0.5 }} 
                              />
                            ))}
                          </Box>
                        </Box>
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Optional Libraries
                          </Typography>
                          <Box>
                            {selectedProject.requirements.dependencies.optional.map((dep, idx) => (
                              <Chip 
                                key={idx} 
                                label={`${dep.name} ${dep.version}`} 
                                size="small" 
                                variant="outlined"
                                sx={{ mr: 0.5, mb: 0.5 }} 
                              />
                            ))}
                          </Box>
                        </Box>
                      </Grid>
                    </Grid>
                  ) : (
                    <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                      <Typography variant="body1" color="text.secondary">
                        Requirements will be available once the implementation planning phase is complete.
                      </Typography>
                    </Box>
                  )}
                </TabPanel>
              </Box>
            </>
          ) : (
            <Paper variant="outlined" sx={{ height: '70vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <Box textAlign="center" p={3}>
                <CodeIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Project Selected
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Select an existing project from the list or create a new one.
                </Typography>
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ImplementationPage;