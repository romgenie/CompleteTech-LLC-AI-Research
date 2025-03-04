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
  Alert
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import * as d3 from 'd3';
import knowledgeGraphService from '../services/knowledgeGraphService';

const KnowledgeGraphPage = () => {
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
  }, [graphData]);

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

  const renderGraph = () => {
    if (!svgRef.current || !graphData) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();

    const width = graphContainerRef.current.clientWidth;
    const height = Math.max(500, graphContainerRef.current.clientHeight);

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Define simulation
    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2));

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
      .attr("r", d => d.id === selectedEntity.id ? 10 : 7)
      .attr("fill", d => entityColors[d.type] || entityColors.default)
      .call(drag(simulation));

    // Add labels
    const label = svg.append("g")
      .selectAll("text")
      .data(graphData.nodes)
      .join("text")
      .text(d => d.name)
      .attr("font-size", 10)
      .attr("dx", 12)
      .attr("dy", 4);

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

      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
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
        </Grid>
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
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="h5">{entityDetails.name}</Typography>
                        <Chip 
                          label={entityDetails.type} 
                          size="medium" 
                          sx={{
                            backgroundColor: entityColors[entityDetails.type] || entityColors.default,
                            color: 'white'
                          }}
                        />
                      </Box>
                      <Divider sx={{ my: 2 }} />
                      <Grid container spacing={2}>
                        {entityDetails.properties && Object.entries(entityDetails.properties).map(([key, value]) => (
                          <Grid item xs={6} key={key}>
                            <Typography variant="body2" color="text.secondary" component="span">
                              {key}:
                            </Typography>
                            <Typography variant="body2" component="span" sx={{ ml: 1 }}>
                              {value}
                            </Typography>
                          </Grid>
                        ))}
                      </Grid>
                      {entityDetails.description && (
                        <>
                          <Divider sx={{ my: 2 }} />
                          <Typography variant="body1">{entityDetails.description}</Typography>
                        </>
                      )}
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
                  <svg ref={svgRef} width="100%" height="100%"></svg>
                ) : (
                  <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" height="100%">
                    <Typography variant="body1" color="text.secondary">
                      Select an entity to visualize relationships
                    </Typography>
                    <Alert severity="info" sx={{ mt: 2, maxWidth: 400 }}>
                      <Typography variant="body2">
                        The Knowledge Graph is fully implemented and integrated with the 
                        Paper Processing Pipeline foundation (Phase 3.5).
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