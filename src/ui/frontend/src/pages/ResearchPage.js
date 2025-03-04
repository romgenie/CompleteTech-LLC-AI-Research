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
  Tab
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import HistoryIcon from '@mui/icons-material/History';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import researchService from '../services/researchService';

// Panel for the content of each tab
function TabPanel({ children, value, index, ...other }) {
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
}

const ResearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [savedQueries, setSavedQueries] = useState([]);
  const [queryHistory, setQueryHistory] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);

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

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSearch = async () => {
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

  const handleSaveQuery = async () => {
    if (!query.trim()) return;
    
    try {
      await researchService.saveQuery(query);
      setSavedQueries(prev => [{ query, timestamp: new Date().toISOString() }, ...prev]);
    } catch (err) {
      console.error('Error saving query:', err);
    }
  };

  const handleSelectReport = (report) => {
    setSelectedReport(report);
  };

  const renderResultsList = () => {
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
                  <Button 
                    variant="outlined" 
                    startIcon={<PictureAsPdfIcon />}
                    onClick={() => window.open(selectedReport.pdfUrl, '_blank')}
                  >
                    Export PDF
                  </Button>
                </Box>
                <Divider sx={{ mb: 3 }} />
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
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchPage;