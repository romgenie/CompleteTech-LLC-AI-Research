import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  CardActions,
  Button,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  Tabs,
  Tab,
  Chip,
  useTheme,
  Alert
} from '@mui/material';
import {
  ArticleOutlined as ArticleIcon,
  SchemaOutlined as SchemaIcon,
  CodeOutlined as CodeIcon,
  TerminalOutlined as TerminalIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ErrorBoundary, ErrorFallback, PaperStatusCard } from '../components';
import { useFetch } from '../hooks';
import { mockData } from '../utils/mockData';

/**
 * Dashboard page displaying overview of system capabilities and recent activity
 * 
 * @returns {JSX.Element} Dashboard component
 */
function Dashboard() {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();
  const navigate = useNavigate();
  
  // Fetch recent papers
  const { 
    data: papers, 
    loading: papersLoading, 
    error: papersError 
  } = useFetch('/api/papers/recent', {
    method: 'GET'
  }, true, () => mockData.papers.slice(0, 5));
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Navigate to paper details
  const handleViewPaper = (paper) => {
    navigate(`/implementation?paper=${paper.id}`);
  };
  
  // Navigate to paper implementation
  const handleImplementPaper = (paper) => {
    navigate(`/implementation?paper=${paper.id}&tab=implementation`);
  };
  
  // Navigate to knowledge graph for a paper
  const handleViewGraph = (paper) => {
    navigate(`/knowledge-graph?paper=${paper.id}`);
  };
  
  // Dashboard statistics
  const stats = {
    papers: 42,
    entities: 1876,
    relationships: 5432,
    implementations: 23
  };
  
  // Feature cards
  const features = [
    {
      title: 'Research',
      description: 'Conduct research queries and generate comprehensive reports with up-to-date information from multiple sources.',
      icon: <ArticleIcon fontSize="large" />,
      path: '/research',
      color: theme.palette.primary.main
    },
    {
      title: 'Knowledge Graph',
      description: 'Explore the knowledge graph of research entities and relationships, with visualization and query capabilities.',
      icon: <SchemaIcon fontSize="large" />,
      path: '/knowledge-graph',
      color: theme.palette.secondary.main
    },
    {
      title: 'Implementation',
      description: 'Generate code implementations from research papers, with customization and explanation of algorithms.',
      icon: <CodeIcon fontSize="large" />,
      path: '/implementation',
      color: theme.palette.success.main
    }
  ];
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      {/* System stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <ArticleIcon color="primary" fontSize="large" />
              <Typography variant="h4">{stats.papers}</Typography>
              <Typography variant="subtitle1">Papers</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <SchemaIcon color="secondary" fontSize="large" />
              <Typography variant="h4">{stats.entities}</Typography>
              <Typography variant="subtitle1">Entities</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <SchemaIcon color="info" fontSize="large" />
              <Typography variant="h4">{stats.relationships}</Typography>
              <Typography variant="subtitle1">Relationships</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CodeIcon color="success" fontSize="large" />
              <Typography variant="h4">{stats.implementations}</Typography>
              <Typography variant="subtitle1">Implementations</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Feature cards */}
      <Typography variant="h5" component="h2" gutterBottom>
        Features
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {features.map((feature) => (
          <Grid item xs={12} md={4} key={feature.title}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardHeader
                title={feature.title}
                avatar={React.cloneElement(feature.icon, { 
                  sx: { color: feature.color } 
                })}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="body1">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => navigate(feature.path)}
                >
                  Explore
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* Recent papers */}
      <Typography variant="h5" component="h2" gutterBottom>
        Recent Papers
      </Typography>
      
      <ErrorBoundary
        fallback={
          <ErrorFallback 
            message="Failed to load recent papers. Please try again later."
            resetButtonText="Retry"
          />
        }
      >
        {papersError ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            Error loading recent papers: {papersError.message}
          </Alert>
        ) : (
          <Box sx={{ mb: 4 }}>
            <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
              <Tab label="All Papers" />
              <Tab label="Processing" />
              <Tab label="Analyzed" />
              <Tab label="Implemented" />
            </Tabs>
            
            {papers && papers.length > 0 ? (
              papers
                .filter(paper => {
                  if (activeTab === 0) return true;
                  if (activeTab === 1) return ['uploaded', 'queued', 'processing', 'extracting_entities', 'extracting_relationships', 'building_knowledge_graph'].includes(paper.status);
                  if (activeTab === 2) return ['analyzed', 'implementation_ready'].includes(paper.status);
                  if (activeTab === 3) return paper.status === 'implemented';
                  return true;
                })
                .map(paper => (
                  <PaperStatusCard
                    key={paper.id}
                    paper={paper}
                    onView={handleViewPaper}
                    onImplement={handleImplementPaper}
                    onViewGraph={handleViewGraph}
                  />
                ))
            ) : (
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  No papers available.
                </Typography>
              </Paper>
            )}
          </Box>
        )}
      </ErrorBoundary>
    </Box>
  );
}

export default Dashboard;