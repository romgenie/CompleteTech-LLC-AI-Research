import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  CircularProgress,
  Alert,
  Breadcrumbs,
  Link,
  Button,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DateRangeIcon from '@mui/icons-material/DateRange';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import ResearchStats from '../components/ResearchStats';
import { ResearchStats as ResearchStatsType } from '../types/research';

// Mock data for research stats
const mockResearchStats: ResearchStatsType = {
  totalQueries: 248,
  savedQueries: 52,
  favorites: 18,
  tagCounts: {
    'NLP': 24,
    'Machine Learning': 37,
    'Neural Networks': 18,
    'Transformers': 42,
    'Computer Vision': 15,
    'LLM': 35,
    'GPT': 22,
    'BERT': 12,
    'Fine-tuning': 9,
    'Embeddings': 14,
    'Reinforcement Learning': 7,
    'Deep Learning': 28,
    'Text Generation': 16,
    'Image Recognition': 11
  },
  topSearchTerms: [
    { term: 'transformer architecture', count: 42 },
    { term: 'large language model comparison', count: 38 },
    { term: 'neural network training', count: 31 },
    { term: 'GPT-4 capabilities', count: 27 },
    { term: 'BERT vs RoBERTa', count: 24 },
    { term: 'attention mechanism explained', count: 22 },
    { term: 'image recognition advancements', count: 18 },
    { term: 'fine-tuning techniques', count: 16 },
    { term: 'reinforcement learning from human feedback', count: 15 },
    { term: 'text generation methods', count: 14 }
  ],
  queriesByDate: [
    { date: '2023-01-10', count: 5 },
    { date: '2023-01-20', count: 8 },
    { date: '2023-02-01', count: 10 },
    { date: '2023-02-15', count: 15 },
    { date: '2023-03-01', count: 12 },
    { date: '2023-03-15', count: 18 },
    { date: '2023-04-01', count: 22 },
    { date: '2023-04-15', count: 20 },
    { date: '2023-05-01', count: 25 },
    { date: '2023-05-15', count: 30 },
    { date: '2023-06-01', count: 28 },
    { date: '2023-06-15', count: 32 },
    { date: '2023-07-01', count: 35 },
    { date: '2023-07-15', count: 38 }
  ],
  averageResultsPerQuery: 7.2
};

/**
 * Page for displaying research statistics and analytics
 */
const ResearchStatsPage: React.FC = () => {
  const [stats, setStats] = useState<ResearchStatsType | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Simulate fetching stats from an API
  useEffect(() => {
    // In a real app, this would be an API call
    const fetchStats = async () => {
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Use mock data
        setStats(mockResearchStats);
        setLoading(false);
      } catch (err) {
        setError('Failed to load research statistics');
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);
  
  // Handle export
  const handleExportStats = () => {
    // In a real app, this would trigger a download of the stats as JSON, CSV, etc.
    console.log('Exporting statistics data...');
    
    // Create a JSON file for download
    const dataStr = JSON.stringify(stats, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'research_stats.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };
  
  return (
    <Container maxWidth="lg">
      <Box my={4}>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link component={RouterLink} to="/" color="inherit">
            Dashboard
          </Link>
          <Link component={RouterLink} to="/research" color="inherit">
            Research
          </Link>
          <Typography color="text.primary">Statistics</Typography>
        </Breadcrumbs>
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Research Analytics
          </Typography>
          
          <Button 
            variant="outlined" 
            startIcon={<FileDownloadIcon />}
            onClick={handleExportStats}
            disabled={loading || !!error}
          >
            Export Data
          </Button>
        </Box>
        
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Visualize and analyze your research activity, trends, and organization
        </Typography>
        
        <Divider sx={{ my: 3 }} />
        
        {loading ? (
          <Box display="flex" justifyContent="center" my={5}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        ) : stats ? (
          <ResearchStats stats={stats} />
        ) : (
          <Alert severity="info">
            No statistics available yet. Try conducting more research queries.
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default ResearchStatsPage;