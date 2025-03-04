import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Chip,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Slider,
  Tooltip,
  IconButton
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TuneIcon from '@mui/icons-material/Tune';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoIcon from '@mui/icons-material/Info';
import DownloadIcon from '@mui/icons-material/Download';
import ShareIcon from '@mui/icons-material/Share';
import * as d3 from 'd3';
import knowledgeGraphService from '../services/knowledgeGraphService';

const KnowledgeGraphPage = () => {
  // Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [entityDetails, setEntityDetails] = useState(null);
  const [relatedEntities, setRelatedEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [graphLoading, setGraphLoading] = useState(false);
  const [error, setError] = useState(null);
  const [entityType, setEntityType] = useState('all');
  const [graphData, setGraphData] = useState(null);
  
  // Visualization settings
  const [advancedSearchOpen, setAdvancedSearchOpen] = useState(false);
  const [visualizationSettings, setVisualizationSettings] = useState({
    showLabels: true,
    highlightConnections: true,
    nodeSize: 7,
    forceStrength: 500,
    clusterByType: false,
    maxRelationshipDepth: 2,
    showRelationshipLabels: false,
    timeBasedLayout: false,
    darkMode: false,
  });
  
  // Analysis settings
  const [analysisSettings, setAnalysisSettings] = useState({
    showCentralityMetrics: false,
    pathfindingEnabled: false,
    showDomainClusters: false,
    highlightTrendingEntities: false,
    showPublicationTimeline: false,
    detectCommunities: false,
    identifyResearchFrontiers: false,
  });
  
  // Export options
  const [exportFormat, setExportFormat] = useState('json');

  const svgRef = useRef(null);
  const graphContainerRef = useRef(null);

  // Colors for different entity types
  const entityColors = {
    MODEL: '#4285F4',      // Google Blue
    DATASET: '#34A853',    // Google Green
    ALGORITHM: '#EA4335',  // Google Red
    PAPER: '#FBBC05',      // Google Yellow
    AUTHOR: '#9C27B0',     // Purple
    CODE: '#00ACC1',       // Cyan
    default: '#757575'     // Gray
  };

  useEffect(() => {
    // When selectedEntity changes, get its details and related entities
    if (selectedEntity) {
      fetchEntityDetails(selectedEntity.id);
      fetchRelatedEntities(selectedEntity.id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedEntity]);

  useEffect(() => {
    // Create or update graph visualization when graphData changes
    if (graphData) {
      renderGraph();
    }
  }, [graphData, visualizationSettings]);

  const fetchEntityDetails = async (entityId) => {
    setLoading(true);
    try {
      const data = await knowledgeGraphService.getEntityDetails(entityId);
      setEntityDetails(data);
    } catch (err) {
      console.error('Error fetching entity details:', err);
      
      // Use mock graph to get entity details
      const mockGraph = knowledgeGraphService.getMockGraph();
      const entity = mockGraph.nodes.find(node => node.id === entityId);
      
      if (entity) {
        // Create mock entity details
        const mockEntityDetails = {
          ...entity,
          description: `This is a ${entity.type.toLowerCase()} related to AI research.`,
          properties: {
            created: "2025-02-10",
            updated: "2025-03-01",
            citations: Math.floor(Math.random() * 1000),
            complexity: ["Low", "Medium", "High"][Math.floor(Math.random() * 3)],
            domain: ["Computer Vision", "NLP", "Reinforcement Learning"][Math.floor(Math.random() * 3)]
          }
        };
        
        setEntityDetails(mockEntityDetails);
      } else {
        setError('Entity not found in mock data');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchRelatedEntities = async (entityId) => {
    setGraphLoading(true);
    try {
      const data = await knowledgeGraphService.getRelatedEntities(entityId);
      setRelatedEntities(data.entities);
      
      // Prepare data for D3 graph
      const nodes = [
        { id: selectedEntity.id, name: selectedEntity.name, type: selectedEntity.type },
        ...data.entities.map(entity => ({ 
          id: entity.id, 
          name: entity.name, 
          type: entity.type 
        }))
      ];
      
      const links = data.relationships.map(rel => ({
        source: rel.source,
        target: rel.target,
        type: rel.type
      }));
      
      setGraphData({ nodes, links });
    } catch (err) {
      console.error('Error fetching related entities:', err);
      
      // Use mock graph data
      const mockGraph = knowledgeGraphService.getMockGraph();
      
      // Find relationships for the selected entity
      const relatedLinks = mockGraph.links.filter(link => 
        link.source === entityId || link.target === entityId
      );
      
      // Get related entity IDs
      const relatedEntityIds = new Set();
      relatedLinks.forEach(link => {
        if (link.source === entityId) {
          relatedEntityIds.add(link.target);
        } else {
          relatedEntityIds.add(link.source);
        }
      });
      
      // Get related entity nodes
      const relatedEntities = mockGraph.nodes.filter(node => 
        relatedEntityIds.has(node.id)
      );
      
      setRelatedEntities(relatedEntities);
      
      // Prepare graph data for visualization
      const nodes = [
        selectedEntity,
        ...relatedEntities
      ];
      
      setGraphData({ 
        nodes: nodes,
        links: relatedLinks
      });
      
      setError('Using mock data for graph visualization');
    } finally {
      setGraphLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await knowledgeGraphService.searchEntities(searchTerm, entityType);
      setSearchResults(data);
      setSelectedEntity(null);
      setEntityDetails(null);
      setRelatedEntities([]);
      setGraphData(null);
    } catch (err) {
      console.error('Search error:', err);
      
      // Use mock data for demonstration
      const mockGraph = knowledgeGraphService.getMockGraph();
      
      // Filter nodes based on search term (case insensitive)
      const filteredNodes = mockGraph.nodes.filter(node => 
        node.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        node.type.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      // If entityType is specified, filter further
      const results = entityType !== 'all' 
        ? filteredNodes.filter(node => node.type === entityType)
        : filteredNodes;
        
      // Add relevance scores for UI display
      const searchResults = results.map(node => ({
        ...node,
        relevance: (9 + Math.random()).toFixed(1)
      }));
      
      setSearchResults(searchResults);
      setSelectedEntity(null);
      setEntityDetails(null);
      setRelatedEntities([]);
      setGraphData(null);
      
      // Show message about using mock data
      setError('Using mock data for demonstration. In production, this would call the actual API.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectEntity = (entity) => {
    setSelectedEntity(entity);
  };
  
  // Handle export graph data
  const handleExportGraph = () => {
    if (!graphData) return;
    
    let exportData;
    let mimeType;
    let fileExtension;
    
    switch (exportFormat) {
      case 'json':
        exportData = JSON.stringify(graphData, null, 2);
        mimeType = 'application/json';
        fileExtension = 'json';
        break;
      case 'csv':
        // Simple CSV format for nodes
        const nodeHeader = 'id,name,type\n';
        const nodeRows = graphData.nodes.map(node => 
          `${node.id},"${node.name}",${node.type}`
        ).join('\n');
        
        // Simple CSV format for links
        const linkHeader = 'source,target,type\n';
        const linkRows = graphData.links.map(link => 
          `${link.source.id || link.source},${link.target.id || link.target},${link.type}`
        ).join('\n');
        
        exportData = `# Nodes\n${nodeHeader}${nodeRows}\n\n# Links\n${linkHeader}${linkRows}`;
        mimeType = 'text/csv';
        fileExtension = 'csv';
        break;
      case 'neo4j':
        // Generate Cypher queries for Neo4j
        const nodeQueries = graphData.nodes.map(node => 
          `CREATE (n:${node.type} {id: "${node.id}", name: "${node.name}"})`
        ).join('\n');
        
        const linkQueries = graphData.links.map(link => {
          const sourceId = link.source.id || link.source;
          const targetId = link.target.id || link.target;
          return `MATCH (a), (b) WHERE a.id = "${sourceId}" AND b.id = "${targetId}" CREATE (a)-[:${link.type}]->(b)`;
        }).join('\n');
        
        exportData = `// Nodes\n${nodeQueries}\n\n// Relationships\n${linkQueries}`;
        mimeType = 'text/plain';
        fileExtension = 'cypher';
        break;
      default:
        exportData = JSON.stringify(graphData, null, 2);
        mimeType = 'application/json';
        fileExtension = 'json';
    }
    
    // Create blob and download link
    const blob = new Blob([exportData], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `knowledge_graph_${selectedEntity.id}.${fileExtension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Force cluster function for type-based clustering
  const forceCluster = () => {
    const strength = 0.15;
    let nodes;

    function force(alpha) {
      // Group nodes by type
      const centroids = {};
      const typeGroups = {};
      
      nodes.forEach(d => {
        if (!typeGroups[d.type]) {
          typeGroups[d.type] = [];
        }
        typeGroups[d.type].push(d);
      });
      
      // Calculate centroid for each group
      Object.keys(typeGroups).forEach(type => {
        const group = typeGroups[type];
        let x = 0, y = 0;
        
        group.forEach(node => {
          x += node.x;
          y += node.y;
        });
        
        centroids[type] = {
          x: x / group.length,
          y: y / group.length
        };
      });
      
      // Apply forces toward centroids
      nodes.forEach(d => {
        const centroid = centroids[d.type];
        d.vx += (centroid.x - d.x) * strength * alpha;
        d.vy += (centroid.y - d.y) * strength * alpha;
      });
    }
    
    force.initialize = (_) => nodes = _;
    
    return force;
  };

  const renderGraph = () => {
    if (!svgRef.current || !graphData) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();

    const width = graphContainerRef.current.clientWidth;
    const height = Math.max(500, graphContainerRef.current.clientHeight);
    
    // Apply dark mode if enabled
    if (visualizationSettings.darkMode) {
      d3.select(svgRef.current).style("background-color", "#1a1a1a");
    } else {
      d3.select(svgRef.current).style("background-color", "transparent");
    }

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Define simulation with settings from visualization options
    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-visualizationSettings.forceStrength))
      .force("center", d3.forceCenter(width / 2, height / 2));
      
    // Add cluster force if enabled
    if (visualizationSettings.clusterByType) {
      simulation.force("x", d3.forceX(width / 2).strength(0.1))
               .force("y", d3.forceY(height / 2).strength(0.1))
               .force("cluster", forceCluster())
    }

    // Create links
    const link = svg.append("g")
      .selectAll("line")
      .data(graphData.links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5);

    // Create nodes
    const node = svg.append("g")
      .selectAll("circle")
      .data(graphData.nodes)
      .join("circle")
      .attr("r", d => d.id === selectedEntity.id ? visualizationSettings.nodeSize + 3 : visualizationSettings.nodeSize)
      .attr("fill", d => entityColors[d.type] || entityColors.default)
      .attr("stroke", d => visualizationSettings.highlightConnections && d.id === selectedEntity.id ? "#000" : "none")
      .attr("stroke-width", 2)
      .call(drag(simulation));

    // Add labels if enabled
    const label = visualizationSettings.showLabels ? svg.append("g")
      .selectAll("text")
      .data(graphData.nodes)
      .join("text")
      .text(d => d.name)
      .attr("font-size", 10)
      .attr("dx", 12)
      .attr("dy", 4)
      .attr("opacity", 0.9)
      .attr("fill", visualizationSettings.darkMode ? "#fff" : "#000")
      .attr("stroke", visualizationSettings.darkMode ? "#000" : "#fff")
      .attr("stroke-width", 0.3)
      .attr("stroke-opacity", 0.8) : null;
      
    // Add relationship labels if enabled
    if (visualizationSettings.showRelationshipLabels) {
      svg.append("g")
        .selectAll("text")
        .data(graphData.links)
        .join("text")
        .text(d => d.type)
        .attr("font-size", 8)
        .attr("fill", "#666")
        .attr("text-anchor", "middle")
        .attr("dy", -3);
    }

    // Add titles for hover
    node.append("title")
      .text(d => `${d.name} (${d.type})`);

    // Update positions on tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      if (visualizationSettings.showLabels && label) {
        label
          .attr("x", d => d.x)
          .attr("y", d => d.y);
      }
      
      if (visualizationSettings.showRelationshipLabels) {
        svg.selectAll("text:not(.node-label)")
          .attr("x", d => (d.source.x + d.target.x) / 2)
          .attr("y", d => (d.source.y + d.target.y) / 2);
      }
    });

    // Define drag behavior
    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      
      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      
      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Knowledge Graph Explorer
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Search, visualize, and explore relationships between AI research entities.
      </Typography>
      {!searchResults.length && !selectedEntity && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2">Getting Started</Typography>
          <Typography variant="body2">
            1. Search for entities like "transformer" or "BERT"<br />
            2. Select an entity from the results to view details<br />
            3. Explore the visualization and try different settings<br />
            4. Use advanced options for research analysis
          </Typography>
        </Alert>
      )}
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
                                if (graphData) renderGraph();
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
                                if (graphData) renderGraph();
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
                                if (graphData) renderGraph();
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
                                if (graphData) renderGraph();
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
                            nodeSize: newValue
                          });
                          if (graphData) renderGraph();
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
                            maxRelationshipDepth: newValue
                          })}
                          step={1}
                          marks
                          min={1}
                          max={5}
                          valueLabelDisplay="auto"
                        />
                      </Tooltip>
                    </Grid>
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
                          <IconButton 
                            color="primary" 
                            onClick={handleExportGraph}
                            disabled={!graphData}
                            sx={{ ml: 1 }}
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ height: '75vh', overflowY: 'auto' }}>
            {loading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                <CircularProgress />
              </Box>
            ) : searchResults.length > 0 ? (
              <List>
                {searchResults.map((entity) => (
                  <React.Fragment key={entity.id}>
                    <ListItem 
                      button 
                      onClick={() => handleSelectEntity(entity)}
                      selected={selectedEntity && selectedEntity.id === entity.id}
                    >
                      <ListItemText 
                        primary={entity.name} 
                        secondary={
                          <Box display="flex" alignItems="center" mt={0.5}>
                            <Chip 
                              label={entity.type} 
                              size="small" 
                              sx={{ 
                                backgroundColor: entityColors[entity.type] || entityColors.default,
                                color: 'white',
                                mr: 1
                              }} 
                            />
                            <Typography variant="caption" color="text.secondary">
                              Relevance: {entity.relevance || 'N/A'}
                            </Typography>
                          </Box>
                        } 
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box p={3} textAlign="center">
                <Typography variant="body1" color="text.secondary">
                  {searchTerm ? 'No results found. Try a different search term.' : 'Search for entities to begin exploring.'}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ height: '25vh', overflowY: 'auto', p: 2 }}>
                {selectedEntity ? (
                  loading ? (
                    <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                      <CircularProgress />
                    </Box>
                  ) : entityDetails ? (
                    <Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h5" component="h2" sx={{ fontWeight: 'medium' }}>
                          {entityDetails.name}
                        </Typography>
                        <Chip 
                          label={entityDetails.type} 
                          size="medium" 
                          sx={{
                            backgroundColor: entityColors[entityDetails.type] || entityColors.default,
                            color: 'white',
                            fontWeight: 'bold',
                            paddingX: 1
                          }}
                        />
                      </Box>
                      <Divider sx={{ my: 2 }} />
                      <Box sx={{ maxHeight: '18vh', overflowY: 'auto', pr: 1 }}>
                        <Grid container spacing={2}>
                          {entityDetails.properties && Object.entries(entityDetails.properties).map(([key, value]) => (
                            <Grid item xs={12} sm={6} key={key}>
                              <Paper 
                                variant="outlined" 
                                sx={{ 
                                  p: 1, 
                                  display: 'flex', 
                                  flexDirection: 'column',
                                  height: '100%',
                                  bgcolor: 'background.default'
                                }}
                              >
                                <Typography 
                                  variant="caption" 
                                  color="text.secondary" 
                                  component="div"
                                  sx={{ textTransform: 'uppercase', fontWeight: 'bold', fontSize: '0.65rem' }}
                                >
                                  {key}
                                </Typography>
                                <Typography 
                                  variant="body2" 
                                  component="div" 
                                  sx={{ 
                                    fontWeight: key === 'citations' || key === 'complexity' ? 'medium' : 'regular',
                                    color: key === 'citations' ? 'success.main' : 'text.primary'
                                  }}
                                >
                                  {value}
                                </Typography>
                              </Paper>
                            </Grid>
                          ))}
                        </Grid>
                        {entityDetails.description && (
                          <>
                            <Divider sx={{ my: 2 }} />
                            <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                              {entityDetails.description}
                            </Typography>
                          </>
                        )}
                      </Box>
                    </Box>
                  ) : (
                    <Typography variant="body1" align="center">No details available</Typography>
                  )
                ) : (
                  <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                    <Typography variant="body1" color="text.secondary">
                      Select an entity to view details
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper 
                variant="outlined" 
                sx={{ height: '48vh', p: 2 }}
                ref={graphContainerRef}
              >
                {graphLoading ? (
                  <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                    <CircularProgress />
                  </Box>
                ) : selectedEntity ? (
                  <Box position="relative" height="100%">
                    <Box position="absolute" top={10} right={10} zIndex={1000} bgcolor="rgba(255,255,255,0.7)" borderRadius="4px" p={0.5}>
                      <Tooltip title={`Download visualization as ${exportFormat.toUpperCase()}`}>
                        <IconButton 
                          size="small" 
                          sx={{ mr: 1 }} 
                          onClick={handleExportGraph}
                          color="primary"
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Share visualization (copy link to clipboard)">
                        <IconButton 
                          size="small" 
                          sx={{ mr: 1 }}
                          color="primary"
                          onClick={() => {
                            navigator.clipboard.writeText(window.location.href);
                            // Show toast or notification (simplified here)
                            alert("Link copied to clipboard");
                          }}
                        >
                          <ShareIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="View visualization help">
                        <IconButton 
                          size="small"
                          color="primary"
                          onClick={() => {
                            setAdvancedSearchOpen(true);
                          }}
                        >
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    {analysisSettings.showCentralityMetrics && (
                      <Box 
                        position="absolute" 
                        bottom={10} 
                        left={10} 
                        zIndex={1000} 
                        p={1.5} 
                        bgcolor="rgba(255,255,255,0.9)" 
                        borderRadius="4px"
                        boxShadow="0 1px 3px rgba(0,0,0,0.12)"
                        border="1px solid rgba(25, 118, 210, 0.3)"
                      >
                        <Typography variant="caption" component="div" fontWeight="bold" color="primary.main">
                          Network Metrics
                        </Typography>
                        <Divider sx={{ my: 0.5 }} />
                        <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={1}>
                          <Typography variant="caption" component="div" fontWeight="medium">Nodes:</Typography>
                          <Typography variant="caption" component="div" color="text.secondary">{graphData?.nodes.length || 0}</Typography>
                          
                          <Typography variant="caption" component="div" fontWeight="medium">Relationships:</Typography>
                          <Typography variant="caption" component="div" color="text.secondary">{graphData?.links.length || 0}</Typography>
                          
                          <Typography variant="caption" component="div" fontWeight="medium">Density:</Typography>
                          <Typography variant="caption" component="div" color="text.secondary">
                            {((graphData?.links.length || 0) / ((graphData?.nodes.length || 0) * ((graphData?.nodes.length || 0) - 1) / 2)).toFixed(3)}
                          </Typography>
                          
                          <Typography variant="caption" component="div" fontWeight="medium">Key Node:</Typography>
                          <Typography variant="caption" component="div" color="text.secondary">{selectedEntity?.name}</Typography>
                        </Box>
                      </Box>
                    )}
                    
                    {analysisSettings.identifyResearchFrontiers && (
                      <Box 
                        position="absolute" 
                        top={10} 
                        left={10} 
                        zIndex={1000} 
                        p={1.5} 
                        bgcolor="rgba(255,255,255,0.9)" 
                        borderRadius="4px"
                        boxShadow="0 1px 3px rgba(0,0,0,0.12)"
                        border="1px solid rgba(25, 118, 210, 0.3)"
                      >
                        <Typography variant="caption" component="div" fontWeight="bold" color="primary.main">
                          Research Frontiers
                        </Typography>
                        <Divider sx={{ my: 0.5 }} />
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mt: 0.5 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Chip size="small" label="Emerging Field" 
                              sx={{ backgroundColor: '#8BC34A', color: 'white', fontSize: '0.7rem', height: 20, mr: 1 }} 
                            />
                            <Typography variant="caption" color="text.secondary">New direction (25%)</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Chip size="small" label="Active Research" 
                              sx={{ backgroundColor: '#FFC107', color: 'white', fontSize: '0.7rem', height: 20, mr: 1 }} 
                            />
                            <Typography variant="caption" color="text.secondary">High activity (45%)</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Chip size="small" label="Core Knowledge" 
                              sx={{ backgroundColor: '#9C27B0', color: 'white', fontSize: '0.7rem', height: 20, mr: 1 }} 
                            />
                            <Typography variant="caption" color="text.secondary">Foundation (30%)</Typography>
                          </Box>
                        </Box>
                      </Box>
                    )}
                    
                    <svg ref={svgRef} width="100%" height="100%"></svg>
                  </Box>
                ) : (
                  <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height="100%">
                    <Typography variant="h6" color="primary" gutterBottom>
                      Knowledge Graph Visualization
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 2, textAlign: 'center' }}>
                      Select an entity from the search results to visualize its relationships
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ maxWidth: 600, px: 3 }}>
                      <Grid item xs={4}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 2, 
                            height: '100%', 
                            border: '1px solid rgba(0,0,0,0.12)',
                            borderRadius: '8px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <SearchIcon color="action" sx={{ fontSize: 40, mb: 1, opacity: 0.7 }} />
                          <Typography variant="subtitle2" textAlign="center">
                            Search for entities
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={4}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 2, 
                            height: '100%', 
                            border: '1px solid rgba(0,0,0,0.12)',
                            borderRadius: '8px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <TuneIcon color="action" sx={{ fontSize: 40, mb: 1, opacity: 0.7 }} />
                          <Typography variant="subtitle2" textAlign="center">
                            Configure visualization
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid item xs={4}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 2, 
                            height: '100%', 
                            border: '1px solid rgba(0,0,0,0.12)',
                            borderRadius: '8px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <DownloadIcon color="action" sx={{ fontSize: 40, mb: 1, opacity: 0.7 }} />
                          <Typography variant="subtitle2" textAlign="center">
                            Export results
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                    
                    <Alert severity="info" sx={{ mt: 3, maxWidth: 500 }}>
                      <Typography variant="subtitle2">Quick Tips</Typography>
                      <Typography variant="body2">
                        • Use the search bar to find entities by name or type<br />
                        • Try "transformer", "BERT", or "attention" to explore related concepts<br />
                        • Enable advanced options to customize the visualization<br />
                        • Use analysis tools to discover research trends and patterns
                      </Typography>
                    </Alert>
                  </Box>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default KnowledgeGraphPage;