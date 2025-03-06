import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Container,
  Grid,
  Typography,
  Paper,
  Box,
  Tabs,
  Tab,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon,
  CloudUpload as UploadIcon,
  Sort as SortIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Timeline as TimelineIcon,
  Clear as ClearIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useFetch } from '../hooks';
import { mockData } from '../utils/mockData';
import { 
  ErrorBoundary, 
  ErrorFallback, 
  LoadingFallback, 
  PaperStatusCard,
  PaperUploadDialog
} from '../components';
import { PAPER_STATUSES } from '../utils/typeDefs';

/**
 * Dashboard for managing uploaded papers and their processing status
 * 
 * @component
 */
const PaperDashboard = () => {
  // State
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [filterMenuAnchor, setFilterMenuAnchor] = useState(null);
  const [sortMenuAnchor, setSortMenuAnchor] = useState(null);
  const [filterOptions, setFilterOptions] = useState({
    statuses: Object.values(PAPER_STATUSES).reduce((acc, status) => {
      acc[status] = true;
      return acc;
    }, {}),
    years: {
      from: 2015,
      to: 2025
    },
    authors: []
  });
  const [sortOption, setSortOption] = useState({
    field: 'updated_at',
    direction: 'desc'
  });
  
  // Fetch papers
  const { 
    data: papers, 
    loading: papersLoading, 
    error: papersError,
    refetch: refetchPapers
  } = useFetch('/api/papers', {
    method: 'GET'
  }, true, () => mockData.papers);
  
  // Stats calculations
  const calculateStats = (papersList) => {
    const stats = {
      total: papersList?.length || 0,
      byStatus: {},
      recent: 0,
      failed: 0
    };
    
    if (!papersList) return stats;
    
    // Count by status
    Object.values(PAPER_STATUSES).forEach(status => {
      stats.byStatus[status] = papersList.filter(paper => paper.status === status).length;
    });
    
    // Count recent (last 7 days)
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    stats.recent = papersList.filter(
      paper => new Date(paper.uploaded_at) > oneWeekAgo
    ).length;
    
    // Count failed
    stats.failed = stats.byStatus[PAPER_STATUSES.FAILED] + stats.byStatus[PAPER_STATUSES.ERROR];
    
    return stats;
  };
  
  const paperStats = calculateStats(papers);
  
  // Filter papers based on active tab, search, and filter options
  const getFilteredPapers = () => {
    if (!papers) return [];
    
    return papers.filter(paper => {
      // Tab filter
      if (activeTab === 1 && !['uploaded', 'queued', 'processing', 'extracting_entities', 'extracting_relationships', 'building_knowledge_graph'].includes(paper.status)) {
        return false;
      }
      if (activeTab === 2 && !['analyzed', 'implementation_ready'].includes(paper.status)) {
        return false;
      }
      if (activeTab === 3 && paper.status !== 'implemented') {
        return false;
      }
      if (activeTab === 4 && !['failed', 'error'].includes(paper.status)) {
        return false;
      }
      
      // Status filter
      if (!filterOptions.statuses[paper.status]) {
        return false;
      }
      
      // Year filter
      const year = parseInt(paper.year);
      if (year && (year < filterOptions.years.from || year > filterOptions.years.to)) {
        return false;
      }
      
      // Author filter
      if (filterOptions.authors.length > 0) {
        const hasMatchingAuthor = paper.authors.some(author => 
          filterOptions.authors.includes(author)
        );
        if (!hasMatchingAuthor) return false;
      }
      
      // Search term
      if (searchTerm) {
        const termLower = searchTerm.toLowerCase();
        const titleMatch = paper.title.toLowerCase().includes(termLower);
        const authorMatch = paper.authors.some(
          author => author.toLowerCase().includes(termLower)
        );
        const abstractMatch = paper.abstract && paper.abstract.toLowerCase().includes(termLower);
        
        if (!titleMatch && !authorMatch && !abstractMatch) {
          return false;
        }
      }
      
      return true;
    }).sort((a, b) => {
      // Sort based on selected option
      const { field, direction } = sortOption;
      
      if (field === 'title') {
        return direction === 'asc' 
          ? a.title.localeCompare(b.title)
          : b.title.localeCompare(a.title);
      }
      
      if (field === 'status') {
        return direction === 'asc'
          ? a.status.localeCompare(b.status)
          : b.status.localeCompare(a.status);
      }
      
      if (field === 'year') {
        const yearA = parseInt(a.year) || 0;
        const yearB = parseInt(b.year) || 0;
        return direction === 'asc' ? yearA - yearB : yearB - yearA;
      }
      
      // Default: sort by date (updated_at or uploaded_at)
      const dateField = field === 'updated_at' ? 'updated_at' : 'uploaded_at';
      const dateA = new Date(a[dateField] || a.uploaded_at);
      const dateB = new Date(b[dateField] || b.uploaded_at);
      
      return direction === 'asc' ? dateA - dateB : dateB - dateA;
    });
  };
  
  const filteredPapers = getFilteredPapers();
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle search change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
  
  // Handle clear search
  const handleClearSearch = () => {
    setSearchTerm('');
  };
  
  // Handle opening filter menu
  const handleFilterMenuOpen = (event) => {
    setFilterMenuAnchor(event.currentTarget);
  };
  
  // Handle closing filter menu
  const handleFilterMenuClose = () => {
    setFilterMenuAnchor(null);
  };
  
  // Handle opening sort menu
  const handleSortMenuOpen = (event) => {
    setSortMenuAnchor(event.currentTarget);
  };
  
  // Handle closing sort menu
  const handleSortMenuClose = () => {
    setSortMenuAnchor(null);
  };
  
  // Handle toggling a status filter
  const handleToggleStatusFilter = (status) => {
    setFilterOptions(prev => ({
      ...prev,
      statuses: {
        ...prev.statuses,
        [status]: !prev.statuses[status]
      }
    }));
  };
  
  // Handle setting sort option
  const handleSetSortOption = (field, direction) => {
    setSortOption({ field, direction });
    handleSortMenuClose();
  };
  
  // Handle opening upload dialog
  const handleOpenUploadDialog = () => {
    setUploadDialogOpen(true);
  };
  
  // Handle closing upload dialog
  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
  };
  
  // Handle paper upload
  const handlePaperUpload = (uploadedPapers) => {
    // In a real app, we would update the papers list or refetch
    console.log('Papers uploaded:', uploadedPapers);
    
    // Refresh papers list
    refetchPapers();
  };
  
  // Handle paper view
  const handleViewPaper = (paper) => {
    // Navigate to paper details
    console.log('View paper:', paper);
  };
  
  // Handle paper implementation
  const handleImplementPaper = (paper) => {
    // Navigate to implementation page
    console.log('Implement paper:', paper);
  };
  
  // Handle paper graph view
  const handleViewGraph = (paper) => {
    // Navigate to knowledge graph for paper
    console.log('View graph for paper:', paper);
  };
  
  // Render filter menu
  const renderFilterMenu = () => (
    <Menu
      id="filter-menu"
      anchorEl={filterMenuAnchor}
      open={Boolean(filterMenuAnchor)}
      onClose={handleFilterMenuClose}
      PaperProps={{
        style: {
          width: 300,
        },
      }}
    >
      <Box sx={{ px: 2, py: 1 }}>
        <Typography variant="subtitle2" gutterBottom>
          Filter by Status
        </Typography>
        <Grid container spacing={1}>
          {Object.entries(filterOptions.statuses).map(([status, enabled]) => (
            <Grid item key={status}>
              <Chip
                label={status}
                color={enabled ? 'primary' : 'default'}
                variant={enabled ? 'filled' : 'outlined'}
                onClick={() => handleToggleStatusFilter(status)}
                size="small"
              />
            </Grid>
          ))}
        </Grid>
      </Box>
      <Divider sx={{ my: 1 }} />
      <MenuItem onClick={handleFilterMenuClose}>
        <Button 
          fullWidth 
          variant="outlined" 
          onClick={() => {
            setFilterOptions({
              statuses: Object.values(PAPER_STATUSES).reduce((acc, status) => {
                acc[status] = true;
                return acc;
              }, {}),
              years: { from: 2015, to: 2025 },
              authors: []
            });
          }}
        >
          Reset Filters
        </Button>
      </MenuItem>
    </Menu>
  );
  
  // Render sort menu
  const renderSortMenu = () => (
    <Menu
      id="sort-menu"
      anchorEl={sortMenuAnchor}
      open={Boolean(sortMenuAnchor)}
      onClose={handleSortMenuClose}
    >
      <MenuItem onClick={() => handleSetSortOption('updated_at', 'desc')}>
        <ListItemIcon>
          {sortOption.field === 'updated_at' && sortOption.direction === 'desc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Newest First</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('updated_at', 'asc')}>
        <ListItemIcon>
          {sortOption.field === 'updated_at' && sortOption.direction === 'asc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Oldest First</ListItemText>
      </MenuItem>
      <Divider />
      <MenuItem onClick={() => handleSetSortOption('title', 'asc')}>
        <ListItemIcon>
          {sortOption.field === 'title' && sortOption.direction === 'asc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Title (A-Z)</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('title', 'desc')}>
        <ListItemIcon>
          {sortOption.field === 'title' && sortOption.direction === 'desc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Title (Z-A)</ListItemText>
      </MenuItem>
      <Divider />
      <MenuItem onClick={() => handleSetSortOption('status', 'asc')}>
        <ListItemIcon>
          {sortOption.field === 'status' && sortOption.direction === 'asc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Status (A-Z)</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('year', 'desc')}>
        <ListItemIcon>
          {sortOption.field === 'year' && sortOption.direction === 'desc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Year (Newest)</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => handleSetSortOption('year', 'asc')}>
        <ListItemIcon>
          {sortOption.field === 'year' && sortOption.direction === 'asc' && (
            <CheckCircleIcon fontSize="small" color="primary" />
          )}
        </ListItemIcon>
        <ListItemText>Year (Oldest)</ListItemText>
      </MenuItem>
    </Menu>
  );
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Paper Dashboard
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <Button
            variant="contained"
            color="primary"
            startIcon={<UploadIcon />}
            onClick={handleOpenUploadDialog}
            sx={{ ml: 2 }}
          >
            Upload Papers
          </Button>
        </Box>
        
        <Typography variant="body1" color="text.secondary">
          Manage your research papers and track their processing status.
        </Typography>
      </Box>
      
      {/* Stats cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5" component="div">
              {paperStats.total}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Papers
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5" component="div">
              {paperStats.recent}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Uploaded in Last 7 Days
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5" component="div">
              {paperStats.byStatus[PAPER_STATUSES.IMPLEMENTED] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Implemented
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h5" component="div" color={paperStats.failed > 0 ? 'error' : 'inherit'}>
              {paperStats.failed}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Failed
            </Typography>
          </Paper>
        </Grid>
      </Grid>
      
      <ErrorBoundary
        fallback={
          <ErrorFallback 
            message="Failed to load papers. Please try again later."
            resetButtonText="Retry"
          />
        }
      >
        {/* Search and filters */}
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search papers by title, author, or abstract"
                value={searchTerm}
                onChange={handleSearchChange}
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: searchTerm && (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        aria-label="clear search"
                        onClick={handleClearSearch}
                        edge="end"
                      >
                        <ClearIcon />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                <Tooltip title="Refresh">
                  <IconButton onClick={refetchPapers}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Filter">
                  <IconButton onClick={handleFilterMenuOpen}>
                    <FilterListIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Sort">
                  <IconButton onClick={handleSortMenuOpen}>
                    <SortIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Settings">
                  <IconButton>
                    <SettingsIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </Box>
        
        {renderFilterMenu()}
        {renderSortMenu()}
        
        {/* Papers list */}
        <Paper elevation={0} variant="outlined" sx={{ mb: 4 }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <span>All Papers</span>
                  <Chip 
                    label={paperStats.total} 
                    size="small" 
                    sx={{ ml: 1 }}
                  />
                </Box>
              } 
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <span>Processing</span>
                  <Chip 
                    label={
                      paperStats.byStatus[PAPER_STATUSES.UPLOADED] +
                      paperStats.byStatus[PAPER_STATUSES.QUEUED] +
                      paperStats.byStatus[PAPER_STATUSES.PROCESSING] +
                      paperStats.byStatus[PAPER_STATUSES.EXTRACTING_ENTITIES] +
                      paperStats.byStatus[PAPER_STATUSES.EXTRACTING_RELATIONSHIPS] +
                      paperStats.byStatus[PAPER_STATUSES.BUILDING_KNOWLEDGE_GRAPH] || 0
                    } 
                    size="small" 
                    color="primary"
                    sx={{ ml: 1 }}
                  />
                </Box>
              }
              icon={<TimelineIcon />}
              iconPosition="start"
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <span>Analyzed</span>
                  <Chip 
                    label={
                      paperStats.byStatus[PAPER_STATUSES.ANALYZED] +
                      paperStats.byStatus[PAPER_STATUSES.IMPLEMENTATION_READY] || 0
                    } 
                    size="small" 
                    color="secondary"
                    sx={{ ml: 1 }}
                  />
                </Box>
              }
              icon={<CheckCircleIcon />}
              iconPosition="start"
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <span>Implemented</span>
                  <Chip 
                    label={paperStats.byStatus[PAPER_STATUSES.IMPLEMENTED] || 0} 
                    size="small" 
                    color="success"
                    sx={{ ml: 1 }}
                  />
                </Box>
              } 
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <span>Failed</span>
                  <Chip 
                    label={paperStats.failed || 0} 
                    size="small" 
                    color="error"
                    sx={{ ml: 1 }}
                  />
                </Box>
              }
              icon={<ErrorIcon />}
              iconPosition="start"
            />
          </Tabs>
          
          {papersLoading ? (
            <LoadingFallback message="Loading papers..." height="300px" />
          ) : papersError ? (
            <Alert severity="error" sx={{ m: 2 }}>
              Error loading papers: {papersError.message}
            </Alert>
          ) : filteredPapers.length === 0 ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                No papers found matching the current filters.
              </Typography>
              <Button 
                variant="outlined" 
                sx={{ mt: 2 }}
                onClick={handleOpenUploadDialog}
                startIcon={<UploadIcon />}
              >
                Upload Papers
              </Button>
            </Box>
          ) : (
            <Box sx={{ p: 2 }}>
              {filteredPapers.map(paper => (
                <PaperStatusCard
                  key={paper.id}
                  paper={paper}
                  onView={handleViewPaper}
                  onImplement={handleImplementPaper}
                  onViewGraph={handleViewGraph}
                  showDetailedStatus={activeTab !== 0}
                />
              ))}
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Showing {filteredPapers.length} of {papers.length} papers
                </Typography>
                {filteredPapers.length < papers.length && (
                  <Button size="small" onClick={() => setActiveTab(0)}>
                    Show All
                  </Button>
                )}
              </Box>
            </Box>
          )}
        </Paper>
      </ErrorBoundary>
      
      {/* Upload Dialog */}
      <PaperUploadDialog
        open={uploadDialogOpen}
        onClose={handleCloseUploadDialog}
        onUpload={handlePaperUpload}
      />
    </Container>
  );
};

export default PaperDashboard;