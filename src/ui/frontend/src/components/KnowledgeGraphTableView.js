import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  TablePagination,
  TableSortLabel,
  Tabs,
  Tab,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import { useTheme } from '../contexts/ThemeContext';

/**
 * A table-based view of the Knowledge Graph that provides an accessible alternative
 * to the D3.js visualization
 */
const KnowledgeGraphTableView = ({ 
  graphData,
  selectedEntity,
  onSelectEntity
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [nodePage, setNodePage] = useState(0);
  const [nodeRowsPerPage, setNodeRowsPerPage] = useState(10);
  const [linkPage, setLinkPage] = useState(0);
  const [linkRowsPerPage, setLinkRowsPerPage] = useState(10);
  const [nodeOrder, setNodeOrder] = useState('asc');
  const [nodeOrderBy, setNodeOrderBy] = useState('name');
  const [linkOrder, setLinkOrder] = useState('asc');
  const [linkOrderBy, setLinkOrderBy] = useState('source');
  const [nodeFilter, setNodeFilter] = useState('');
  const [linkFilter, setLinkFilter] = useState('');
  const [filteredNodes, setFilteredNodes] = useState([]);
  const [filteredLinks, setFilteredLinks] = useState([]);
  
  // Get theme settings for high contrast display
  const { isHighContrast } = useTheme();
  
  // Effect to filter and sort nodes
  useEffect(() => {
    if (!graphData || !graphData.nodes) {
      setFilteredNodes([]);
      return;
    }
    
    // Filter nodes
    const filtered = graphData.nodes.filter(node => {
      const searchTerms = nodeFilter.toLowerCase().split(' ');
      const nodeText = `${node.name} ${node.type} ${node.id}`.toLowerCase();
      return searchTerms.every(term => nodeText.includes(term));
    });
    
    // Sort nodes
    const sorted = stableSort(filtered, getComparator(nodeOrder, nodeOrderBy));
    setFilteredNodes(sorted);
  }, [graphData, nodeFilter, nodeOrder, nodeOrderBy]);
  
  // Effect to filter and sort links
  useEffect(() => {
    if (!graphData || !graphData.links) {
      setFilteredLinks([]);
      return;
    }
    
    // Filter links
    const filtered = graphData.links.filter(link => {
      const searchTerms = linkFilter.toLowerCase().split(' ');
      
      // Get source and target names
      const sourceName = typeof link.source === 'object' ? link.source.name : 
        graphData.nodes.find(n => n.id === link.source)?.name || link.source;
      
      const targetName = typeof link.target === 'object' ? link.target.name : 
        graphData.nodes.find(n => n.id === link.target)?.name || link.target;
        
      const linkText = `${sourceName} ${targetName} ${link.type}`.toLowerCase();
      return searchTerms.every(term => linkText.includes(term));
    });
    
    // Sort links
    const sorted = stableSort(filtered, getComparator(linkOrder, linkOrderBy));
    setFilteredLinks(sorted);
  }, [graphData, linkFilter, linkOrder, linkOrderBy]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle node table page change
  const handleNodePageChange = (event, newPage) => {
    setNodePage(newPage);
  };
  
  // Handle node rows per page change
  const handleNodeRowsPerPageChange = (event) => {
    setNodeRowsPerPage(parseInt(event.target.value, 10));
    setNodePage(0);
  };
  
  // Handle link table page change
  const handleLinkPageChange = (event, newPage) => {
    setLinkPage(newPage);
  };
  
  // Handle link rows per page change
  const handleLinkRowsPerPageChange = (event) => {
    setLinkRowsPerPage(parseInt(event.target.value, 10));
    setLinkPage(0);
  };
  
  // Handle node table sort
  const handleNodeSortRequest = (property) => {
    const isAsc = nodeOrderBy === property && nodeOrder === 'asc';
    setNodeOrder(isAsc ? 'desc' : 'asc');
    setNodeOrderBy(property);
  };
  
  // Handle link table sort
  const handleLinkSortRequest = (property) => {
    const isAsc = linkOrderBy === property && linkOrder === 'asc';
    setLinkOrder(isAsc ? 'desc' : 'asc');
    setLinkOrderBy(property);
  };
  
  // Create sort handler for a given property
  const createSortHandler = (handler, property) => (event) => {
    handler(property);
  };
  
  // Helper function for sorting
  function getComparator(order, orderBy) {
    return order === 'desc'
      ? (a, b) => descendingComparator(a, b, orderBy)
      : (a, b) => -descendingComparator(a, b, orderBy);
  }
  
  // Helper function for descending comparison
  function descendingComparator(a, b, orderBy) {
    // Handle source and target properties for relationships
    if (orderBy === 'source' || orderBy === 'target') {
      const aValue = typeof a[orderBy] === 'object' ? a[orderBy].name : a[orderBy];
      const bValue = typeof b[orderBy] === 'object' ? b[orderBy].name : b[orderBy];
      
      if (bValue < aValue) return -1;
      if (bValue > aValue) return 1;
      return 0;
    }
    
    // Regular property comparison
    if (b[orderBy] < a[orderBy]) return -1;
    if (b[orderBy] > a[orderBy]) return 1;
    return 0;
  }
  
  // Helper function for stable sort
  function stableSort(array, comparator) {
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
      const order = comparator(a[0], b[0]);
      if (order !== 0) return order;
      return a[1] - b[1];
    });
    return stabilizedThis.map((el) => el[0]);
  }
  
  // Format link source or target display
  const formatEndpoint = (endpoint) => {
    if (typeof endpoint === 'object') {
      return endpoint.name;
    }
    
    // Try to find the node by ID
    if (graphData && graphData.nodes) {
      const node = graphData.nodes.find(n => n.id === endpoint);
      if (node) return node.name;
    }
    
    return endpoint;
  };
  
  // Handle row click to select entity
  const handleRowClick = (entity) => {
    if (onSelectEntity) {
      onSelectEntity(entity);
    }
  };
  
  // Empty state message
  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 4, mb: 2 }}>
        <Typography variant="h6" align="center">
          No graph data available
        </Typography>
        <Typography variant="body2" align="center" color="text.secondary">
          Search for entities or load a graph to view data
        </Typography>
      </Paper>
    );
  }
  
  return (
    <Paper 
      elevation={3} 
      sx={{ 
        mb: 2, 
        overflow: 'hidden',
        border: isHighContrast ? (theme) => `2px solid ${theme.palette.divider}` : 'none'
      }}
    >
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          aria-label="Knowledge Graph data tables"
        >
          <Tab label={`Entities (${graphData.nodes.length})`} id="tab-entities" aria-controls="tabpanel-entities" />
          <Tab label={`Relationships (${graphData.links.length})`} id="tab-relationships" aria-controls="tabpanel-relationships" />
        </Tabs>
      </Box>
      
      {/* Entities Tab */}
      <Box
        role="tabpanel"
        hidden={activeTab !== 0}
        id="tabpanel-entities"
        aria-labelledby="tab-entities"
        sx={{ p: 0 }}
      >
        {activeTab === 0 && (
          <Box>
            <Box sx={{ p: 2, pb: 0 }}>
              <TextField
                fullWidth
                variant="outlined"
                size="small"
                value={nodeFilter}
                onChange={(e) => setNodeFilter(e.target.value)}
                placeholder="Search entities..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                aria-label="Search entities"
                sx={{ mb: 2 }}
              />
            </Box>
            <TableContainer>
              <Table aria-label="Entities in the Knowledge Graph">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={nodeOrderBy === 'name'}
                        direction={nodeOrderBy === 'name' ? nodeOrder : 'asc'}
                        onClick={createSortHandler(handleNodeSortRequest, 'name')}
                      >
                        Name
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={nodeOrderBy === 'type'}
                        direction={nodeOrderBy === 'type' ? nodeOrder : 'asc'}
                        onClick={createSortHandler(handleNodeSortRequest, 'type')}
                      >
                        Type
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={nodeOrderBy === 'id'}
                        direction={nodeOrderBy === 'id' ? nodeOrder : 'asc'}
                        onClick={createSortHandler(handleNodeSortRequest, 'id')}
                      >
                        ID
                      </TableSortLabel>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredNodes
                    .slice(nodePage * nodeRowsPerPage, nodePage * nodeRowsPerPage + nodeRowsPerPage)
                    .map((node) => (
                      <TableRow 
                        key={node.id}
                        hover
                        onClick={() => handleRowClick(node)}
                        sx={{ 
                          cursor: 'pointer',
                          backgroundColor: node.id === selectedEntity?.id ? 
                            (theme) => theme.palette.action.selected : 
                            'inherit'
                        }}
                        aria-selected={node.id === selectedEntity?.id}
                        selected={node.id === selectedEntity?.id}
                      >
                        <TableCell component="th" scope="row">
                          {node.name}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={node.type} 
                            size="small" 
                            variant={isHighContrast ? "outlined" : "filled"}
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>{node.id}</TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={filteredNodes.length}
              rowsPerPage={nodeRowsPerPage}
              page={nodePage}
              onPageChange={handleNodePageChange}
              onRowsPerPageChange={handleNodeRowsPerPageChange}
            />
          </Box>
        )}
      </Box>
      
      {/* Relationships Tab */}
      <Box
        role="tabpanel"
        hidden={activeTab !== 1}
        id="tabpanel-relationships"
        aria-labelledby="tab-relationships"
        sx={{ p: 0 }}
      >
        {activeTab === 1 && (
          <Box>
            <Box sx={{ p: 2, pb: 0 }}>
              <TextField
                fullWidth
                variant="outlined"
                size="small"
                value={linkFilter}
                onChange={(e) => setLinkFilter(e.target.value)}
                placeholder="Search relationships..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                aria-label="Search relationships"
                sx={{ mb: 2 }}
              />
            </Box>
            <TableContainer>
              <Table aria-label="Relationships in the Knowledge Graph">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={linkOrderBy === 'source'}
                        direction={linkOrderBy === 'source' ? linkOrder : 'asc'}
                        onClick={createSortHandler(handleLinkSortRequest, 'source')}
                      >
                        Source
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={linkOrderBy === 'type'}
                        direction={linkOrderBy === 'type' ? linkOrder : 'asc'}
                        onClick={createSortHandler(handleLinkSortRequest, 'type')}
                      >
                        Relationship
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={linkOrderBy === 'target'}
                        direction={linkOrderBy === 'target' ? linkOrder : 'asc'}
                        onClick={createSortHandler(handleLinkSortRequest, 'target')}
                      >
                        Target
                      </TableSortLabel>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredLinks
                    .slice(linkPage * linkRowsPerPage, linkPage * linkRowsPerPage + linkRowsPerPage)
                    .map((link) => (
                      <TableRow 
                        key={link.id || `${link.source}-${link.target}`}
                        hover
                      >
                        <TableCell component="th" scope="row">
                          {formatEndpoint(link.source)}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={link.type} 
                            size="small" 
                            variant={isHighContrast ? "outlined" : "filled"}
                            color="secondary"
                          />
                        </TableCell>
                        <TableCell>{formatEndpoint(link.target)}</TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={filteredLinks.length}
              rowsPerPage={linkRowsPerPage}
              page={linkPage}
              onPageChange={handleLinkPageChange}
              onRowsPerPageChange={handleLinkRowsPerPageChange}
            />
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default KnowledgeGraphTableView;