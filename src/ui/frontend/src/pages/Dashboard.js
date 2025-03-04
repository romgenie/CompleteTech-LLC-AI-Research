import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
  Box,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  AccountTree as GraphIcon,
  Code as CodeIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';

import knowledgeGraphService from '../services/knowledgeGraphService';
import researchService from '../services/researchService';
import implementationService from '../services/implementationService';

/**
 * Dashboard page component.
 * 
 * @returns {React.ReactElement} Dashboard page
 */
function Dashboard() {
  const [stats, setStats] = useState({
    entities: 0,
    relationships: 0,
    research: { pending: 0, completed: 0 },
    implementations: { requested: 0, completed: 0 },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch dashboard stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);

        // In a real application, we would make actual API calls here
        // For now we'll use placeholder data for the demonstration

        // Example of how we would get the actual data:
        // const graphStats = await knowledgeGraphService.getGraphStats();
        // const researchTasks = await researchService.getTasks();
        // const implementations = await implementationService.getImplementations();

        // Placeholder data
        const graphStats = {
          entities: 42,
          relationships: 128,
          entity_types: ['Model', 'Dataset', 'Paper', 'Author'],
          relationship_types: ['TRAINED_ON', 'AUTHORED_BY', 'CITES'],
        };

        const researchTasks = [
          { status: 'pending' },
          { status: 'pending' },
          { status: 'completed' },
          { status: 'completed' },
          { status: 'completed' },
        ];

        const implementations = [
          { status: 'requested' },
          { status: 'requested' },
          { status: 'completed' },
        ];

        // Process the data
        const pendingResearch = researchTasks.filter(task => task.status === 'pending').length;
        const completedResearch = researchTasks.filter(task => task.status === 'completed').length;
        
        const requestedImpl = implementations.filter(impl => impl.status === 'requested').length;
        const completedImpl = implementations.filter(impl => impl.status === 'completed').length;

        setStats({
          entities: graphStats.entities,
          relationships: graphStats.relationships,
          research: {
            pending: pendingResearch,
            completed: completedResearch,
          },
          implementations: {
            requested: requestedImpl,
            completed: completedImpl,
          },
        });
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const featureCards = [
    {
      title: 'Research',
      description: 'Submit research queries, explore AI research topics, and generate research reports',
      icon: <SearchIcon fontSize="large" color="primary" />,
      action: () => navigate('/research'),
      buttonText: 'Start Research',
    },
    {
      title: 'Knowledge Graph',
      description: 'Explore the AI research knowledge graph, discover connections, and visualize relationships',
      icon: <GraphIcon fontSize="large" color="primary" />,
      action: () => navigate('/knowledge-graph'),
      buttonText: 'Explore Graph',
    },
    {
      title: 'Implementation',
      description: 'Request implementations of research papers, upload papers, and track implementation progress',
      icon: <CodeIcon fontSize="large" color="primary" />,
      action: () => navigate('/implementation'),
      buttonText: 'Implement Research',
    },
  ];

  // Show loading state
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  // Show error state
  if (error) {
    return (
      <Box mt={4}>
        <Paper elevation={3} sx={{ p: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
          <Typography variant="h6">Error</Typography>
          <Typography>{error}</Typography>
          <Button variant="contained" sx={{ mt: 2 }} onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats Summary */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'primary.light',
              color: 'primary.contrastText',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Entities
            </Typography>
            <Typography variant="h3">{stats.entities}</Typography>
            <Typography variant="body2">in Knowledge Graph</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'secondary.light',
              color: 'secondary.contrastText',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Relationships
            </Typography>
            <Typography variant="h3">{stats.relationships}</Typography>
            <Typography variant="body2">in Knowledge Graph</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'success.light',
              color: 'success.contrastText',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Research Tasks
            </Typography>
            <Typography variant="h3">{stats.research.pending + stats.research.completed}</Typography>
            <Typography variant="body2">
              {stats.research.pending} pending, {stats.research.completed} completed
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              height: 140,
              bgcolor: 'info.light',
              color: 'info.contrastText',
            }}
          >
            <Typography variant="h6" gutterBottom>
              Implementations
            </Typography>
            <Typography variant="h3">{stats.implementations.requested + stats.implementations.completed}</Typography>
            <Typography variant="body2">
              {stats.implementations.requested} requested, {stats.implementations.completed} completed
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Feature Cards */}
      <Typography variant="h5" gutterBottom>
        Features
      </Typography>
      <Grid container spacing={3}>
        {featureCards.map(card => (
          <Grid item xs={12} sm={6} md={4} key={card.title}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="center" mb={2}>
                  {card.icon}
                  <Typography variant="h5" component="div" sx={{ ml: 1 }}>
                    {card.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {card.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small" onClick={card.action}>
                  {card.buttonText}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Activity */}
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Recent Activity
        </Typography>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body1" color="text.secondary" align="center">
            No recent activity to display.
          </Typography>
        </Paper>
      </Box>
      
      {/* Development Status */}
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Development Status
        </Typography>
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                Completed Components
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <Box component="li">
                  <Typography variant="body2">Knowledge Extraction Pipeline</Typography>
                </Box>
                <Box component="li">
                  <Typography variant="body2">Knowledge Graph System</Typography>
                </Box>
                <Box component="li">
                  <Typography variant="body2">Research Generation System</Typography>
                </Box>
                <Box component="li">
                  <Typography variant="body2">Technical Infrastructure and UI</Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" gutterBottom>
                In Progress (Phase 3.5)
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <Box component="li">
                  <Typography variant="body2">
                    Paper Processing Pipeline
                    <Box component="span" sx={{ ml: 1, color: 'primary.main', fontWeight: 'bold' }}>
                      (Foundation Implemented)
                    </Box>
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                The Paper Processing Pipeline foundation has been implemented with the core state machine 
                architecture, Celery task definitions, and API endpoints. Full processing capabilities are
                planned for completion in the next release.
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Container>
  );
}

export default Dashboard;