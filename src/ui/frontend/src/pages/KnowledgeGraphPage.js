import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  IconButton,
  Snackbar,
  Portal
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TuneIcon from '@mui/icons-material/Tune';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoIcon from '@mui/icons-material/Info';
import DownloadIcon from '@mui/icons-material/Download';
import ShareIcon from '@mui/icons-material/Share';
import AccessibilityIcon from '@mui/icons-material/Accessibility';
import SpeedIcon from '@mui/icons-material/Speed';
import * as d3 from 'd3';
import knowledgeGraphService from '../services/knowledgeGraphService';
import { 
  getFilteredNodes, 
  createNodeSizeScale, 
  calculateLevelOfDetail,
  createOptimizedForceParameters,
  getNavigableNode,
  findRelatedNodes
} from '../utils/graphUtils';
import KnowledgeGraphAccessibility from '../components/KnowledgeGraphAccessibility';

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
    levelOfDetail: true,
    useWebGL: false,
    useWorkerThread: false,
    progressiveLoading: true,
  });
  
  // Accessibility settings
  const [accessibilitySettings, setAccessibilitySettings] = useState({
    highContrastMode: false,
    largeNodeSize: false,
    showTextualAlternative: false,
    keyboardNavigationEnabled: true,
    reducedMotion: false,
    colorBlindMode: 'none',
    minimumLabelSize: 10,
    screenReaderAnnouncements: 'minimal'
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
  
  // UI state
  const [exportFormat, setExportFormat] = useState('json');
  const [accessibilityDialogOpen, setAccessibilityDialogOpen] = useState(false);
  const [performanceInfoOpen, setPerformanceInfoOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [focusedNodeId, setFocusedNodeId] = useState(null);
  const [currentZoom, setCurrentZoom] = useState(1);
  
  // Worker refs
  const simulationWorker = useRef(null);
  const rendererRef = useRef(null);
  const zoomRef = useRef(null);

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

    // Performance measurement
    const startTime = performance.now();

    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();

    const width = graphContainerRef.current.clientWidth;
    const height = Math.max(500, graphContainerRef.current.clientHeight);
    
    // Apply color theme based on settings
    if (visualizationSettings.darkMode || accessibilitySettings.highContrastMode) {
      const bgColor = accessibilitySettings.highContrastMode ? "#000000" : "#1a1a1a";
      d3.select(svgRef.current).style("background-color", bgColor);
    } else {
      d3.select(svgRef.current).style("background-color", "transparent");
    }

    // Add accessibility attributes
    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .attr("role", "img")
      .attr("tabindex", "0")
      .attr("aria-label", `Knowledge graph visualization with ${graphData.nodes.length} nodes and ${graphData.links.length} links`);
    
    // Create main container groups
    const container = svg.append("g").attr("class", "graph-container");
    const linksGroup = container.append("g").attr("class", "links");
    const nodesGroup = container.append("g").attr("class", "nodes");
    const labelsGroup = container.append("g").attr("class", "labels");
    
    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 8])
      .on("zoom", (event) => {
        container.attr("transform", event.transform);
        
        // Store current zoom level for level-of-detail rendering
        const newZoom = event.transform.k;
        setCurrentZoom(newZoom);
        
        if (visualizationSettings.levelOfDetail) {
          // Update visual elements based on zoom level
          const lod = calculateLevelOfDetail(newZoom, graphData.nodes.length);
          
          // Apply level of detail changes
          nodesGroup.selectAll("circle")
            .attr("stroke-width", lod.nodeBorderWidth)
            .attr("opacity", lod.nodeOpacity)
            .attr("r", d => {
              const baseSize = d.id === selectedEntity?.id 
                ? visualizationSettings.nodeSize + 3 
                : visualizationSettings.nodeSize;
              return baseSize * lod.nodeRadiusMultiplier;
            });
          
          linksGroup.selectAll("line")
            .attr("stroke-opacity", lod.linkOpacity);
          
          // Show/hide labels based on zoom level
          labelsGroup.style("display", lod.showLabels ? "block" : "none");
          if (lod.showLabels) {
            labelsGroup.selectAll("text")
              .attr("font-size", lod.labelFontSize);
          }
        }
      });
    
    svg.call(zoom);
    zoomRef.current = zoom;
    
    // Store optimal force simulation parameters
    const forceParams = createOptimizedForceParameters(
      graphData.nodes,
      visualizationSettings
    );

    // Define simulation with optimized settings
    const simulation = d3.forceSimulation(graphData.nodes)
      .alpha(0.3)
      .alphaDecay(forceParams.alphaDecay)
      .alphaMin(forceParams.alphaMin)
      .velocityDecay(forceParams.velocityDecay)
      .force("link", d3.forceLink(graphData.links)
        .id(d => d.id)
        .distance(forceParams.linkDistance))
      .force("charge", d3.forceManyBody()
        .strength(forceParams.chargeStrength))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide()
        .radius(forceParams.collisionRadius));
      
    // Add cluster force if enabled
    if (visualizationSettings.clusterByType) {
      simulation
        .force("x", d3.forceX(width / 2).strength(0.1))
        .force("y", d3.forceY(height / 2).strength(0.1))
        .force("cluster", forceCluster());
    }
    
    // Create dynamic node size scale based on connection count
    const nodeSizeScale = createNodeSizeScale(
      graphData.nodes, 
      graphData.links, 
      accessibilitySettings.largeNodeSize 
        ? visualizationSettings.nodeSize * 1.5 
        : visualizationSettings.nodeSize
    );

    // Get color mapping for nodes based on accessibility settings
    const getNodeColor = (node) => {
      let baseColor = entityColors[node.type] || entityColors.default;
      
      // Apply color blind modes
      if (accessibilitySettings.colorBlindMode !== 'none') {
        switch (accessibilitySettings.colorBlindMode) {
          case 'deuteranopia': // Red-green color blindness
            if (baseColor === '#4285F4') return '#4285F4'; // Keep blue
            if (baseColor === '#EA4335') return '#FFA500'; // Red -> Orange
            if (baseColor === '#34A853') return '#FFEA00'; // Green -> Yellow
            return baseColor;
          case 'protanopia': // Another type of red-green color blindness
            if (baseColor === '#4285F4') return '#4285F4'; // Keep blue
            if (baseColor === '#EA4335') return '#FFD700'; // Red -> Gold
            if (baseColor === '#34A853') return '#CDDC39'; // Green -> Lime
            return baseColor;
          case 'tritanopia': // Blue-yellow color blindness
            if (baseColor === '#4285F4') return '#7B1FA2'; // Blue -> Purple
            if (baseColor === '#FBBC05') return '#FF5722'; // Yellow -> Orange-red
            return baseColor;
          default:
            return baseColor;
        }
      }
      
      // Apply high contrast mode if enabled
      if (accessibilitySettings.highContrastMode) {
        // Brighten colors for high contrast
        if (baseColor === '#757575') return '#FFFFFF'; // Default gray to white
        return baseColor;
      }
      
      return baseColor;
    };

    // Create links with improved styling
    const link = linksGroup
      .selectAll("line")
      .data(graphData.links)
      .join("line")
      .attr("stroke", d => visualizationSettings.darkMode ? "#666" : "#999")
      .attr("stroke-opacity", visualizationSettings.darkMode ? 0.8 : 0.6)
      .attr("stroke-width", 1.5)
      .attr("data-source", d => typeof d.source === 'object' ? d.source.id : d.source)
      .attr("data-target", d => typeof d.target === 'object' ? d.target.id : d.target)
      .attr("data-type", d => d.type)
      .attr("aria-label", d => {
        const source = typeof d.source === 'object' ? d.source.name : 'unknown';
        const target = typeof d.target === 'object' ? d.target.name : 'unknown';
        return `Relationship: ${source} ${d.type} ${target}`;
      });

    // Create nodes with accessibility attributes
    const node = nodesGroup
      .selectAll("circle")
      .data(graphData.nodes)
      .join("circle")
      .attr("r", d => nodeSizeScale(d))
      .attr("fill", d => getNodeColor(d))
      .attr("stroke", d => {
        if (d.id === focusedNodeId) return "#ffeb3b"; // Yellow highlight for keyboard focus
        if (visualizationSettings.highlightConnections && d.id === selectedEntity?.id) {
          return accessibilitySettings.highContrastMode ? "#FFFFFF" : "#000000";
        }
        return "none";
      })
      .attr("stroke-width", d => d.id === focusedNodeId ? 3 : 2)
      .attr("data-id", d => d.id)
      .attr("data-type", d => d.type)
      .attr("tabindex", -1) // For keyboard navigation
      .attr("role", "button")
      .attr("aria-label", d => `${d.name}, ${d.type}`)
      .call(drag(simulation));

    // Add labels with proper scaling
    if (visualizationSettings.showLabels) {
      const labelFontSize = Math.max(
        10, 
        accessibilitySettings.minimumLabelSize
      );
      
      const label = labelsGroup
        .selectAll("text")
        .data(graphData.nodes)
        .join("text")
        .attr("class", "node-label")
        .text(d => d.name)
        .attr("font-size", labelFontSize)
        .attr("dx", d => nodeSizeScale(d) + 4)
        .attr("dy", 4)
        .attr("opacity", 0.9)
        .attr("fill", accessibilitySettings.highContrastMode 
          ? "#FFFFFF" 
          : (visualizationSettings.darkMode ? "#fff" : "#000"))
        .attr("stroke", accessibilitySettings.highContrastMode
          ? "#000000"
          : (visualizationSettings.darkMode ? "#000" : "#fff"))
        .attr("stroke-width", 0.3)
        .attr("stroke-opacity", 0.8)
        .attr("pointer-events", "none") // Don't interfere with node clicks
        .attr("aria-hidden", "true"); // Labels are presentational
    }
      
    // Add relationship labels if enabled
    if (visualizationSettings.showRelationshipLabels) {
      labelsGroup
        .selectAll(".relationship-label")
        .data(graphData.links)
        .join("text")
        .attr("class", "relationship-label")
        .text(d => d.type)
        .attr("font-size", accessibilitySettings.minimumLabelSize * 0.8)
        .attr("fill", accessibilitySettings.highContrastMode 
          ? "#FFFFFF" 
          : "#666")
        .attr("text-anchor", "middle")
        .attr("dy", -3)
        .attr("pointer-events", "none")
        .attr("aria-hidden", "true");
    }

    // Add interaction handlers
    node
      .on("click", (event, d) => {
        // Find the entity in searchResults or use the node directly
        const clickedEntity = searchResults.find(entity => entity.id === d.id) || d;
        handleSelectEntity(clickedEntity);
        
        // Announce selection to screen readers
        if (accessibilitySettings.screenReaderAnnouncements !== 'minimal') {
          const announcement = document.getElementById('sr-announcement');
          if (announcement) {
            announcement.textContent = `Selected ${d.type}: ${d.name}`;
          }
        }
      })
      .on("mouseover", function(event, d) {
        d3.select(this).attr("stroke-width", 3);
        
        // Highlight connected nodes and links
        if (visualizationSettings.highlightConnections) {
          const connectedNodeIds = new Set();
          link.each(function(l) {
            if (l.source.id === d.id || l.target.id === d.id) {
              const targetId = l.source.id === d.id ? l.target.id : l.source.id;
              connectedNodeIds.add(targetId);
              d3.select(this).attr("stroke", "#ff5722").attr("stroke-width", 2);
            }
          });
          
          node.each(function(n) {
            if (connectedNodeIds.has(n.id)) {
              d3.select(this).attr("stroke", "#ff5722").attr("stroke-width", 2);
            }
          });
        }
      })
      .on("mouseout", function(event, d) {
        d3.select(this).attr("stroke-width", d.id === focusedNodeId ? 3 : 
          (visualizationSettings.highlightConnections && d.id === selectedEntity?.id ? 2 : 0));
        
        // Reset highlights
        link.attr("stroke", visualizationSettings.darkMode ? "#666" : "#999")
            .attr("stroke-width", 1.5);
        
        node.each(function(n) {
          if (n.id !== selectedEntity?.id && n.id !== focusedNodeId) {
            d3.select(this).attr("stroke", "none");
          } else if (n.id === selectedEntity?.id) {
            d3.select(this).attr("stroke", accessibilitySettings.highContrastMode ? "#FFFFFF" : "#000000");
          }
        });
      });
      
    // Progressive loading animation if enabled
    if (visualizationSettings.progressiveLoading && !accessibilitySettings.reducedMotion) {
      // Start with nodes invisible
      node.attr("opacity", 0);
      link.attr("opacity", 0);
      
      // Fade in nodes and links progressively
      const delay = Math.min(5, 200 / Math.sqrt(graphData.nodes.length));
      
      node.transition()
        .delay((d, i) => i * delay)
        .duration(300)
        .attr("opacity", 1);
        
      link.transition()
        .delay((d, i) => i * delay * 0.5)
        .duration(200)
        .attr("opacity", 0.6);
    }

    // Update positions on tick with improved performance for large graphs
    simulation.on("tick", () => {
      // For very large graphs, limit updates for better performance
      if (graphData.nodes.length > 1000 && !accessibilitySettings.reducedMotion) {
        // Only update every few ticks
        if (simulation.alpha() < 0.1 || Math.random() < 0.2) {
          updatePositions();
        }
      } else {
        updatePositions();
      }
    });
    
    // Function to update positions of all elements
    function updatePositions() {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      if (visualizationSettings.showLabels) {
        labelsGroup.selectAll(".node-label")
          .attr("x", d => d.x)
          .attr("y", d => d.y);
      }
      
      if (visualizationSettings.showRelationshipLabels) {
        labelsGroup.selectAll(".relationship-label")
          .attr("x", d => (d.source.x + d.target.x) / 2)
          .attr("y", d => (d.source.y + d.target.y) / 2);
      }
    }
    
    // For reduced motion, run a static layout instead of animation
    if (accessibilitySettings.reducedMotion) {
      // Run simulation steps without animation
      for (let i = 0; i < forceParams.iterations; i++) {
        simulation.tick();
      }
      updatePositions();
      simulation.stop();
    }
    
    // Add keyboard navigation handlers (if enabled)
    if (accessibilitySettings.keyboardNavigationEnabled) {
      svg.on("keydown", (event) => {
        if (!graphData.nodes.length) return;
        
        switch (event.key) {
          case "ArrowRight":
          case "ArrowDown":
            event.preventDefault();
            const nextNode = getNavigableNode(focusedNodeId, graphData.nodes, 1);
            if (nextNode) {
              setFocusedNodeId(nextNode.id);
              focusNode(nextNode.id);
            }
            break;
            
          case "ArrowLeft":
          case "ArrowUp":
            event.preventDefault();
            const prevNode = getNavigableNode(focusedNodeId, graphData.nodes, -1);
            if (prevNode) {
              setFocusedNodeId(prevNode.id);
              focusNode(prevNode.id);
            }
            break;
            
          case "Home":
            event.preventDefault();
            if (graphData.nodes.length > 0) {
              setFocusedNodeId(graphData.nodes[0].id);
              focusNode(graphData.nodes[0].id);
            }
            break;
            
          case "End":
            event.preventDefault();
            if (graphData.nodes.length > 0) {
              setFocusedNodeId(graphData.nodes[graphData.nodes.length - 1].id);
              focusNode(graphData.nodes[graphData.nodes.length - 1].id);
            }
            break;
            
          case "Enter":
          case " ": // Space
            event.preventDefault();
            if (focusedNodeId) {
              const selectedNode = graphData.nodes.find(n => n.id === focusedNodeId);
              if (selectedNode) {
                handleSelectEntity(selectedNode);
              }
            }
            break;
            
          case "+":
          case "=":
            event.preventDefault();
            zoomRef.current.scaleBy(svg.transition().duration(300), 1.3);
            break;
            
          case "-":
            event.preventDefault();
            zoomRef.current.scaleBy(svg.transition().duration(300), 0.7);
            break;
            
          case "0":
            event.preventDefault();
            zoomRef.current.transform(svg.transition().duration(500), d3.zoomIdentity);
            break;
            
          case "Escape":
            event.preventDefault();
            setFocusedNodeId(null);
            break;
        }
      });
    }
    
    // Helper function to focus a specific node
    function focusNode(nodeId) {
      // Update visual highlight
      node.attr("stroke", d => {
        if (d.id === nodeId) return "#ffeb3b"; // Yellow highlight
        if (visualizationSettings.highlightConnections && d.id === selectedEntity?.id) {
          return accessibilitySettings.highContrastMode ? "#FFFFFF" : "#000000";
        }
        return "none";
      }).attr("stroke-width", d => d.id === nodeId ? 3 : 2);
      
      // Announce to screen readers
      if (accessibilitySettings.screenReaderAnnouncements !== 'minimal') {
        const focusedNode = graphData.nodes.find(n => n.id === nodeId);
        if (focusedNode) {
          const announcement = document.getElementById('sr-announcement');
          if (announcement) {
            // For verbose mode, include connected nodes
            if (accessibilitySettings.screenReaderAnnouncements === 'verbose') {
              const relatedIds = findRelatedNodes(nodeId, graphData.nodes, graphData.links, 3);
              const relatedNodes = relatedIds.map(id => {
                const node = graphData.nodes.find(n => n.id === id);
                return node ? node.name : '';
              }).filter(Boolean);
              
              const relatedText = relatedNodes.length > 0 
                ? `. Connected to: ${relatedNodes.join(', ')}` 
                : '';
                
              announcement.textContent = `Focused on ${focusedNode.type}: ${focusedNode.name}${relatedText}`;
            } else {
              announcement.textContent = `Focused on ${focusedNode.type}: ${focusedNode.name}`;
            }
          }
        }
      }
      
      // If the node is not visible in the current viewport, center it
      const focusedNodeElement = node.filter(d => d.id === nodeId).node();
      if (focusedNodeElement) {
        const boundingBox = focusedNodeElement.getBoundingClientRect();
        const containerBox = graphContainerRef.current.getBoundingClientRect();
        
        // Check if node is outside visible area
        if (boundingBox.left < containerBox.left || 
            boundingBox.right > containerBox.right ||
            boundingBox.top < containerBox.top ||
            boundingBox.bottom > containerBox.bottom) {
          
          const focusedNode = graphData.nodes.find(n => n.id === nodeId);
          if (focusedNode && focusedNode.x && focusedNode.y) {
            const transform = d3.zoomIdentity
              .translate(width/2 - focusedNode.x, height/2 - focusedNode.y)
              .scale(currentZoom);
              
            zoomRef.current.transform(svg.transition().duration(500), transform);
          }
        }
      }
    }

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
    
    // Record performance metrics
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    if (graphData.nodes.length > 500) {
      console.log(`Graph rendered in ${renderTime.toFixed(1)}ms (${graphData.nodes.length} nodes, ${graphData.links.length} links)`);
    }
  };

  // Create a Web Worker for simulation (if supported and enabled)
  useEffect(() => {
    if (visualizationSettings.useWorkerThread && window.Worker && !simulationWorker.current) {
      try {
        // Create a simple worker for force simulation
        const workerCode = `
          self.onmessage = function(e) {
            const { nodes, links, iterations, params } = e.data;
            
            // Run simulation
            const positions = runForceSimulation(nodes, links, iterations, params);
            self.postMessage(positions);
          };

          function runForceSimulation(nodes, links, iterations, params) {
            // Simple force-directed layout algorithm
            // In a real implementation, this would use a proper force simulation library
            const nodePositions = new Map();
            
            // Initialize positions if not provided
            nodes.forEach(node => {
              if (!nodePositions.has(node.id)) {
                nodePositions.set(node.id, {
                  x: node.x || Math.random() * params.width,
                  y: node.y || Math.random() * params.height
                });
              }
            });
            
            // Run simulation for fixed number of iterations
            for (let i = 0; i < iterations; i++) {
              // Apply forces
              // ... (simplified force calculation)
            }
            
            // Return updated positions
            return Array.from(nodePositions.entries()).map(([id, pos]) => ({
              id,
              x: pos.x,
              y: pos.y
            }));
          }
        `;
        
        const blob = new Blob([workerCode], { type: 'application/javascript' });
        const workerUrl = URL.createObjectURL(blob);
        simulationWorker.current = new Worker(workerUrl);
        
        // Set up message handler
        simulationWorker.current.onmessage = (e) => {
          const positions = e.data;
          // Update node positions with results from worker
          if (positions && graphData) {
            const updatedNodes = graphData.nodes.map(node => {
              const pos = positions.find(p => p.id === node.id);
              if (pos) {
                return { ...node, x: pos.x, y: pos.y };
              }
              return node;
            });
            
            setGraphData(prev => ({
              ...prev,
              nodes: updatedNodes
            }));
          }
        };
        
        // Clean up
        URL.revokeObjectURL(workerUrl);
      } catch (error) {
        console.error('Error creating Web Worker:', error);
        setNotification({
          open: true,
          message: 'Worker threads not supported in your browser. Using main thread.',
          severity: 'warning'
        });
      }
    }
    
    return () => {
      if (simulationWorker.current) {
        simulationWorker.current.terminate();
        simulationWorker.current = null;
      }
    };
  }, [visualizationSettings.useWorkerThread, graphData]);

  // WebGL Renderer setup (if supported and enabled)
  useEffect(() => {
    if (visualizationSettings.useWebGL && !rendererRef.current) {
      try {
        // Example WebGL setup (would be replaced with Three.js or similar)
        console.log('WebGL rendering would be enabled here using Three.js or similar');
        
        // In a real implementation, this would initialize a WebGL context
        // and render the graph using WebGL for improved performance with large graphs
      } catch (error) {
        console.error('Error initializing WebGL renderer:', error);
        setNotification({
          open: true,
          message: 'WebGL rendering not supported. Using SVG.',
          severity: 'warning'
        });
      }
    }
    
    return () => {
      // Clean up WebGL resources
      if (rendererRef.current) {
        // Dispose of WebGL context and resources
        rendererRef.current = null;
      }
    };
  }, [visualizationSettings.useWebGL]);

  // Handle loading real-world data for performance testing
  const handleLoadRealWorldData = async () => {
    setGraphLoading(true);
    try {
      const data = await knowledgeGraphService.getRealWorldGraph();
      
      if (data && data.nodes && data.nodes.length > 0) {
        setGraphData(data);
        setNotification({
          open: true,
          message: `Loaded real-world dataset with ${data.nodes.length} nodes and ${data.links.length} links`,
          severity: 'success'
        });
      } else {
        throw new Error('Invalid data format');
      }
    } catch (error) {
      console.error('Error loading real-world data:', error);
      setNotification({
        open: true,
        message: 'Failed to load real-world data. Using test data instead.',
        severity: 'error'
      });
      
      // Fall back to test data
      const testData = await knowledgeGraphService.getLargeTestGraph('large');
      setGraphData(testData);
    } finally {
      setGraphLoading(false);
    }
  };

  // Handle accessibility settings change
  const handleAccessibilitySettingsChange = (newSettings) => {
    setAccessibilitySettings(newSettings);
    setAccessibilityDialogOpen(false);
    
    // Apply settings immediately if there's a graph
    if (graphData) {
      renderGraph();
    }
    
    // Show confirmation
    setNotification({
      open: true,
      message: 'Accessibility settings updated',
      severity: 'success'
    });
  };

  return (
    <Box>
      {/* Screen reader announcements */}
      <div 
        id="sr-announcement" 
        role="status" 
        aria-live="polite" 
        style={{ 
          position: 'absolute', 
          width: '1px', 
          height: '1px', 
          margin: '-1px',
          padding: 0,
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          border: 0
        }}
      />
      
      {/* Accessibility Dialog */}
      {accessibilityDialogOpen && (
        <Portal>
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              bgcolor: 'rgba(0,0,0,0.5)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              p: 2
            }}
            onClick={() => setAccessibilityDialogOpen(false)}
          >
            <Box 
              sx={{ 
                maxWidth: '800px', 
                width: '100%', 
                maxHeight: '90vh', 
                overflowY: 'auto',
                onClick: e => e.stopPropagation()
              }}
              onClick={e => e.stopPropagation()}
            >
              <KnowledgeGraphAccessibility 
                settings={accessibilitySettings}
                onSettingsChange={handleAccessibilitySettingsChange}
              />
            </Box>
          </Box>
        </Portal>
      )}
      
      {/* Notifications */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        message={notification.message}
        severity={notification.severity}
      />
      
      <Typography variant="h4" component="h1" gutterBottom>
        Knowledge Graph Explorer
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Search, visualize, and explore relationships between AI research entities.
      </Typography>
      
      {/* Accessibility and performance buttons */}
      <Box sx={{ position: 'absolute', top: 20, right: 20, display: 'flex', gap: 1 }}>
        <Tooltip title="Accessibility Settings">
          <IconButton 
            color="primary" 
            onClick={() => setAccessibilityDialogOpen(true)}
            aria-label="Open accessibility settings"
          >
            <AccessibilityIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Load Real-World Test Data">
          <IconButton 
            color="primary" 
            onClick={handleLoadRealWorldData}
            aria-label="Load real-world test data"
            disabled={graphLoading}
          >
            <SpeedIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
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
                    
                    {/* Performance optimization settings */}
                    <Grid item xs={6} md={3}>
                      <Tooltip title="Adjust detail level based on zoom for better performance">
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={visualizationSettings.levelOfDetail}
                              onChange={(e) => {
                                setVisualizationSettings({
                                  ...visualizationSettings,
                                  levelOfDetail: e.target.checked
                                });
                                if (graphData) renderGraph();
                              }}
                              color="primary"
                            />
                          }
                          label="Level of Detail"
                        />
                      </Tooltip>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Tooltip title="Progressively load visual elements for better performance">
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={visualizationSettings.progressiveLoading}
                              onChange={(e) => {
                                setVisualizationSettings({
                                  ...visualizationSettings,
                                  progressiveLoading: e.target.checked
                                });
                                if (graphData) renderGraph();
                              }}
                              color="primary"
                            />
                          }
                          label="Progressive Load"
                        />
                      </Tooltip>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Tooltip title="Use WebGL rendering for large graphs (experimental)">
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={visualizationSettings.useWebGL}
                              onChange={(e) => {
                                setVisualizationSettings({
                                  ...visualizationSettings,
                                  useWebGL: e.target.checked
                                });
                                // WebGL requires a re-initialization
                                if (rendererRef.current) {
                                  rendererRef.current = null;
                                }
                                if (graphData) renderGraph();
                              }}
                              color="primary"
                            />
                          }
                          label="WebGL (Beta)"
                        />
                      </Tooltip>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Tooltip title="Use Web Worker for force simulation (experimental)">
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={visualizationSettings.useWorkerThread}
                              onChange={(e) => {
                                setVisualizationSettings({
                                  ...visualizationSettings,
                                  useWorkerThread: e.target.checked
                                });
                                if (graphData) renderGraph();
                              }}
                              color="primary"
                            />
                          }
                          label="Worker Thread"
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