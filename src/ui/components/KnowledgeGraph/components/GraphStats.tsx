/**
 * Knowledge Graph statistics component (stub implementation)
 */
import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  Divider, 
  Chip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { 
  BarChart, 
  PieChart, 
  Pie, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  Cell, 
  ResponsiveContainer
} from 'recharts';
import { GraphStatistics, EntityType } from '../types/knowledgeGraph.types';
import { getEntityColor } from '../utils/knowledgeGraphUtils';

interface GraphStatsProps {
  statistics: GraphStatistics | null;
  loading: boolean;
  error: Error | null;
  onTypeClick?: (type: EntityType) => void;
}

export const GraphStats: React.FC<GraphStatsProps> = ({
  statistics,
  loading,
  error,
  onTypeClick
}) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">{error.message}</Alert>
      </Box>
    );
  }

  if (!statistics) {
    return (
      <Box p={2}>
        <Alert severity="info">No statistics available.</Alert>
      </Box>
    );
  }

  // Transform entity type counts for charts
  const entityTypeData = Object.entries(statistics.entityTypeCounts).map(([type, count]) => ({
    name: type,
    value: count,
    color: getEntityColor(type as EntityType)
  })).filter(item => item.value > 0);

  // Transform relationship type counts for charts
  const relationshipTypeData = Object.entries(statistics.relationshipTypeCounts).map(([type, count]) => ({
    name: type,
    value: count,
    color: '#' + ((Math.random() * 0xffffff) << 0).toString(16).padStart(6, '0')
  })).filter(item => item.value > 0);

  return (
    <Box p={2}>
      <Typography variant="h5" component="h2" gutterBottom>
        Knowledge Graph Statistics
      </Typography>
      
      <Grid container spacing={2}>
        {/* Overview Cards */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom>
                Overview
              </Typography>
              <Box>
                <Typography variant="body1">
                  <strong>Entities:</strong> {statistics.entityCount}
                </Typography>
                <Typography variant="body1">
                  <strong>Relationships:</strong> {statistics.relationshipCount}
                </Typography>
                <Typography variant="body1">
                  <strong>Density:</strong> {(statistics.density * 100).toFixed(2)}%
                </Typography>
                <Typography variant="body1">
                  <strong>Average Degree:</strong> {statistics.averageDegree.toFixed(2)}
                </Typography>
                <Typography variant="body1">
                  <strong>Max Degree:</strong> {statistics.maxDegree}
                </Typography>
                {statistics.diameter !== undefined && (
                  <Typography variant="body1">
                    <strong>Diameter:</strong> {statistics.diameter}
                  </Typography>
                )}
                {statistics.clusteringCoefficient !== undefined && (
                  <Typography variant="body1">
                    <strong>Clustering Coefficient:</strong> {statistics.clusteringCoefficient.toFixed(2)}
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Entity Type Distribution */}
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom>
                Entity Types
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                {entityTypeData.map((type) => (
                  <Chip
                    key={type.name}
                    label={`${type.name}: ${type.value}`}
                    sx={{
                      backgroundColor: type.color,
                      color: 'white',
                      cursor: onTypeClick ? 'pointer' : 'default'
                    }}
                    onClick={() => onTypeClick && onTypeClick(type.name as EntityType)}
                  />
                ))}
              </Box>
              
              <Box sx={{ height: 200, display: 'flex', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  Chart visualization will be implemented here
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Relationship Type Distribution */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom>
                Relationship Types
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell align="right">Percentage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {relationshipTypeData.map((type) => (
                      <TableRow key={type.name}>
                        <TableCell component="th" scope="row">
                          {type.name}
                        </TableCell>
                        <TableCell align="right">{type.value}</TableCell>
                        <TableCell align="right">
                          {statistics.relationshipCount > 0 
                            ? ((type.value / statistics.relationshipCount) * 100).toFixed(1) + '%' 
                            : '0%'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};