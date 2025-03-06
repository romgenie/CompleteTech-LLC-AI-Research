import React, { useState } from 'react';
import {
  Typography, 
  Box, 
  TextField, 
  Button, 
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
  useTheme
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import researchService from '../services/researchService';
import paginationService from '../services/paginationService';
import { Pagination } from '../components';

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
  const theme = useTheme();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [selectedReport, setSelectedReport] = useState(null);

  // Use paginated queries for history and saved queries
  const {
    data: historyData,
    isLoading: historyLoading,
    error: historyError,
    pagination: historyPagination
  } = paginationService.useResearchData({
    initialPage: 1,
    initialPageSize: 10,
    sortField: 'timestamp',
    sortDirection: 'desc',
    requestConfig: {
      params: { type: 'history' }
    }
  });

  // Saved queries with pagination
  const {
    data: savedQueriesData,
    isLoading: savedQueriesLoading,
    error: savedQueriesError,
    pagination: savedQueriesPagination
  } = paginationService.useResearchData({
    initialPage: 1,
    initialPageSize: 10,
    sortField: 'timestamp',
    sortDirection: 'desc',
    requestConfig: {
      params: { type: 'saved' }
    }
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setSearchLoading(true);
    setSearchError(null);
    try {
      const data = await researchService.conductResearch(query);
      setResults(data.results);
      
      // Real API would update the history automatically
      // We don't need to update the history state manually here, 
      // as the paginated query will refetch
    } catch (err) {
      console.error('Research error:', err);
      
      // Use mock data for demonstration purposes
      const mockData = researchService.getMockResults();
      setResults(mockData.results);
      
      // Still show the error to indicate we're using mock data
      setSearchError('Using mock data for demonstration. In production, this would call the actual API.');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSaveQuery = async () => {
    if (!query.trim()) return;
    
    try {
      await researchService.saveQuery(query);
      // Refresh saved queries after saving
      savedQueriesPagination.goToPage(1);
    } catch (err) {
      console.error('Error saving query:', err);
    }
  };

  const handleSelectReport = (report) => {
    setSelectedReport(report);
  };

  const renderResultsList = () => {
    if (searchLoading) {
      return (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      );
    }

    if (searchError) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {searchError}
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
              disabled={searchLoading}
            >
              {searchLoading ? <CircularProgress size={24} /> : 'Search'}
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
          <Paper variant="outlined" sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
              <TabPanel value={tabValue} index={0}>
                {renderResultsList()}
              </TabPanel>
              <TabPanel value={tabValue} index={1}>
                {savedQueriesLoading ? (
                  <Box display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                  </Box>
                ) : savedQueriesError ? (
                  <Alert severity="error" sx={{ m: 2 }}>
                    Error loading saved queries
                  </Alert>
                ) : savedQueriesData?.items?.length ? (
                  <List>
                    {savedQueriesData.items.map((item, index) => (
                      <ListItem 
                        button 
                        key={item.id || index}
                        onClick={() => setQuery(item.query)}
                      >
                        <ListItemText 
                          primary={item.query} 
                          secondary={new Date(item.timestamp).toLocaleDateString()} 
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body1" color="text.secondary" sx={{ p: 2 }}>
                    No saved queries yet.
                  </Typography>
                )}
                
                {/* Pagination for saved queries */}
                {savedQueriesData && savedQueriesData.total > 0 && (
                  <Box sx={{ mx: 2 }}>
                    <Pagination
                      page={savedQueriesPagination.page}
                      pageSize={savedQueriesPagination.pageSize}
                      total={savedQueriesData.total}
                      totalPages={savedQueriesData.totalPages}
                      onPageChange={savedQueriesPagination.goToPage}
                      onPageSizeChange={savedQueriesPagination.setPageSize}
                      loading={savedQueriesLoading}
                      compact={true}
                    />
                  </Box>
                )}
              </TabPanel>
              <TabPanel value={tabValue} index={2}>
                {historyLoading ? (
                  <Box display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                  </Box>
                ) : historyError ? (
                  <Alert severity="error" sx={{ m: 2 }}>
                    Error loading history
                  </Alert>
                ) : historyData?.items?.length ? (
                  <List>
                    {historyData.items.map((item, index) => (
                      <ListItem 
                        button 
                        key={item.id || index}
                        onClick={() => setQuery(item.query)}
                      >
                        <ListItemText 
                          primary={item.query} 
                          secondary={new Date(item.timestamp).toLocaleDateString()} 
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body1" color="text.secondary" sx={{ p: 2 }}>
                    No query history yet.
                  </Typography>
                )}
                
                {/* Pagination for history */}
                {historyData && historyData.total > 0 && (
                  <Box sx={{ mx: 2 }}>
                    <Pagination
                      page={historyPagination.page}
                      pageSize={historyPagination.pageSize}
                      total={historyData.total}
                      totalPages={historyData.totalPages}
                      onPageChange={historyPagination.goToPage}
                      onPageSizeChange={historyPagination.setPageSize}
                      loading={historyLoading}
                      compact={true}
                    />
                  </Box>
                )}
              </TabPanel>
            </Box>
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
                <Alert severity="info" sx={{ mt: 3, maxWidth: 550 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Server-Side Pagination Implementation:</Typography>
                  <Typography variant="body2">
                    This page now demonstrates server-side pagination for research history and saved queries.
                    The pagination system efficiently handles large datasets by fetching only the current page
                    of data from the server, with prefetching for smooth navigation.
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