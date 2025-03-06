import React, { useState, useEffect } from 'react';
import {
  Container, 
  Typography, 
  Box, 
  TextField, 
  Button, 
  Card, 
  CardContent, 
  Divider,
  CircularProgress,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  Alert,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import HistoryIcon from '@mui/icons-material/History';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LocalLibraryIcon from '@mui/icons-material/LocalLibrary';
import researchService from '../services/researchService';
import CitationManager from '../components/CitationManager';
import { CitationStyle } from '../utils/citationManager';

// Interface for tab panel props
interface TabPanelProps {
  children?: React.ReactNode;
  value: number;
  index: number;
}

// Panel for the content of each tab
const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`research-tabpanel-${index}`}
      aria-labelledby={`research-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

// Interface for saved query
interface SavedQuery {
  query: string;
  timestamp: string;
}

// Interface for research result
interface ResearchResult {
  id: string;
  title: string;
  source: string;
  relevance: number;
  content: string;
  pdfUrl?: string;
}

const ResearchPage: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<ResearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState<number>(0);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [queryHistory, setQueryHistory] = useState<SavedQuery[]>([]);
  const [selectedReport, setSelectedReport] = useState<ResearchResult | null>(null);
  const [isCitationOpen, setIsCitationOpen] = useState<boolean>(false);

  // Fetch saved queries and history on component mount
  useEffect(() => {
    const fetchSavedQueries = async () => {
      try {
        const data = await researchService.getSavedQueries();
        setSavedQueries(data);
      } catch (err) {
        console.error('Error fetching saved queries:', err);
      }
    };

    const fetchQueryHistory = async () => {
      try {
        const data = await researchService.getQueryHistory();
        setQueryHistory(data);
      } catch (err) {
        console.error('Error fetching query history:', err);
      }
    };

    fetchSavedQueries();
    fetchQueryHistory();
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number): void => {
    setTabValue(newValue);
  };

  const handleSearch = async (): Promise<void> => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await researchService.conductResearch(query);
      setResults(data.results);
      
      // Update history in state
      setQueryHistory(prev => [{ query, timestamp: new Date().toISOString() }, ...prev]);
    } catch (err) {
      console.error('Research error:', err);
      
      // Use mock data for demonstration purposes
      const mockData = researchService.getMockResults();
      setResults(mockData.results);
      setQueryHistory(prev => [{ query, timestamp: new Date().toISOString() }, ...prev]);
      
      // Still show the error to indicate we're using mock data
      setError('Using mock data for demonstration. In production, this would call the actual API.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveQuery = async (): Promise<void> => {
    if (!query.trim()) return;
    
    try {
      await researchService.saveQuery(query);
      setSavedQueries(prev => [{ query, timestamp: new Date().toISOString() }, ...prev]);
    } catch (err) {
      console.error('Error saving query:', err);
    }
  };

  const handleSelectReport = (report: ResearchResult): void => {
    setSelectedReport(report);
  };

  const handleCitation = (citation: string, style: CitationStyle): void => {
    // Here you would typically insert the citation into the selected text
    // or add it to a list of citations for the current document
    console.log(`Added citation in ${style} style:`, citation);
  };

  const toggleCitationManager = (): void => {
    setIsCitationOpen(!isCitationOpen);
  };

  const renderResultsList = (): React.ReactNode => {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      );
    }

    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      );
    }

    if (results.length === 0) {
      return (
        <Typography variant="body1" color="text.secondary" p={3}>
          No results to display. Try conducting a research query.
        </Typography>
      );
    }

    return (
      <List>
        {results.map((result, index) => (
          <React.Fragment key={index}>
            <ListItem 
              button
              onClick={() => handleSelectReport(result)}
              selected={selectedReport && selectedReport.id === result.id}
            >
              <ListItemText 
                primary={result.title} 
                secondary={`Source: ${result.source} | Relevance: ${result.relevance}/10`} 
              />
            </ListItem>
            {index < results.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    );
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Research Assistant
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Ask research questions and get comprehensive reports with citations and references.
      </Typography>
      <Box mb={4}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={10}>
            <TextField
              fullWidth
              label="Research Query"
              variant="outlined"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., Explain the latest advancements in transformer architecture for NLP"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={6} md={1}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={handleSearch}
              sx={{ height: '56px' }}
              startIcon={<SearchIcon />}
            >
              Search
            </Button>
          </Grid>
          <Grid item xs={6} md={1}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleSaveQuery}
              sx={{ height: '56px' }}
              startIcon={<BookmarkIcon />}
            >
              Save
            </Button>
          </Grid>
        </Grid>
      </Box>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="research tabs">
          <Tab label="Results" id="research-tab-0" aria-controls="research-tabpanel-0" />
          <Tab label="Saved Queries" id="research-tab-1" aria-controls="research-tabpanel-1" />
          <Tab label="History" id="research-tab-2" aria-controls="research-tabpanel-2" />
        </Tabs>
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ height: '70vh', overflowY: 'auto' }}>
            <TabPanel value={tabValue} index={0}>
              {renderResultsList()}
            </TabPanel>
            <TabPanel value={tabValue} index={1}>
              <List>
                {savedQueries.length ? (
                  savedQueries.map((item, index) => (
                    <ListItem 
                      button 
                      key={index}
                      onClick={() => setQuery(item.query)}
                    >
                      <ListItemText 
                        primary={item.query} 
                        secondary={new Date(item.timestamp).toLocaleDateString()} 
                      />
                    </ListItem>
                  ))
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    No saved queries yet.
                  </Typography>
                )}
              </List>
            </TabPanel>
            <TabPanel value={tabValue} index={2}>
              <List>
                {queryHistory.length ? (
                  queryHistory.map((item, index) => (
                    <ListItem 
                      button 
                      key={index}
                      onClick={() => setQuery(item.query)}
                    >
                      <ListItemText 
                        primary={item.query} 
                        secondary={new Date(item.timestamp).toLocaleDateString()} 
                      />
                    </ListItem>
                  ))
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    No query history yet.
                  </Typography>
                )}
              </List>
            </TabPanel>
          </Paper>
        </Grid>
        <Grid item xs={12} md={8}>
          <Paper variant="outlined" sx={{ height: '70vh', overflowY: 'auto', p: 3 }}>
            {selectedReport ? (
              <>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h5">{selectedReport.title}</Typography>
                  <Box>
                    <Button 
                      variant="outlined" 
                      startIcon={<LocalLibraryIcon />}
                      onClick={toggleCitationManager}
                      sx={{ mr: 1 }}
                    >
                      {isCitationOpen ? 'Hide Citations' : 'Manage Citations'}
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<PictureAsPdfIcon />}
                      onClick={() => selectedReport.pdfUrl && window.open(selectedReport.pdfUrl, '_blank')}
                    >
                      Export PDF
                    </Button>
                  </Box>
                </Box>
                <Divider sx={{ mb: 3 }} />
                
                {isCitationOpen && (
                  <Box mb={3}>
                    <CitationManager 
                      researchResults={Array.isArray(results) ? results : []}
                      onCite={handleCitation}
                    />
                  </Box>
                )}
                
                <Typography variant="body1" component="div">
                  <div dangerouslySetInnerHTML={{ __html: selectedReport.content }} />
                </Typography>
              </>
            ) : (
              <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                justifyContent="center" 
                height="100%"
              >
                <SearchIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Select a research result to view
                </Typography>
                <Alert severity="info" sx={{ mt: 3, maxWidth: 400 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Integration Status:</Typography>
                  <Typography variant="body2">
                    The Research Assistant is integrated with the Paper Processing Pipeline foundation and Citation Management,
                    allowing seamless connections between research queries, paper analysis, and bibliography management.
                  </Typography>
                </Alert>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchPage;