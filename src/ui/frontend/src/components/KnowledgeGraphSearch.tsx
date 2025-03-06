import React from 'react';
import {
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Alert,
  Switch,
  FormControlLabel,
  Slider,
  Divider
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TuneIcon from '@mui/icons-material/Tune';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import ViewListIcon from '@mui/icons-material/ViewList';
import BubbleChartIcon from '@mui/icons-material/BubbleChart';

interface VisualizationSettings {
  showLabels: boolean;
  highlightConnections: boolean;
  nodeSize: number;
  forceStrength: number;
  clusterByType: boolean;
  maxRelationshipDepth: number;
  showRelationshipLabels: boolean;
  timeBasedLayout: boolean;
  darkMode: boolean;
  filterThreshold: number;
  importanceThreshold: number;
  progressiveLoading: boolean;
  levelOfDetail: boolean;
  tableView: boolean;
}

interface AnalysisSettings {
  showCentralityMetrics: boolean;
  pathfindingEnabled: boolean;
  showDomainClusters: boolean;
  highlightTrendingEntities: boolean;
  showPublicationTimeline: boolean;
  detectCommunities: boolean;
  identifyResearchFrontiers: boolean;
}

interface KnowledgeGraphSearchProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  entityType: string;
  setEntityType: (type: string) => void;
  advancedSearchOpen: boolean;
  setAdvancedSearchOpen: (open: boolean) => void;
  visualizationSettings: VisualizationSettings;
  setVisualizationSettings: (settings: VisualizationSettings) => void;
  analysisSettings: AnalysisSettings;
  setAnalysisSettings: (settings: AnalysisSettings) => void;
  exportFormat: string;
  setExportFormat: (format: string) => void;
  handleSearch: () => void;
  benchmarkMode: boolean;
  setBenchmarkMode: (mode: boolean) => void;
  testDataSize: number;
  setTestDataSize: (size: number) => void;
  generateBenchmarkData: () => void;
  handleExportGraph: () => void;
  filteredGraphData: any | null;
  loadedNodeCount: number;
  handleLoadMoreNodes: () => void;
}

const KnowledgeGraphSearch: React.FC<KnowledgeGraphSearchProps> = ({
  searchTerm,
  setSearchTerm,
  entityType,
  setEntityType,
  advancedSearchOpen,
  setAdvancedSearchOpen,
  visualizationSettings,
  setVisualizationSettings,
  analysisSettings,
  setAnalysisSettings,
  exportFormat,
  setExportFormat,
  handleSearch,
  benchmarkMode,
  setBenchmarkMode,
  testDataSize,
  setTestDataSize,
  generateBenchmarkData,
  handleExportGraph,
  filteredGraphData,
  loadedNodeCount,
  handleLoadMoreNodes
}) => {
  return (
    <Box mb={4}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <TextField
            fullWidth
            label="Search Knowledge Graph"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search for models, datasets, papers, authors, algorithms..."
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth variant="outlined">
            <InputLabel id="entity-type-label">Entity Type</InputLabel>
            <Select
              labelId="entity-type-label"
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              label="Entity Type"
            >
              <MenuItem value="all">All Types</MenuItem>
              
              {/* Core Entity Types */}
              <MenuItem value="MODEL">AI Models</MenuItem>
              <MenuItem value="DATASET">Datasets</MenuItem>
              <MenuItem value="ALGORITHM">Algorithms</MenuItem>
              <MenuItem value="PAPER">Research Papers</MenuItem>
              <MenuItem value="AUTHOR">Authors</MenuItem>
              <MenuItem value="CODE">Code Repositories</MenuItem>
              
              {/* AI Entity Types */}
              <MenuItem value="ARCHITECTURE">Model Architectures</MenuItem>
              <MenuItem value="FRAMEWORK">Frameworks</MenuItem>
              <MenuItem value="PARAMETER">Parameters</MenuItem>
              <MenuItem value="METRIC">Evaluation Metrics</MenuItem>
              
              {/* Scientific Entity Types */}
              <MenuItem value="THEORY">Theories</MenuItem>
              <MenuItem value="METHODOLOGY">Methodologies</MenuItem>
              <MenuItem value="FINDING">Research Findings</MenuItem>
              <MenuItem value="HYPOTHESIS">Hypotheses</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={1}>
          <Grid container spacing={1}>
            <Grid item xs={6} md={12}>
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
            <Grid item xs={6} md={12} sx={{ mt: { xs: 0, md: 1 } }}>
              <Tooltip title="Advanced Search & Visualization Options">
                <Button
                  fullWidth
                  variant={advancedSearchOpen ? "contained" : "outlined"}
                  color="secondary"
                  onClick={() => setAdvancedSearchOpen(!advancedSearchOpen)}
                  sx={{ 
                    height: { xs: '56px', md: '36px' },
                    position: 'relative',
                    overflow: 'hidden',
                    '&::after': advancedSearchOpen ? {
                      content: '""',
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      width: '100%',
                      height: '3px',
                      backgroundColor: 'primary.main',
                      animation: 'pulse 2s infinite'
                    } : {}
                  }}
                  startIcon={<TuneIcon />}
                >
                  {advancedSearchOpen ? "Hide Options" : "Advanced Options"}
                </Button>
              </Tooltip>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      
      {/* Advanced Search Options */}
      <Accordion 
        expanded={advancedSearchOpen} 
        onChange={() => setAdvancedSearchOpen(!advancedSearchOpen)}
        sx={{ mt: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle1" fontWeight="medium">Advanced Search & Visualization Options</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box mb={2}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle2" fontWeight="bold" color="primary">Accessibility Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box mb={2}>
                  <Typography variant="body2" gutterBottom>
                    Use high contrast mode in the theme settings (top-right gear icon) for improved visibility.
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Keyboard navigation:</strong> Use arrow keys to navigate nodes, Enter to select, +/- to zoom.
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      View Mode
                    </Typography>
                    <ToggleButtonGroup
                      value={visualizationSettings.tableView ? 'table' : 'graph'}
                      exclusive
                      onChange={(e, newView) => {
                        if (newView !== null) {
                          setVisualizationSettings({
                            ...visualizationSettings,
                            tableView: newView === 'table'
                          });
                        }
                      }}
                      aria-label="Graph view mode"
                    >
                      <ToggleButton value="graph" aria-label="Graph view">
                        <BubbleChartIcon sx={{ mr: 1 }} />
                        Visual Graph
                      </ToggleButton>
                      <ToggleButton value="table" aria-label="Table view">
                        <ViewListIcon sx={{ mr: 1 }} />
                        Table View
                      </ToggleButton>
                    </ToggleButtonGroup>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Table view provides an accessible alternative for screen readers and easier navigation.
                    </Typography>
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>
            
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle2" fontWeight="bold" color="primary">Visualization Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Display node labels in the graph visualization">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.showLabels}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                showLabels: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Show Labels"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Highlight connections to the selected entity">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.highlightConnections}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                highlightConnections: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Highlight Connections"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Show labels for relationship types between entities">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.showRelationshipLabels}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                showRelationshipLabels: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Relationship Labels"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Group entities by type (models, papers, authors, etc.)">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.clusterByType}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                clusterByType: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Cluster by Type"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" gutterBottom>
                      Node Size: {visualizationSettings.nodeSize}
                    </Typography>
                    <Slider
                      value={visualizationSettings.nodeSize}
                      onChange={(e, newValue) => {
                        setVisualizationSettings({
                          ...visualizationSettings,
                          nodeSize: newValue as number
                        });
                      }}
                      step={1}
                      marks
                      min={3}
                      max={12}
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" gutterBottom>
                      Relationship Depth: {visualizationSettings.maxRelationshipDepth}
                    </Typography>
                    <Tooltip title="Controls how many degrees of separation to show from the selected entity">
                      <Slider
                        value={visualizationSettings.maxRelationshipDepth}
                        onChange={(e, newValue) => setVisualizationSettings({
                          ...visualizationSettings,
                          maxRelationshipDepth: newValue as number
                        })}
                        step={1}
                        marks
                        min={1}
                        max={5}
                        valueLabelDisplay="auto"
                      />
                    </Tooltip>
                  </Grid>
                  
                  {/* Performance Optimization Settings */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom color="primary">
                      Performance Optimization
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Enable smart filtering for large graphs">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.filterThreshold !== undefined && visualizationSettings.filterThreshold > 0}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                filterThreshold: e.target.checked ? 100 : 0
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Smart Node Filtering"
                      />
                    </Tooltip>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Load nodes incrementally for better performance">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.progressiveLoading || false}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                progressiveLoading: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Progressive Loading"
                      />
                    </Tooltip>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Adjust detail based on zoom level">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.levelOfDetail || false}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                levelOfDetail: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Level-of-Detail"
                      />
                    </Tooltip>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Enable dark mode for the visualization">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={visualizationSettings.darkMode}
                            onChange={(e) => {
                              setVisualizationSettings({
                                ...visualizationSettings,
                                darkMode: e.target.checked
                              });
                            }}
                            color="primary"
                          />
                        }
                        label="Dark Mode"
                      />
                    </Tooltip>
                  </Grid>
                  
                  {visualizationSettings.progressiveLoading && filteredGraphData && (
                    <Grid item xs={12}>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Typography variant="body2">
                          Showing {loadedNodeCount} of {filteredGraphData.nodes.length} nodes 
                          ({Math.round(loadedNodeCount / filteredGraphData.nodes.length * 100)}%)
                        </Typography>
                        {loadedNodeCount < filteredGraphData.nodes.length && (
                          <Button 
                            variant="outlined" 
                            size="small" 
                            onClick={handleLoadMoreNodes}
                            sx={{ ml: 2 }}
                          >
                            Load More Nodes
                          </Button>
                        )}
                      </Box>
                      <Slider
                        value={loadedNodeCount}
                        onChange={(e, newValue) => {
                          // This behavior should be implemented in parent component
                        }}
                        min={Math.min(50, filteredGraphData.nodes.length)}
                        max={filteredGraphData.nodes.length}
                        step={Math.max(1, Math.floor(filteredGraphData.nodes.length / 10))}
                        valueLabelDisplay="auto"
                        valueLabelFormat={(value) => `${value} nodes`}
                        disabled // Since we handle this in the parent
                      />
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Box>
          
          <Box>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle2" fontWeight="bold" color="primary">Analysis Tools</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Show network metrics such as node count and graph density">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={analysisSettings.showCentralityMetrics}
                            onChange={(e) => setAnalysisSettings({
                              ...analysisSettings,
                              showCentralityMetrics: e.target.checked
                            })}
                            color="secondary"
                          />
                        }
                        label="Network Metrics"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Enable finding paths between entities">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={analysisSettings.pathfindingEnabled}
                            onChange={(e) => setAnalysisSettings({
                              ...analysisSettings,
                              pathfindingEnabled: e.target.checked
                            })}
                            color="secondary"
                          />
                        }
                        label="Path Analysis"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Detect research communities based on connection patterns">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={analysisSettings.detectCommunities}
                            onChange={(e) => setAnalysisSettings({
                              ...analysisSettings,
                              detectCommunities: e.target.checked
                            })}
                            color="secondary"
                          />
                        }
                        label="Communities"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Highlight emerging research areas and active frontiers">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={analysisSettings.identifyResearchFrontiers}
                            onChange={(e) => setAnalysisSettings({
                              ...analysisSettings,
                              identifyResearchFrontiers: e.target.checked
                            })}
                            color="secondary"
                          />
                        }
                        label="Research Frontiers"
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ mr: 2 }}>Export Format:</Typography>
                      <FormControl size="small" sx={{ minWidth: 150 }}>
                        <InputLabel id="export-format-label">Export Format</InputLabel>
                        <Select
                          labelId="export-format-label"
                          value={exportFormat}
                          onChange={(e) => setExportFormat(e.target.value)}
                          label="Export Format"
                        >
                          <MenuItem value="json">JSON (Data)</MenuItem>
                          <MenuItem value="csv">CSV (Spreadsheet)</MenuItem>
                          <MenuItem value="svg">SVG (Vector Image)</MenuItem>
                          <MenuItem value="png">PNG (Image)</MenuItem>
                          <MenuItem value="neo4j">Neo4j Cypher (Database)</MenuItem>
                        </Select>
                      </FormControl>
                      <Tooltip title="Download knowledge graph in selected format">
                        <Button
                          variant="contained"
                          color="primary"
                          onClick={handleExportGraph}
                          disabled={!filteredGraphData}
                          sx={{ ml: 2 }}
                          size="small"
                        >
                          Export
                        </Button>
                      </Tooltip>
                    </Box>
                  </Grid>
                  
                  {/* Performance Benchmark Controls */}
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" fontWeight="bold" color="primary">
                      Performance Benchmarking
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Tooltip title="Enable performance benchmarking mode">
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={benchmarkMode}
                            onChange={(e) => setBenchmarkMode(e.target.checked)}
                            color="warning"
                          />
                        }
                        label="Benchmark Mode"
                      />
                    </Tooltip>
                  </Grid>
                  
                  <Grid item xs={6} md={4}>
                    <Typography variant="body2" gutterBottom>
                      Test Data Size: {testDataSize} nodes
                    </Typography>
                    <Slider
                      value={testDataSize}
                      onChange={(e, newValue) => setTestDataSize(newValue as number)}
                      step={100}
                      marks={[
                        { value: 100, label: '100' },
                        { value: 500, label: '500' },
                        { value: 1000, label: '1K' },
                        { value: 2000, label: '2K' }
                      ]}
                      min={100}
                      max={2000}
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={5}>
                    <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
                      <Button 
                        variant="contained" 
                        color="warning"
                        onClick={generateBenchmarkData}
                        disabled={benchmarkMode === false}
                        sx={{ mt: 1 }}
                      >
                        Generate Test Data & Benchmark
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default KnowledgeGraphSearch;