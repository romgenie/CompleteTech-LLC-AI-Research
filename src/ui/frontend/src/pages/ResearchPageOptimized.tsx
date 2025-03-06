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
  IconButton,
  Tooltip,
  ListItemSecondaryAction
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SearchIcon from '@mui/icons-material/Search';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import HistoryIcon from '@mui/icons-material/History';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LabelIcon from '@mui/icons-material/Label';
import RecommendIcon from '@mui/icons-material/Recommend';
import { 
  useResearch, 
  useSaveQuery, 
  useSavedQueries, 
  useQueryHistory, 
  useUpdateSavedQuery,
  useAllTags,
  MockSearchResult 
} from '../services/researchService';
import { 
  CitationManager, 
  FavoriteButton, 
  TagManager,
  ResearchFilterPanel,
  ResearchExportDialog
} from '../components';
import { useFavorites } from '../hooks';
import { mockData } from '../utils/mockData';
import { ResearchFilterOptions, ExportOptions, ResearchResult } from '../types/research';

// Panel for the content of each tab
interface TabPanelProps {
  children?: React.ReactNode;
  value: number;
  index: number;
}

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
}

const ResearchPageOptimized: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [tabValue, setTabValue] = useState<number>(0);
  const [selectedReport, setSelectedReport] = useState<MockSearchResult | null>(null);
  const [isCitationOpen, setIsCitationOpen] = useState<boolean>(false);
  const [isFilterOpen, setIsFilterOpen] = useState<boolean>(false);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);
  const [filterOptions, setFilterOptions] = useState<ResearchFilterOptions>({});
  
  // React Query hooks
  const savedQueriesQuery = useSavedQueries();
  const queryHistoryQuery = useQueryHistory();
  const researchMutation = useResearch();
  const saveQueryMutation = useSaveQuery();
  const updateQueryMutation = useUpdateSavedQuery();
  const allTagsQuery = useAllTags();
  
  // Custom hooks
  const { isFavorite, toggleFavorite } = useFavorites();
  
  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number): void => {
    setTabValue(newValue);
  };
  
  // Handle search
  const handleSearch = async (): Promise<void> => {
    if (!query.trim()) return;
    
    try {
      await researchMutation.mutateAsync({ query });
      // Update the query history list
      queryHistoryQuery.refetch();
    } catch (err) {
      // Error is handled by React Query
      console.error('Research error (handled by React Query):', err);
    }
  };
  
  // Handle save query
  const handleSaveQuery = async (): Promise<void> => {
    if (!query.trim()) return;
    
    try {
      await saveQueryMutation.mutateAsync({ query });
      // Update the saved queries list
      savedQueriesQuery.refetch();
    } catch (err) {
      // Error is handled by React Query
      console.error('Save query error (handled by React Query):', err);
    }
  };
  
  // Handle select report
  const handleSelectReport = (report: MockSearchResult): void => {
    setSelectedReport(report);
  };
  
  // Handle citation toggle
  const toggleCitationManager = (): void => {
    setIsCitationOpen(!isCitationOpen);
  };
  
  // Handle citation action
  const handleCitation = (citation: string, style: string): void => {
    console.log(`Added citation in ${style} style:`, citation);
  };
  
  // Handle filter toggle
  const toggleFilterPanel = (): void => {
    setIsFilterOpen(!isFilterOpen);
  };
  
  // Handle filter change
  const handleFilterChange = (filters: ResearchFilterOptions): void => {
    setFilterOptions(filters);
  };
  
  // Handle export toggle
  const toggleExportDialog = (): void => {
    setIsExportOpen(!isExportOpen);
  };
  
  // Handle export action
  const handleExport = (options: ExportOptions): void => {
    console.log('Exporting with options:', options);
    // In a real implementation, this would call an API endpoint
  };
  
  // Handle add tag
  const handleAddTag = async (itemId: string, tag: string): Promise<void> => {
    const query = savedQueriesQuery.data?.find(q => q.id === itemId);
    if (!query) return;
    
    const currentTags = query.tags || [];
    const updatedTags = [...currentTags, tag];
    
    try {
      await updateQueryMutation.mutateAsync({
        id: itemId,
        tags: updatedTags
      });
      savedQueriesQuery.refetch();
    } catch (err) {
      console.error('Error adding tag:', err);
    }
  };
  
  // Handle remove tag
  const handleRemoveTag = async (itemId: string, tag: string): Promise<void> => {
    const query = savedQueriesQuery.data?.find(q => q.id === itemId);
    if (!query || !query.tags) return;
    
    const updatedTags = query.tags.filter(t => t !== tag);
    
    try {
      await updateQueryMutation.mutateAsync({
        id: itemId,
        tags: updatedTags
      });
      savedQueriesQuery.refetch();
    } catch (err) {
      console.error('Error removing tag:', err);
    }
  };
  
  // Handle favorite toggle
  const handleToggleFavorite = async (itemId: string): Promise<void> => {
    const query = savedQueriesQuery.data?.find(q => q.id === itemId);
    if (!query) return;
    
    const newFavoriteStatus = !query.isFavorite;
    
    try {
      await updateQueryMutation.mutateAsync({
        id: itemId,
        isFavorite: newFavoriteStatus
      });
      
      // Update local storage favorites
      toggleFavorite(itemId);
      
      // Refresh saved queries
      savedQueriesQuery.refetch();
    } catch (err) {
      console.error('Error toggling favorite status:', err);
    }
  };
  
  // Render results list
  const renderResultsList = () => {
    if (researchMutation.isLoading) {
      return (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (researchMutation.isError) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {researchMutation.error instanceof Error 
            ? researchMutation.error.message 
            : 'An error occurred during research'}
        </Alert>
      );
    }
    
    const results = researchMutation.data 
      ? mockData.researchResults.sources.map((source, index) => ({
          id: `result-${index}`,
          title: source.title,
          source: source.url.includes('arxiv') ? 'ArXiv' : 'Research Journal',
          relevance: parseFloat(source.confidence) * 10,
          content: mockData.researchResults.sections[index % mockData.researchResults.sections.length].content,
          pdfUrl: source.url
        }))
      : [];
    
    if (results.length === 0) {
      return (
        <Typography variant="body1" color="text.secondary" p={3}>
          No results to display. Try conducting a research query.
        </Typography>
      );
    }
    
    return (
      <List>
        {results.map((result) => (
          <React.Fragment key={result.id}>
            <ListItem 
              button
              onClick={() => handleSelectReport(result)}
              selected={selectedReport && selectedReport.id === result.id}
            >
              <ListItemText 
                primary={result.title} 
                secondary={`Source: ${result.source} | Relevance: ${result.relevance.toFixed(1)}/10`} 
              />
            </ListItem>
            {results.indexOf(result) < results.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    );
  };
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Research Assistant (Optimized)
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" paragraph>
            Ask research questions and get comprehensive reports with citations and references.
          </Typography>
        </Box>
        
        <Box>
          <Button 
            component={RouterLink} 
            to="/research/stats" 
            variant="outlined"
            startIcon={<AssessmentIcon />}
            sx={{ mr: 1 }}
          >
            Stats
          </Button>
          <Button 
            component={RouterLink} 
            to="/research/tags" 
            variant="outlined"
            startIcon={<LabelIcon />}
            sx={{ mr: 1 }}
          >
            Manage Tags
          </Button>
          <Button 
            component={RouterLink} 
            to="/research/recommendations" 
            variant="outlined"
            startIcon={<RecommendIcon />}
          >
            Recommendations
          </Button>
        </Box>
      </Box>
      
      {/* Filter panel */}
      <ResearchFilterPanel
        onFilterChange={handleFilterChange}
        availableTags={allTagsQuery.tags || []}
        expanded={isFilterOpen}
      />
      
      {/* Export dialog */}
      <ResearchExportDialog
        open={isExportOpen}
        onClose={toggleExportDialog}
        onExport={handleExport}
      />
      
      <Box mb={4}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Research Query"
              variant="outlined"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., Explain the latest advancements in transformer architecture for NLP"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              disabled={researchMutation.isLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={1}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={handleSearch}
              sx={{ height: '56px' }}
              startIcon={<SearchIcon />}
              disabled={researchMutation.isLoading}
            >
              {researchMutation.isLoading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={1}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleSaveQuery}
              sx={{ height: '56px' }}
              startIcon={<BookmarkIcon />}
              disabled={saveQueryMutation.isLoading}
            >
              {saveQueryMutation.isLoading ? 'Saving...' : 'Save'}
            </Button>
          </Grid>
          <Grid item xs={6} md={1}>
            <Button
              fullWidth
              variant="outlined"
              onClick={toggleFilterPanel}
              sx={{ height: '56px' }}
              startIcon={<FilterAltIcon />}
            >
              Filter
            </Button>
          </Grid>
          <Grid item xs={6} md={1}>
            <Button
              fullWidth
              variant="outlined"
              onClick={toggleExportDialog}
              sx={{ height: '56px' }}
              startIcon={<CloudDownloadIcon />}
            >
              Export
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
              {savedQueriesQuery.isLoading ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : savedQueriesQuery.isError ? (
                <Alert severity="error" sx={{ m: 2 }}>
                  {savedQueriesQuery.error instanceof Error 
                    ? savedQueriesQuery.error.message 
                    : 'Error loading saved queries'}
                </Alert>
              ) : (
                <List>
                  {savedQueriesQuery.data && savedQueriesQuery.data.length > 0 ? (
                    savedQueriesQuery.data.map((item, index) => (
                      <ListItem 
                        button 
                        key={item.id}
                        onClick={() => setQuery(item.query)}
                      >
                        <ListItemText 
                          primary={item.query} 
                          secondary={
                            <Box>
                              <Typography variant="caption" display="block">
                                {new Date(item.createdAt).toLocaleDateString()}
                              </Typography>
                              <TagManager
                                itemId={item.id}
                                currentTags={item.tags || []}
                                onAddTag={handleAddTag}
                                onRemoveTag={handleRemoveTag}
                                showButton={false}
                              />
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <FavoriteButton 
                            isFavorite={!!item.isFavorite}
                            onToggle={() => handleToggleFavorite(item.id)}
                            size="small"
                          />
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))
                  ) : (
                    <Typography variant="body1" color="text.secondary" p={2}>
                      No saved queries yet.
                    </Typography>
                  )}
                </List>
              )}
            </TabPanel>
            <TabPanel value={tabValue} index={2}>
              {queryHistoryQuery.isLoading ? (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress />
                </Box>
              ) : queryHistoryQuery.isError ? (
                <Alert severity="error" sx={{ m: 2 }}>
                  {queryHistoryQuery.error instanceof Error 
                    ? queryHistoryQuery.error.message 
                    : 'Error loading query history'}
                </Alert>
              ) : (
                <List>
                  {queryHistoryQuery.data && queryHistoryQuery.data.length > 0 ? (
                    queryHistoryQuery.data.map((item, index) => (
                      <ListItem 
                        button 
                        key={item.id}
                        onClick={() => setQuery(item.query)}
                      >
                        <ListItemText 
                          primary={item.query} 
                          secondary={new Date(item.timestamp).toLocaleDateString()} 
                        />
                      </ListItem>
                    ))
                  ) : (
                    <Typography variant="body1" color="text.secondary" p={2}>
                      No query history yet.
                    </Typography>
                  )}
                </List>
              )}
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
                      onClick={toggleCitationManager}
                      sx={{ mr: 1 }}
                    >
                      {isCitationOpen ? 'Hide Citations' : 'Manage Citations'}
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<PictureAsPdfIcon />}
                      onClick={() => window.open(selectedReport.pdfUrl, '_blank')}
                      sx={{ mr: 1 }}
                    >
                      View PDF
                    </Button>
                    <Button 
                      variant="outlined" 
                      startIcon={<CloudDownloadIcon />}
                      onClick={toggleExportDialog}
                    >
                      Export
                    </Button>
                  </Box>
                </Box>
                <Divider sx={{ mb: 3 }} />
                
                {isCitationOpen && (
                  <Box mb={3}>
                    <CitationManager 
                      researchResults={[selectedReport]}
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
                <Alert severity="info" sx={{ mt: 3, maxWidth: 500 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>New Features:</Typography>
                  <Typography variant="body2" paragraph>
                    This page now implements organization features:
                  </Typography>
                  <ul>
                    <li>Tag your research queries for better organization</li>
                    <li>Add queries to favorites for quick access</li>
                    <li>Filter research by tags, date and favorites</li>
                    <li>Export your research in various formats</li>
                  </ul>
                </Alert>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchPageOptimized;