import React, { useState, useEffect, useRef, useMemo } from 'react';
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
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import TuneIcon from '@mui/icons-material/Tune';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoIcon from '@mui/icons-material/Info';
import DownloadIcon from '@mui/icons-material/Download';
import ShareIcon from '@mui/icons-material/Share';
import SpeedIcon from '@mui/icons-material/Speed';
import * as d3 from 'd3';
import knowledgeGraphService from '../services/knowledgeGraphService';
import { useSvgD3 } from '../hooks/useD3';
import { 
  getFilteredNodes, 
  createNodeSizeScale, 
  countNodeConnections, 
  createOptimizedForceParameters,
  generateTestData,
  calculateLevelOfDetail,
  getNavigableNode
} from '../utils/graphUtils';
import { knowledgeGraphColorSchemes } from '../theme';
import { useTheme } from '../contexts/ThemeContext';
import KnowledgeGraphAccessibility from '../components/KnowledgeGraphAccessibility';
import KnowledgeGraphTableView from '../components/KnowledgeGraphTableView';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import ToggleButton from '@mui/material/ToggleButton';
import ViewListIcon from '@mui/icons-material/ViewList';
import BubbleChartIcon from '@mui/icons-material/BubbleChart';

// Define TypeScript interfaces for the data structures
interface Entity {
  id: string;
  name: string;
  type: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  index?: number;
}

interface Relationship {
  source: string | Entity;
  target: string | Entity;
  type: string;
}

interface GraphData {
  nodes: Entity[];
  links: Relationship[];
}

interface EntityDetails extends Entity {
  description?: string;
  properties?: Record<string, any>;
}

const KnowledgeGraphPage = () => {
  // Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [entityDetails, setEntityDetails] = useState<EntityDetails | null>(null);
  const [relatedEntities, setRelatedEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(false);
  const [graphLoading, setGraphLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [entityType, setEntityType] = useState('all');
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [filteredGraphData, setFilteredGraphData] = useState<GraphData | null>(null);
  
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
    filterThreshold: 100,
    importanceThreshold: 0.5,
    progressiveLoading: false,
    levelOfDetail: true,
    tableView: false // Added table view toggle for accessibility
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
  
  // Benchmark mode
  const [benchmarkMode, setBenchmarkMode] = useState(false);
  const [benchmarkResults, setBenchmarkResults] = useState<{
    renderTime: number;
    frameRate: number;
    nodeCount: number;
    linkCount: number;
  } | null>(null);
  const [testDataSize, setTestDataSize] = useState(100);
  
  const graphContainerRef = useRef<HTMLDivElement | null>(null);

  // Track loaded node count for progressive loading
  const [loadedNodeCount, setLoadedNodeCount] = useState(0);
  const progressiveLoadingStep = 50; // Number of nodes to add each step
  
  // Get theme context for high contrast settings
  const { isHighContrast, isDarkMode } = useTheme();
  
  // Select appropriate color scheme based on theme settings
  const getColorScheme = () => {
    if (isHighContrast) {
      return isDarkMode 
        ? knowledgeGraphColorSchemes.highContrastDark
        : knowledgeGraphColorSchemes.highContrastLight;
    }
    return knowledgeGraphColorSchemes.standard;
  };
  
  // Colors for different entity types - dynamically updates with theme changes
  const entityColors = getColorScheme();

  // Performance metrics
  const fpsCounterRef = useRef(0);
  const lastFrameTimeRef = useRef(0);
  const frameDurationsRef = useRef<number[]>([]);
  const frameCountRef = useRef(0);

  useEffect(() => {
    // When selectedEntity changes, get its details and related entities
    if (selectedEntity) {
      fetchEntityDetails(selectedEntity.id);
      fetchRelatedEntities(selectedEntity.id);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedEntity]);
  
  // Re-render graph when theme changes (for high contrast mode)
  useEffect(() => {
    if (filteredGraphData && filteredGraphData.nodes.length > 0) {
      // Trigger a re-render of the graph with the new color scheme
      const currentNodeCount = loadedNodeCount;
      setLoadedNodeCount(0); // Reset to trigger re-render
      setTimeout(() => setLoadedNodeCount(currentNodeCount), 50); // Restore after brief delay
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isHighContrast, isDarkMode]);
  
  useEffect(() => {
    // Apply smart filtering to graph data
    if (graphData && graphData.nodes.length > 0) {
      if (graphData.nodes.length > (visualizationSettings.filterThreshold || 100)) {
        // Apply smart filtering for large graphs
        const filteredNodes = getFilteredNodes(
          graphData.nodes, 
          graphData.links,
          selectedEntity?.id || null,
          visualizationSettings
        );
        
        // Only keep links between filtered nodes
        const nodeIds = new Set(filteredNodes.map(node => node.id));
        const filteredLinks = graphData.links.filter(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
          return nodeIds.has(sourceId) && nodeIds.has(targetId);
        });
        
        setFilteredGraphData({ nodes: filteredNodes, links: filteredLinks });
        setLoadedNodeCount(visualizationSettings.progressiveLoading ? 
          Math.min(progressiveLoadingStep, filteredNodes.length) : 
          filteredNodes.length
        );
      } else {
        // For smaller graphs, no filtering needed
        setFilteredGraphData(graphData);
        setLoadedNodeCount(visualizationSettings.progressiveLoading ? 
          Math.min(progressiveLoadingStep, graphData.nodes.length) : 
          graphData.nodes.length
        );
      }
    } else {
      setFilteredGraphData(null);
      setLoadedNodeCount(0);
    }
  }, [graphData, visualizationSettings.filterThreshold, visualizationSettings.importanceThreshold, selectedEntity, visualizationSettings.progressiveLoading]);

  // Store currently focused node for keyboard navigation
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const svgRef = useRef<SVGSVGElement | null>(null);
  
  // Use D3 hook for rendering
  const renderGraph = useSvgD3((svg) => {
    if (!svg.node() || !filteredGraphData || loadedNodeCount === 0) return;
    
    // Store ref for keyboard handlers
    svgRef.current = svg.node();
    
    const startTime = performance.now();
    
    // Clear previous graph
    svg.selectAll("*").remove();
    
    const width = graphContainerRef.current?.clientWidth || 800;
    const height = Math.max(500, graphContainerRef.current?.clientHeight || 600);
    
    // Apply dark mode if enabled
    if (visualizationSettings.darkMode) {
      svg.style("background-color", "#1a1a1a");
    } else {
      svg.style("background-color", "transparent");
    }
    
    // Set ARIA attributes for accessibility
    svg.attr("aria-label", "Knowledge Graph Visualization")
       .attr("role", "application")
       .attr("tabindex", "0");
    
    // Get only the nodes to render based on progressive loading
    const nodesToRender = filteredGraphData.nodes.slice(0, loadedNodeCount);
    const nodeIds = new Set(nodesToRender.map(node => node.id));
    
    // Only include links where both nodes are being rendered
    const linksToRender = filteredGraphData.links.filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });
    
    // Create the visualization container
    const vis = svg.append("g")
      .attr("class", "visualization")
      .attr("aria-label", "Graph visualization containing " + 
            nodesToRender.length + " nodes and " + linksToRender.length + " relationships");
    
    // Get optimized force simulation parameters
    const forceParams = createOptimizedForceParameters(
      nodesToRender,
      visualizationSettings
    );
    
    // Create node size scale based on connections
    const nodeSizeScale = createNodeSizeScale(
      nodesToRender,
      linksToRender,
      visualizationSettings.nodeSize
    );
    
    // Define simulation with settings from visualization options
    const simulation = d3.forceSimulation(nodesToRender)
      .force("link", d3.forceLink(linksToRender)
        .id((d: any) => d.id)
        .distance(forceParams.linkDistance))
      .force("charge", d3.forceManyBody()
        .strength(forceParams.chargeStrength))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(forceParams.collisionRadius))
      .alphaDecay(forceParams.alphaDecay)
      .velocityDecay(forceParams.velocityDecay)
      .alphaMin(forceParams.alphaMin);
      
    // Add cluster force if enabled
    if (visualizationSettings.clusterByType) {
      simulation.force("x", d3.forceX(width / 2).strength(0.1))
               .force("y", d3.forceY(height / 2).strength(0.1))
               .force("cluster", forceCluster());
    }
    
    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 8])
      .on("zoom", (event) => {
        vis.attr("transform", event.transform);
        
        // Store current zoom level for accessibility features
        setZoomLevel(event.transform.k);
        
        // Level of detail adjustments based on zoom level
        if (visualizationSettings.levelOfDetail) {
          const scale = event.transform.k;
          const lodSettings = calculateLevelOfDetail(scale, nodesToRender.length);
          
          // Show/hide labels based on zoom level
          vis.selectAll("text.node-label")
            .style("display", d => {
              // TypeScript needs a special accessor pattern for this to work
              const nodeData = d as Entity;
              return nodeData.id === selectedEntity?.id || nodeData.id === focusedNodeId || 
                     lodSettings.showLabels ? "block" : "none";
            })
            .attr("font-size", lodSettings.labelFontSize);
          
          // Show relationship labels only at higher zoom levels
          vis.selectAll("text.relationship-label")
            .style("display", lodSettings.showRelationshipLabels ? "block" : "none");
            
          // Adjust node size based on zoom
          vis.selectAll("circle.node")
            .attr("r", d => {
              // TypeScript needs a special accessor pattern for this to work
              const nodeData = d as Entity;
              const baseSize = nodeSizeScale(nodeData);
              // Adjust size inversely to zoom to maintain visual size
              return baseSize / Math.sqrt(scale);
            });
            
          // Adjust stroke width based on zoom
          vis.selectAll("circle.node")
            .attr("stroke-width", d => {
              // TypeScript needs a special accessor pattern for this to work
              const nodeData = d as Entity;
              if (nodeData.id === selectedEntity?.id) return 2.5 / Math.sqrt(scale);
              if (nodeData.id === focusedNodeId) return 2 / Math.sqrt(scale);
              if (visualizationSettings.highlightConnections && 
                  isConnectedToSelected(nodeData.id)) return 1.5 / Math.sqrt(scale);
              return lodSettings.nodeBorderWidth;
            });
            
          // Adjust link opacity
          vis.selectAll("line.link")
            .attr("stroke-opacity", lodSettings.linkOpacity);
        }
      });
      
    svg.call(zoom);
    
    // Create links
    const link = vis.append("g")
      .attr("aria-label", "Graph relationships")
      .selectAll("line")
      .data(linksToRender)
      .join("line")
      .attr("class", "link")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5)
      .attr("aria-label", d => {
        const sourceId = typeof d.source === 'object' ? d.source.id : d.source;
        const targetId = typeof d.target === 'object' ? d.target.id : d.target;
        const sourceName = nodesToRender.find(node => node.id === sourceId)?.name || sourceId;
        const targetName = nodesToRender.find(node => node.id === targetId)?.name || targetId;
        return `Relationship: ${sourceName} ${d.type} ${targetName}`;
      });
    
    // Create nodes with dynamic size
    const node = vis.append("g")
      .attr("aria-label", "Graph nodes")
      .selectAll("circle")
      .data(nodesToRender)
      .join("circle")
      .attr("class", "node")
      .attr("r", d => nodeSizeScale(d as Entity))
      .attr("fill", d => entityColors[(d as Entity).type] || entityColors.default)
      .attr("stroke", d => getNodeStrokeColor(d as Entity))
      .attr("stroke-width", d => {
        const nodeData = d as Entity;
        if (nodeData.id === selectedEntity?.id) return 2;
        if (nodeData.id === focusedNodeId) return 1.5;
        return 1; 
      })
      .attr("tabindex", d => ((d as Entity).id === selectedEntity?.id || (d as Entity).id === focusedNodeId) ? 0 : -1)
      .attr("role", "button")
      .attr("aria-label", d => `${(d as Entity).type} node: ${(d as Entity).name}`)
      .attr("aria-pressed", d => (d as Entity).id === selectedEntity?.id ? "true" : "false")
      .call(drag(simulation))
      .on("click", (event, d) => {
        // Update selected entity when node is clicked
        handleSelectEntity(d as Entity);
        
        // Set focus to this node
        setFocusedNodeId((d as Entity).id);
        
        // Announce selection to screen readers
        announceToScreenReader(`Selected ${(d as Entity).type}: ${(d as Entity).name}`);
      })
      .on("keydown", (event, d) => {
        // Handle keyboard actions on nodes
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          handleSelectEntity(d as Entity);
          announceToScreenReader(`Selected ${(d as Entity).type}: ${(d as Entity).name}`);
        }
      })
      .on("focus", (event, d) => {
        // Update focused node when keyboard focus changes
        setFocusedNodeId((d as Entity).id);
        
        // Highlight node visually
        d3.select(event.currentTarget)
          .attr("stroke-width", 2)
          .attr("stroke", "#000");
      })
      .on("blur", (event, d) => {
        // Reset focus styling unless this is the selected node
        if ((d as Entity).id !== selectedEntity?.id) {
          d3.select(event.currentTarget)
            .attr("stroke-width", 1)
            .attr("stroke", getNodeStrokeColor(d as Entity));
        }
      });
    
    // Add labels if enabled
    if (visualizationSettings.showLabels) {
      const label = vis.append("g")
        .attr("aria-hidden", "true") // Hide from screen readers (node has aria-label already)
        .selectAll("text")
        .data(nodesToRender)
        .join("text")
        .attr("class", "node-label")
        .text(d => (d as Entity).name)
        .attr("font-size", 10)
        .attr("dx", 12)
        .attr("dy", 4)
        .attr("opacity", 0.9)
        .attr("fill", visualizationSettings.darkMode ? "#fff" : "#000")
        .attr("stroke", visualizationSettings.darkMode ? "#000" : "#fff")
        .attr("stroke-width", 0.3)
        .attr("stroke-opacity", 0.8);
    }
      
    // Add relationship labels if enabled
    if (visualizationSettings.showRelationshipLabels) {
      vis.append("g")
        .attr("aria-hidden", "true") // Hide from screen readers (link has aria-label already)
        .selectAll("text")
        .data(linksToRender)
        .join("text")
        .attr("class", "relationship-label")
        .text(d => d.type)
        .attr("font-size", 8)
        .attr("fill", "#666")
        .attr("text-anchor", "middle")
        .attr("dy", -3);
    }
    
    // Add titles for hover
    node.append("title")
      .text(d => `${(d as Entity).name} (${(d as Entity).type})`);
    
    // Create an element for screen reader announcements
    const announcer = d3.select("body")
      .selectAll("#sr-announcer")
      .data([0]) // Ensure we only create this once
      .join("div")
      .attr("id", "sr-announcer")
      .attr("role", "status")
      .attr("aria-live", "polite")
      .style("position", "absolute")
      .style("width", "1px")
      .style("height", "1px")
      .style("padding", "0")
      .style("margin", "-1px")
      .style("overflow", "hidden")
      .style("clip", "rect(0, 0, 0, 0)")
      .style("white-space", "nowrap")
      .style("border", "0");
    
    // Set up keyboard navigation for the SVG
    svg.on("keydown", (event) => {
      // Handle arrow keys, Enter, space, etc.
      switch (event.key) {
        case "ArrowRight":
          navigateToNode(1);
          event.preventDefault();
          break;
          
        case "ArrowLeft":
          navigateToNode(-1);
          event.preventDefault();
          break;
          
        case "Home":
          navigateToFirstNode();
          event.preventDefault();
          break;
          
        case "End":
          navigateToLastNode();
          event.preventDefault();
          break;
          
        case "+":
        case "=":
          zoomIn();
          event.preventDefault();
          break;
          
        case "-":
          zoomOut();
          event.preventDefault();
          break;
          
        case "0":
          resetZoom();
          event.preventDefault();
          break;
          
        case "s":
          if (focusedNodeId) {
            // Select the currently focused node
            const focusedNode = nodesToRender.find(n => n.id === focusedNodeId);
            if (focusedNode) {
              handleSelectEntity(focusedNode);
              announceToScreenReader(`Selected ${focusedNode.type}: ${focusedNode.name}`);
            }
          }
          event.preventDefault();
          break;
      }
    });
    
    // Helper functions for keyboard navigation
    function navigateToNode(direction: 1 | -1) {
      const nextNode = getNavigableNode(focusedNodeId, nodesToRender, direction);
      if (nextNode) {
        // Focus the node
        setFocusedNodeId(nextNode.id);
        
        // Find and focus the DOM element
        const nodeElement = svg.selectAll("circle.node").filter(d => (d as Entity).id === nextNode.id).node();
        if (nodeElement) {
          nodeElement.focus();
          
          // Pan to node
          const x = (nodesToRender[nextNode.index].x || 0);
          const y = (nodesToRender[nextNode.index].y || 0);
          const transform = d3.zoomTransform(svg.node());
          
          // Announce to screen readers
          const focusedNode = nodesToRender[nextNode.index];
          announceToScreenReader(`Focused ${focusedNode.type}: ${focusedNode.name}`);
          
          // Pan to make node visible
          svg.transition().duration(300).call(
            zoom.transform,
            d3.zoomIdentity
              .translate(width / 2 - x * transform.k, height / 2 - y * transform.k)
              .scale(transform.k)
          );
        }
      }
    }
    
    function navigateToFirstNode() {
      if (nodesToRender.length > 0) {
        setFocusedNodeId(nodesToRender[0].id);
        const nodeElement = svg.selectAll("circle.node").filter(d => (d as Entity).id === nodesToRender[0].id).node();
        if (nodeElement) {
          nodeElement.focus();
          announceToScreenReader(`Focused first node: ${nodesToRender[0].name}`);
        }
      }
    }
    
    function navigateToLastNode() {
      if (nodesToRender.length > 0) {
        const lastIndex = nodesToRender.length - 1;
        setFocusedNodeId(nodesToRender[lastIndex].id);
        const nodeElement = svg.selectAll("circle.node").filter(d => (d as Entity).id === nodesToRender[lastIndex].id).node();
        if (nodeElement) {
          nodeElement.focus();
          announceToScreenReader(`Focused last node: ${nodesToRender[lastIndex].name}`);
        }
      }
    }
    
    function zoomIn() {
      const currentTransform = d3.zoomTransform(svg.node());
      svg.transition().duration(300).call(
        zoom.transform,
        currentTransform.scale(currentTransform.k * 1.3)
      );
      announceToScreenReader("Zoomed in");
    }
    
    function zoomOut() {
      const currentTransform = d3.zoomTransform(svg.node());
      svg.transition().duration(300).call(
        zoom.transform,
        currentTransform.scale(currentTransform.k / 1.3)
      );
      announceToScreenReader("Zoomed out");
    }
    
    function resetZoom() {
      svg.transition().duration(500).call(
        zoom.transform,
        d3.zoomIdentity
      );
      announceToScreenReader("Zoom reset");
    }
    
    // Helper function for screen reader announcements
    function announceToScreenReader(message: string) {
      announcer.text(message);
    }
    
    // Update positions on tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => ((d.source as Entity).x))
        .attr("y1", d => ((d.source as Entity).y))
        .attr("x2", d => ((d.target as Entity).x))
        .attr("y2", d => ((d.target as Entity).y));
    
      node
        .attr("cx", d => (d as Entity).x)
        .attr("cy", d => (d as Entity).y);
    
      if (visualizationSettings.showLabels) {
        vis.selectAll("text.node-label")
          .attr("x", d => (d as Entity).x)
          .attr("y", d => (d as Entity).y);
      }
      
      if (visualizationSettings.showRelationshipLabels) {
        vis.selectAll("text.relationship-label")
          .attr("x", d => (((d.source as Entity).x + (d.target as Entity).x) / 2))
          .attr("y", d => (((d.source as Entity).y + (d.target as Entity).y) / 2));
      }
      
      // Track FPS for benchmarking
      if (benchmarkMode) {
        const now = performance.now();
        const elapsed = now - lastFrameTimeRef.current;
        
        if (lastFrameTimeRef.current !== 0) {
          frameDurationsRef.current.push(elapsed);
          if (frameDurationsRef.current.length > 100) {
            frameDurationsRef.current.shift();
          }
        }
        
        lastFrameTimeRef.current = now;
        frameCountRef.current++;
        
        // Update benchmark results every 30 frames
        if (frameCountRef.current % 30 === 0) {
          const avg = frameDurationsRef.current.reduce((a, b) => a + b, 0) / 
                      Math.max(1, frameDurationsRef.current.length);
          const fps = 1000 / avg;
          
          setBenchmarkResults({
            renderTime: performance.now() - startTime,
            frameRate: fps,
            nodeCount: nodesToRender.length,
            linkCount: linksToRender.length
          });
        }
      }
    });
    
    // Run simulation for a fixed number of steps for large graphs
    if (nodesToRender.length > 500) {
      simulation.stop();
      for (let i = 0; i < forceParams.iterations; ++i) simulation.tick();
    }
    
    const endTime = performance.now();
    
    if (benchmarkMode) {
      setBenchmarkResults(prev => ({
        ...(prev || {}),
        renderTime: endTime - startTime,
        nodeCount: nodesToRender.length,
        linkCount: linksToRender.length
      }));
    }
    
    // Helper function to get stroke color
    function getNodeStrokeColor(d: Entity): string {
      if (d.id === selectedEntity?.id) return "#000";
      if (d.id === focusedNodeId) return "#444";
      if (visualizationSettings.highlightConnections && isConnectedToSelected(d.id)) return "#555";
      return "#fff";
    }
    
    // Helper function to check if node is connected to selected
    function isConnectedToSelected(nodeId: string): boolean {
      if (!selectedEntity) return false;
      
      return !!linksToRender.find(link => {
        const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
        const targetId = typeof link.target === 'object' ? link.target.id : link.target;
        return (sourceId === selectedEntity.id && targetId === nodeId) || 
               (targetId === selectedEntity.id && sourceId === nodeId);
      });
    }
    
    // Force cluster function for type-based clustering
    function forceCluster() {
      const strength = 0.15;
      let nodes: Entity[];
    
      function force(alpha: number) {
        // Group nodes by type
        const centroids: Record<string, {x: number, y: number}> = {};
        const typeGroups: Record<string, Entity[]> = {};
        
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
            x += node.x || 0;
            y += node.y || 0;
          });
          
          centroids[type] = {
            x: x / group.length,
            y: y / group.length
          };
        });
        
        // Apply forces toward centroids
        nodes.forEach(d => {
          const centroid = centroids[d.type];
          if (d.vx !== undefined && d.vy !== undefined && centroid) {
            d.vx += (centroid.x - (d.x || 0)) * strength * alpha;
            d.vy += (centroid.y - (d.y || 0)) * strength * alpha;
          }
        });
      }
      
      force.initialize = function(_nodes: Entity[]) { 
        nodes = _nodes;
      };
      
      return force;
    }
    
    // Define drag behavior
    function drag(simulation: d3.Simulation<Entity, undefined>) {
      function dragstarted(event: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      
      function dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      
      function dragended(event: any) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }
  }, [filteredGraphData, loadedNodeCount, selectedEntity, visualizationSettings, benchmarkMode, focusedNodeId]);
  
  // Handle keyboard navigation for graph container
  const handleGraphKeydown = (event: React.KeyboardEvent) => {
    // Only handle keyboard when graph is loaded
    if (!filteredGraphData || !svgRef.current) return;
    
    // Pass keyboard events to the SVG
    const svgElement = svgRef.current;
    if (svgElement) {
      // Focus SVG if it's not already focused
      if (document.activeElement !== svgElement) {
        svgElement.focus();
      }
    }
  };

  const fetchEntityDetails = async (entityId: string) => {
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
  
  const fetchRelatedEntities = async (entityId: string) => {
    setGraphLoading(true);
    try {
      const data = await knowledgeGraphService.getRelatedEntities(entityId);
      setRelatedEntities(data.entities);
      
      // Prepare data for D3 graph
      const nodes = [
        { id: selectedEntity!.id, name: selectedEntity!.name, type: selectedEntity!.type },
        ...data.entities.map((entity: Entity) => ({ 
          id: entity.id, 
          name: entity.name, 
          type: entity.type 
        }))
      ];
      
      const links = data.relationships.map((rel: Relationship) => ({
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
      const relatedEntityIds = new Set<string>();
      relatedLinks.forEach(link => {
        if (link.source === entityId) {
          relatedEntityIds.add(link.target as string);
        } else {
          relatedEntityIds.add(link.source as string);
        }
      });
      
      // Get related entity nodes
      const relatedEntities = mockGraph.nodes.filter(node => 
        relatedEntityIds.has(node.id)
      );
      
      setRelatedEntities(relatedEntities);
      
      // Prepare graph data for visualization
      const nodes = [
        selectedEntity!,
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
      setFilteredGraphData(null);
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
      setFilteredGraphData(null);
      
      // Show message about using mock data
      setError('Using mock data for demonstration. In production, this would call the actual API.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSelectEntity = (entity: Entity) => {
    setSelectedEntity(entity);
  };
  
  const handleLoadMoreNodes = () => {
    if (!filteredGraphData) return;
    
    const newLoadedCount = Math.min(
      loadedNodeCount + progressiveLoadingStep,
      filteredGraphData.nodes.length
    );
    setLoadedNodeCount(newLoadedCount);
  };
  
  // Generate test data for benchmarking
  const generateBenchmarkData = () => {
    setGraphLoading(true);
    
    // Generate test data
    const testData = generateTestData(testDataSize);
    
    // Setup for visualization
    setSearchResults([]);
    
    // Use first node as selected entity
    const firstNode = testData.nodes[0];
    setSelectedEntity(firstNode);
    setEntityDetails({
      ...firstNode,
      description: "Test node for benchmarking large graph performance.",
      properties: {
        complexity: "High",
        domain: "Performance Testing",
        testSize: testDataSize
      }
    });
    
    setRelatedEntities(testData.nodes.slice(1, 20));
    setGraphData(testData);
    
    // Reset benchmark measurements
    frameCountRef.current = 0;
    lastFrameTimeRef.current = 0;
    frameDurationsRef.current = [];
    
    setGraphLoading(false);
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
        const linkRows = graphData.links.map(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
          return `${sourceId},${targetId},${link.type}`;
        }).join('\n');
        
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
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
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
    link.download = `knowledge_graph_${selectedEntity?.id}.${fileExtension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
                                // Reset to initial load if progressive loading is enabled
                                if (e.target.checked && filteredGraphData) {
                                  setLoadedNodeCount(Math.min(progressiveLoadingStep, filteredGraphData.nodes.length));
                                } else if (filteredGraphData) {
                                  setLoadedNodeCount(filteredGraphData.nodes.length);
                                }
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
                            setLoadedNodeCount(newValue as number);
                          }}
                          min={Math.min(progressiveLoadingStep, filteredGraphData.nodes.length)}
                          max={filteredGraphData.nodes.length}
                          step={Math.max(1, Math.floor(filteredGraphData.nodes.length / 10))}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${value} nodes`}
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
                          startIcon={<SpeedIcon />}
                          onClick={generateBenchmarkData}
                          disabled={benchmarkMode === false}
                          sx={{ mt: 1 }}
                        >
                          Generate Test Data & Benchmark
                        </Button>
                      </Box>
                    </Grid>
                    
                    {benchmarkResults && (
                      <Grid item xs={12}>
                        <Paper sx={{ p: 2, mt: 1, bgcolor: 'warning.light' }}>
                          <Typography variant="subtitle2" gutterBottom color="warning.dark">
                            Benchmark Results
                          </Typography>
                          <Grid container spacing={2}>
                            <Grid item xs={3}>
                              <Typography variant="body2" fontWeight="bold">Render Time:</Typography>
                              <Typography variant="body2">{benchmarkResults.renderTime.toFixed(2)} ms</Typography>
                            </Grid>
                            <Grid item xs={3}>
                              <Typography variant="body2" fontWeight="bold">Frame Rate:</Typography>
                              <Typography variant="body2">{benchmarkResults.frameRate.toFixed(1)} FPS</Typography>
                            </Grid>
                            <Grid item xs={3}>
                              <Typography variant="body2" fontWeight="bold">Nodes:</Typography>
                              <Typography variant="body2">{benchmarkResults.nodeCount}</Typography>
                            </Grid>
                            <Grid item xs={3}>
                              <Typography variant="body2" fontWeight="bold">Links:</Typography>
                              <Typography variant="body2">{benchmarkResults.linkCount}</Typography>
                            </Grid>
                          </Grid>
                        </Paper>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
      {error && (
        <Alert severity="info" sx={{ mb: 3 }}>
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
                                  {value?.toString()}
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
                onKeyDown={handleGraphKeydown}
                tabIndex={-1}
                role="region"
                aria-label="Knowledge Graph Visualization Area"
              >
                {graphLoading ? (
                  <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                    <CircularProgress />
                  </Box>
                ) : selectedEntity ? (
                  <Box position="relative" height="100%">
                    {/* Choose which view to render based on tableView setting */}
                    {visualizationSettings.tableView ? (
                      <KnowledgeGraphTableView 
                        graphData={filteredGraphData} 
                        selectedEntity={selectedEntity}
                        onSelectEntity={handleSelectEntity}
                      />
                    ) : (
                      <>
                        {/* View Toggle */}
                        <Box position="absolute" top={10} left={10} zIndex={1000} bgcolor="rgba(255,255,255,0.8)" borderRadius="4px" p={0.5}>
                          <ToggleButtonGroup
                            size="small"
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
                            <ToggleButton value="graph" aria-label="Visual graph">
                              <BubbleChartIcon />
                            </ToggleButton>
                            <ToggleButton value="table" aria-label="Table view">
                              <ViewListIcon />
                            </ToggleButton>
                          </ToggleButtonGroup>
                        </Box>
                        
                        {/* Control Panel */}
                        <Box position="absolute" top={10} right={10} zIndex={1000} bgcolor="rgba(255,255,255,0.8)" borderRadius="4px" p={0.5}>
                          <Tooltip title={`Download visualization as ${exportFormat.toUpperCase()}`}>
                            <IconButton 
                              size="small" 
                              sx={{ mr: 1 }} 
                              onClick={handleExportGraph}
                              color="primary"
                              aria-label="Download visualization"
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Share visualization (copy link to clipboard)">
                            <IconButton 
                              size="small" 
                              sx={{ mr: 1 }}
                              color="primary"
                              aria-label="Share visualization"
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
                              aria-label="View help"
                              onClick={() => {
                                setAdvancedSearchOpen(true);
                              }}
                            >
                              <InfoIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        
                        {/* Accessibility Keyboard Controls */}
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
                          aria-live="polite"
                        >
                          <Typography variant="caption" component="div" fontWeight="bold" color="primary.main">
                            Keyboard Navigation
                          </Typography>
                          <Divider sx={{ my: 0.5 }} />
                          <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={0.5}>
                            <Typography variant="caption" component="div" fontWeight="medium">←/→:</Typography>
                            <Typography variant="caption" component="div" color="text.secondary">Navigate nodes</Typography>
                            
                            <Typography variant="caption" component="div" fontWeight="medium">Home/End:</Typography>
                            <Typography variant="caption" component="div" color="text.secondary">First/Last node</Typography>
                            
                            <Typography variant="caption" component="div" fontWeight="medium">+/-:</Typography>
                            <Typography variant="caption" component="div" color="text.secondary">Zoom in/out</Typography>
                            
                            <Typography variant="caption" component="div" fontWeight="medium">Enter/Space:</Typography>
                            <Typography variant="caption" component="div" color="text.secondary">Select node</Typography>
                          </Box>
                        </Box>
                        
                        {/* Network Metrics Panel (if enabled) */}
                        {analysisSettings.showCentralityMetrics && filteredGraphData && (
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
                            aria-label="Network metrics panel"
                          >
                            <Typography variant="caption" component="div" fontWeight="bold" color="primary.main">
                              Network Metrics
                            </Typography>
                            <Divider sx={{ my: 0.5 }} />
                            <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={1}>
                              <Typography variant="caption" component="div" fontWeight="medium">Nodes:</Typography>
                              <Typography variant="caption" component="div" color="text.secondary">{filteredGraphData.nodes.length}</Typography>
                              
                              <Typography variant="caption" component="div" fontWeight="medium">Relationships:</Typography>
                              <Typography variant="caption" component="div" color="text.secondary">{filteredGraphData.links.length}</Typography>
                              
                              <Typography variant="caption" component="div" fontWeight="medium">Density:</Typography>
                              <Typography variant="caption" component="div" color="text.secondary">
                                {((filteredGraphData.links.length) / 
                                  ((filteredGraphData.nodes.length) * 
                                   ((filteredGraphData.nodes.length) - 1) / 2)).toFixed(3)}
                              </Typography>
                              
                              <Typography variant="caption" component="div" fontWeight="medium">Key Node:</Typography>
                              <Typography variant="caption" component="div" color="text.secondary">{selectedEntity.name}</Typography>
                            </Box>
                          </Box>
                        )}
                        
                        {/* Research Frontiers Panel (if enabled) */}
                        {analysisSettings.identifyResearchFrontiers && (
                          <Box 
                            position="absolute" 
                            top={analysisSettings.showCentralityMetrics ? 150 : 100} 
                            left={10} 
                            zIndex={1000} 
                            p={1.5} 
                            bgcolor="rgba(255,255,255,0.9)" 
                            borderRadius="4px"
                            boxShadow="0 1px 3px rgba(0,0,0,0.12)"
                            border="1px solid rgba(25, 118, 210, 0.3)"
                            aria-label="Research frontiers panel"
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
                        
                        {/* Text-based alternative view for screen readers */}
                        <Box 
                          id="graph-text-alternative"
                          className="visually-hidden" 
                          aria-live="polite" 
                          role="region"
                          aria-label="Text description of knowledge graph"
                          sx={{ 
                            position: 'absolute', 
                            width: '1px', 
                            height: '1px', 
                            padding: 0, 
                            margin: '-1px', 
                            overflow: 'hidden', 
                            clip: 'rect(0, 0, 0, 0)', 
                            whiteSpace: 'nowrap', 
                            border: 0 
                          }}
                        >
                          {filteredGraphData && selectedEntity ? (
                            <>
                              <div>Knowledge graph centered on {selectedEntity.type}: {selectedEntity.name}</div>
                              <div>The graph contains {filteredGraphData.nodes.length} nodes and {filteredGraphData.links.length} connections.</div>
                              <div>Related entities: {filteredGraphData.links
                                .filter(link => {
                                  const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                                  const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                                  return sourceId === selectedEntity.id || targetId === selectedEntity.id;
                                })
                                .map(link => {
                                  const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                                  const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                                  const otherNodeId = sourceId === selectedEntity.id ? targetId : sourceId;
                                  const otherNode = filteredGraphData.nodes.find(node => node.id === otherNodeId);
                                  return otherNode ? `${otherNode.name} (${otherNode.type})` : '';
                                })
                                .filter(Boolean)
                                .join(', ')}
                              </div>
                            </>
                          ) : (
                            <div>No knowledge graph visualization available. Please select an entity first.</div>
                          )}
                        </Box>
                        
                        {/* Progressive loading indicator if enabled */}
                        {visualizationSettings.progressiveLoading && filteredGraphData && 
                          loadedNodeCount < filteredGraphData.nodes.length && (
                          <Box 
                            position="absolute" 
                            bottom={10} 
                            right={10} 
                            zIndex={1000} 
                            p={1} 
                            bgcolor="rgba(255,255,255,0.9)" 
                            borderRadius="4px"
                            boxShadow="0 1px 3px rgba(0,0,0,0.12)"
                            border="1px solid rgba(25, 118, 210, 0.3)"
                            display="flex"
                            alignItems="center"
                            aria-live="polite"
                          >
                            <Typography variant="caption" component="div" sx={{ mr: 1 }}>
                              {loadedNodeCount} of {filteredGraphData.nodes.length} nodes
                            </Typography>
                            <Button 
                              size="small" 
                              variant="outlined" 
                              color="primary" 
                              onClick={handleLoadMoreNodes}
                              sx={{ minWidth: 20, py: 0, px: 1 }}
                              aria-label={`Load more nodes. Currently showing ${loadedNodeCount} of ${filteredGraphData.nodes.length}`}
                            >
                              Load More
                            </Button>
                          </Box>
                        )}
                        
                        {/* The D3 visualization area */}
                        <svg width="100%" height="100%" role="img" aria-labelledby="graph-text-alternative"></svg>
                      </>
                    )}
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
                        • Use arrow keys and keyboard to navigate the graph
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