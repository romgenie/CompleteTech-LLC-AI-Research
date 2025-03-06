import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Divider,
  FormControlLabel,
  Switch
} from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';
import SpeedIcon from '@mui/icons-material/Speed';
import MemoryIcon from '@mui/icons-material/Memory';
import NetworkCheckIcon from '@mui/icons-material/NetworkCheck';

import { 
  BenchmarkResults, 
  BenchmarkSuite,
  getBenchmarkDatasets,
  generateBenchmarkReport,
  formatBenchmarkResult
} from '../utils/benchmarkUtils';

interface KnowledgeGraphBenchmarkProps {
  runBenchmark: (nodeCount: number) => Promise<BenchmarkResults>;
  onComplete?: (report: string) => void;
}

const KnowledgeGraphBenchmark: React.FC<KnowledgeGraphBenchmarkProps> = ({ 
  runBenchmark,
  onComplete 
}) => {
  const [benchmarkSuite, setBenchmarkSuite] = useState<BenchmarkSuite>({
    small: null,
    medium: null,
    large: null,
    veryLarge: null
  });
  const [currentTest, setCurrentTest] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [report, setReport] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [includeVeryLarge, setIncludeVeryLarge] = useState<boolean>(false);
  
  const abortControllerRef = useRef<AbortController | null>(null);
  
  const runFullBenchmark = async () => {
    try {
      setError(null);
      setProgress(0);
      
      // Create datasets for different sizes
      const datasets = getBenchmarkDatasets();
      
      // Small dataset benchmark
      setCurrentTest('small');
      setProgress(10);
      const smallResults = await runBenchmark(100);
      setBenchmarkSuite(prev => ({ ...prev, small: smallResults }));
      setProgress(25);
      
      // Medium dataset benchmark
      setCurrentTest('medium');
      setProgress(30);
      const mediumResults = await runBenchmark(500);
      setBenchmarkSuite(prev => ({ ...prev, medium: mediumResults }));
      setProgress(50);
      
      // Large dataset benchmark
      setCurrentTest('large');
      setProgress(60);
      const largeResults = await runBenchmark(1000);
      setBenchmarkSuite(prev => ({ ...prev, large: largeResults }));
      setProgress(75);
      
      // Very large dataset benchmark (optional)
      if (includeVeryLarge) {
        setCurrentTest('veryLarge');
        setProgress(80);
        const veryLargeResults = await runBenchmark(2000);
        setBenchmarkSuite(prev => ({ ...prev, veryLarge: veryLargeResults }));
      }
      
      setProgress(100);
      setCurrentTest(null);
      
      // Generate report
      const benchmarkReport = generateBenchmarkReport({
        small: smallResults,
        medium: mediumResults,
        large: largeResults,
        veryLarge: includeVeryLarge ? await runBenchmark(2000) : null
      });
      
      setReport(benchmarkReport);
      
      if (onComplete) {
        onComplete(benchmarkReport);
      }
    } catch (e) {
      if (e instanceof Error) {
        setError(`Benchmark failed: ${e.message}`);
      } else {
        setError('Benchmark failed with an unknown error');
      }
      setCurrentTest(null);
    }
  };
  
  const cancelBenchmark = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setCurrentTest(null);
    setError('Benchmark cancelled');
  };
  
  const renderStatusLabel = (size: string) => {
    if (currentTest === size) {
      return <Chip color="primary" label="Running..." size="small" />;
    }
    
    const result = benchmarkSuite[size as keyof BenchmarkSuite];
    if (result) {
      const isGoodPerformance = 
        (size === 'small' && result.frameRate > 40) ||
        (size === 'medium' && result.frameRate > 30) ||
        (size === 'large' && result.frameRate > 20) ||
        (size === 'veryLarge' && result.frameRate > 15);
      
      return isGoodPerformance ? 
        <Chip color="success" label="Passed" size="small" /> : 
        <Chip color="warning" label="Needs optimization" size="small" />;
    }
    
    return <Chip variant="outlined" label="Not run" size="small" />;
  };
  
  const getPerformanceRating = (): 'excellent' | 'good' | 'fair' | 'poor' | undefined => {
    if (!benchmarkSuite.small || !benchmarkSuite.medium || !benchmarkSuite.large) {
      return undefined;
    }
    
    // Calculate an overall score based on frame rates and render times
    const smallScore = benchmarkSuite.small.frameRate / 60;
    const mediumScore = benchmarkSuite.medium.frameRate / 45;
    const largeScore = benchmarkSuite.large.frameRate / 30;
    
    // Weight larger datasets more heavily
    const weightedScore = (smallScore + mediumScore * 2 + largeScore * 3) / 6;
    
    if (weightedScore > 0.85) return 'excellent';
    if (weightedScore > 0.7) return 'good';
    if (weightedScore > 0.5) return 'fair';
    return 'poor';
  };
  
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom display="flex" alignItems="center">
        <BarChartIcon sx={{ mr: 1 }} /> Knowledge Graph Performance Benchmark
      </Typography>
      
      <Typography variant="body2" paragraph color="text.secondary">
        This tool measures the performance of the knowledge graph visualization with different dataset sizes.
        It evaluates render time, frame rate, and interaction responsiveness to identify potential performance issues.
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ mb: 3 }}>
        <FormControlLabel
          control={
            <Switch
              checked={includeVeryLarge}
              onChange={(e) => setIncludeVeryLarge(e.target.checked)}
              disabled={!!currentTest}
            />
          }
          label="Include very large dataset test (2000 nodes)"
        />
      </Box>
      
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Small Dataset</Typography>
              <Typography variant="h5">100 Nodes</Typography>
              <Box sx={{ mt: 2 }}>
                {renderStatusLabel('small')}
              </Box>
              {benchmarkSuite.small && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {benchmarkSuite.small.frameRate.toFixed(1)} fps
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Medium Dataset</Typography>
              <Typography variant="h5">500 Nodes</Typography>
              <Box sx={{ mt: 2 }}>
                {renderStatusLabel('medium')}
              </Box>
              {benchmarkSuite.medium && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {benchmarkSuite.medium.frameRate.toFixed(1)} fps
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Large Dataset</Typography>
              <Typography variant="h5">1000 Nodes</Typography>
              <Box sx={{ mt: 2 }}>
                {renderStatusLabel('large')}
              </Box>
              {benchmarkSuite.large && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {benchmarkSuite.large.frameRate.toFixed(1)} fps
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">Very Large Dataset</Typography>
              <Typography variant="h5">2000 Nodes</Typography>
              <Box sx={{ mt: 2 }}>
                {renderStatusLabel('veryLarge')}
              </Box>
              {benchmarkSuite.veryLarge && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {benchmarkSuite.veryLarge.frameRate.toFixed(1)} fps
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {progress > 0 && progress < 100 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>
            Running {currentTest} dataset benchmark...
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      )}
      
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={runFullBenchmark}
          disabled={!!currentTest}
          startIcon={<SpeedIcon />}
        >
          Run Benchmark
        </Button>
        
        {currentTest && (
          <Button 
            variant="outlined" 
            color="error" 
            onClick={cancelBenchmark}
          >
            Cancel
          </Button>
        )}
      </Box>
      
      {getPerformanceRating() && (
        <Alert 
          severity={
            getPerformanceRating() === 'excellent' ? 'success' :
            getPerformanceRating() === 'good' ? 'success' :
            getPerformanceRating() === 'fair' ? 'warning' :
            'error'
          }
          sx={{ mb: 3 }}
        >
          <Typography variant="subtitle2">
            Overall Performance Rating: {getPerformanceRating()?.toUpperCase()}
          </Typography>
          {getPerformanceRating() === 'excellent' && (
            <Typography variant="body2">
              The visualization performs exceptionally well across all dataset sizes. Great job!
            </Typography>
          )}
          {getPerformanceRating() === 'good' && (
            <Typography variant="body2">
              The visualization performs well for most dataset sizes with minor optimizations needed for larger datasets.
            </Typography>
          )}
          {getPerformanceRating() === 'fair' && (
            <Typography variant="body2">
              The visualization works acceptably but shows performance degradation with larger datasets. 
              Consider implementing additional optimizations.
            </Typography>
          )}
          {getPerformanceRating() === 'poor' && (
            <Typography variant="body2">
              The visualization shows significant performance issues, especially with larger datasets. 
              Major optimizations are recommended.
            </Typography>
          )}
        </Alert>
      )}
      
      {benchmarkSuite.small && benchmarkSuite.medium && benchmarkSuite.large && (
        <>
          <Typography variant="h6" gutterBottom sx={{ mt: 3, display: 'flex', alignItems: 'center' }}>
            <NetworkCheckIcon sx={{ mr: 1 }} /> Detailed Results
          </Typography>
          <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Dataset</TableCell>
                  <TableCell align="right">Nodes</TableCell>
                  <TableCell align="right">Links</TableCell>
                  <TableCell align="right">Render Time (ms)</TableCell>
                  <TableCell align="right">Frame Rate (fps)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Small</TableCell>
                  <TableCell align="right">{benchmarkSuite.small.nodeCount}</TableCell>
                  <TableCell align="right">{benchmarkSuite.small.linkCount}</TableCell>
                  <TableCell align="right">{benchmarkSuite.small.renderTime.toFixed(2)}</TableCell>
                  <TableCell align="right">{benchmarkSuite.small.frameRate.toFixed(2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Medium</TableCell>
                  <TableCell align="right">{benchmarkSuite.medium.nodeCount}</TableCell>
                  <TableCell align="right">{benchmarkSuite.medium.linkCount}</TableCell>
                  <TableCell align="right">{benchmarkSuite.medium.renderTime.toFixed(2)}</TableCell>
                  <TableCell align="right">{benchmarkSuite.medium.frameRate.toFixed(2)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Large</TableCell>
                  <TableCell align="right">{benchmarkSuite.large.nodeCount}</TableCell>
                  <TableCell align="right">{benchmarkSuite.large.linkCount}</TableCell>
                  <TableCell align="right">{benchmarkSuite.large.renderTime.toFixed(2)}</TableCell>
                  <TableCell align="right">{benchmarkSuite.large.frameRate.toFixed(2)}</TableCell>
                </TableRow>
                {benchmarkSuite.veryLarge && (
                  <TableRow>
                    <TableCell>Very Large</TableCell>
                    <TableCell align="right">{benchmarkSuite.veryLarge.nodeCount}</TableCell>
                    <TableCell align="right">{benchmarkSuite.veryLarge.linkCount}</TableCell>
                    <TableCell align="right">{benchmarkSuite.veryLarge.renderTime.toFixed(2)}</TableCell>
                    <TableCell align="right">{benchmarkSuite.veryLarge.frameRate.toFixed(2)}</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <MemoryIcon sx={{ mr: 1 }} /> Efficiency Analysis
          </Typography>
          
          <Typography variant="body2" paragraph>
            Rendering efficiency (nodes/ms): 
            Small: {(benchmarkSuite.small.nodeCount / benchmarkSuite.small.renderTime).toFixed(2)} | 
            Medium: {(benchmarkSuite.medium.nodeCount / benchmarkSuite.medium.renderTime).toFixed(2)} | 
            Large: {(benchmarkSuite.large.nodeCount / benchmarkSuite.large.renderTime).toFixed(2)}
            {benchmarkSuite.veryLarge && ` | Very Large: ${(benchmarkSuite.veryLarge.nodeCount / benchmarkSuite.veryLarge.renderTime).toFixed(2)}`}
          </Typography>
          
          <Typography variant="body2" paragraph>
            Scaling ratio (large:small): {((benchmarkSuite.large.nodeCount / benchmarkSuite.large.renderTime) / 
            (benchmarkSuite.small.nodeCount / benchmarkSuite.small.renderTime)).toFixed(2)}x
          </Typography>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="caption" display="block" color="text.secondary">
            Note: Benchmark results vary by device. For reference, a good visualization should maintain 
            at least 30fps for medium datasets and 15fps for very large datasets.
          </Typography>
        </>
      )}
    </Paper>
  );
};

export default KnowledgeGraphBenchmark;