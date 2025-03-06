import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Breadcrumbs,
  Link,
  Divider,
  CircularProgress,
  useMediaQuery,
  useTheme
} from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import RecommendIcon from '@mui/icons-material/Recommend';
import InsightsIcon from '@mui/icons-material/Insights';
import { 
  ResearchRecommendationList, 
  ResearchInsightList 
} from '../components';
import { 
  useRecommendations, 
  useResearchInsights, 
  useSaveRecommendation 
} from '../services/recommendationService';
import { useSavedQueries, useAllTags } from '../services/researchService';
import { useLocalStorage } from '../hooks';

/**
 * Tab panel component
 */
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`recommendation-tabpanel-${index}`}
      aria-labelledby={`recommendation-tab-${index}`}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

/**
 * Page for research recommendations and insights
 */
const ResearchRecommendationsPage: React.FC = () => {
  const [tabIndex, setTabIndex] = useState(0);
  const [savedRecommendations, setSavedRecommendations] = useLocalStorage<string[]>('saved_recommendations', []);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Get saved queries and tags
  const savedQueriesQuery = useSavedQueries();
  const allTagsQuery = useAllTags();
  
  // Get recommendations and insights
  const recommendationsQuery = useRecommendations(
    allTagsQuery.tags || [],
    savedQueriesQuery.data || []
  );
  
  const insightsQuery = useResearchInsights(
    allTagsQuery.tags || [],
    savedQueriesQuery.data || []
  );
  
  // Mutation for saving recommendations
  const saveRecommendationMutation = useSaveRecommendation();
  
  // Handle tab change
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabIndex(newValue);
  };
  
  // Handle using a recommendation
  const handleUseRecommendation = (query: string) => {
    // Navigate to research page with the query
    navigate('/research/optimized', { state: { query } });
  };
  
  // Handle saving a recommendation
  const handleSaveRecommendation = async (id: string) => {
    // Toggle the saved status
    if (savedRecommendations.includes(id)) {
      setSavedRecommendations(savedRecommendations.filter(recId => recId !== id));
    } else {
      setSavedRecommendations([...savedRecommendations, id]);
      
      // Also save it on the server (if we were using an actual API)
      try {
        await saveRecommendationMutation.mutateAsync({ recommendationId: id });
      } catch (error) {
        console.error('Failed to save recommendation:', error);
      }
    }
  };
  
  return (
    <Container maxWidth="lg">
      <Box my={4}>
        <Breadcrumbs 
          separator={<NavigateNextIcon fontSize="small" />} 
          aria-label="breadcrumb"
          sx={{ mb: 2 }}
        >
          <Link component={RouterLink} to="/" color="inherit">
            Dashboard
          </Link>
          <Link component={RouterLink} to="/research" color="inherit">
            Research
          </Link>
          <Typography color="text.primary">Recommendations</Typography>
        </Breadcrumbs>
        
        <Box mb={3}>
          <Typography variant="h4" component="h1" gutterBottom>
            Research Recommendations
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Personalized research suggestions based on your previous queries and interests
          </Typography>
        </Box>
        
        <Paper variant="outlined">
          <Tabs 
            value={tabIndex} 
            onChange={handleTabChange}
            variant={isMobile ? "fullWidth" : "standard"}
            centered={!isMobile}
            aria-label="recommendation tabs"
          >
            <Tab 
              icon={!isMobile ? <RecommendIcon /> : undefined}
              iconPosition="start"
              label="Recommended Topics" 
              id="recommendation-tab-0" 
              aria-controls="recommendation-tabpanel-0" 
            />
            <Tab 
              icon={!isMobile ? <InsightsIcon /> : undefined}
              iconPosition="start"
              label="Research Insights" 
              id="recommendation-tab-1" 
              aria-controls="recommendation-tabpanel-1" 
            />
          </Tabs>
          
          <Divider />
          
          <TabPanel value={tabIndex} index={0}>
            <ResearchRecommendationList
              recommendationGroups={recommendationsQuery.data || []}
              onUseRecommendation={handleUseRecommendation}
              onSaveRecommendation={handleSaveRecommendation}
              savedRecommendations={savedRecommendations}
              loading={recommendationsQuery.isLoading || savedQueriesQuery.isLoading}
              error={recommendationsQuery.error || savedQueriesQuery.error}
            />
          </TabPanel>
          
          <TabPanel value={tabIndex} index={1}>
            <ResearchInsightList
              insights={insightsQuery.data || []}
              loading={insightsQuery.isLoading || savedQueriesQuery.isLoading}
              error={insightsQuery.error || savedQueriesQuery.error}
            />
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default ResearchRecommendationsPage;