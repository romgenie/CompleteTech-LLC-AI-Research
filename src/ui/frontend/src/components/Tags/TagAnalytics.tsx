import React, { useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardHeader, 
  Grid, 
  Chip, 
  Divider, 
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import * as d3 from 'd3';

import { Tag, TagUsageStats } from '../../types/research';
import { useTagStats, usePopularTags } from '../../services/tagsService';
import { useD3 } from '../../hooks/useD3';

interface TagAnalyticsProps {
  tagId?: string;
}

/**
 * Component for displaying tag usage analytics
 */
const TagAnalytics: React.FC<TagAnalyticsProps> = ({ tagId }) => {
  const [selectedTagId, setSelectedTagId] = React.useState<string | undefined>(tagId);
  const { data: popularTags, isLoading: isLoadingPopular } = usePopularTags(10);
  const { data: tagStats, isLoading: isLoadingStats } = useTagStats(selectedTagId || '');

  // Chart references
  const usageChartRef = useD3(
    (svg) => {
      if (!tagStats || !tagStats.dailyUse || tagStats.dailyUse.length === 0) return;

      // Clear previous chart
      svg.selectAll('*').remove();

      const margin = { top: 20, right: 30, bottom: 30, left: 40 };
      const width = svg.node()?.parentElement?.clientWidth || 300;
      const height = 200;
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Parse dates and create scales
      const dateParser = d3.timeParse('%Y-%m-%d');
      const dates = tagStats.dailyUse.map(d => dateParser(d.date) || new Date());
      const counts = tagStats.dailyUse.map(d => d.count);

      const xScale = d3.scaleTime()
        .domain(d3.extent(dates) as [Date, Date])
        .range([0, innerWidth]);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(counts) || 10])
        .nice()
        .range([innerHeight, 0]);

      // Create the line generator
      const line = d3.line<any>()
        .x(d => xScale(dateParser(d.date) || new Date()))
        .y(d => yScale(d.count))
        .curve(d3.curveMonotoneX);

      // Create chart group
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale).ticks(5).tickSizeOuter(0));

      g.append('g')
        .call(d3.axisLeft(yScale).ticks(5).tickSizeOuter(0));

      // Add the line path
      g.append('path')
        .datum(tagStats.dailyUse)
        .attr('fill', 'none')
        .attr('stroke', '#2196f3')
        .attr('stroke-width', 2)
        .attr('d', line);

      // Add dots for each data point
      g.selectAll('.dot')
        .data(tagStats.dailyUse)
        .enter().append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(dateParser(d.date) || new Date()))
        .attr('cy', d => yScale(d.count))
        .attr('r', 4)
        .attr('fill', '#2196f3');
    },
    [tagStats?.dailyUse]
  );

  const relationshipChartRef = useD3(
    (svg) => {
      if (!tagStats || !tagStats.relatedTags || tagStats.relatedTags.length === 0) return;

      // Clear previous chart
      svg.selectAll('*').remove();

      const margin = { top: 20, right: 30, bottom: 100, left: 40 };
      const width = svg.node()?.parentElement?.clientWidth || 300;
      const height = 250;
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Sort tags by co-occurrence
      const sortedTags = [...tagStats.relatedTags].sort((a, b) => b.cooccurrence - a.cooccurrence);
      const tags = sortedTags.slice(0, 8); // Limit to top 8 for readability

      // Create scales
      const xScale = d3.scaleBand()
        .domain(tags.map(d => d.tagId))
        .range([0, innerWidth])
        .padding(0.2);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(tags, d => d.cooccurrence) || 1])
        .nice()
        .range([innerHeight, 0]);

      // Create chart group
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(xScale))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em');

      g.append('g')
        .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => (d as number).toFixed(2)));

      // Add the bars
      g.selectAll('.bar')
        .data(tags)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.tagId) || 0)
        .attr('y', d => yScale(d.cooccurrence))
        .attr('width', xScale.bandwidth())
        .attr('height', d => innerHeight - yScale(d.cooccurrence))
        .attr('fill', '#4caf50');
    },
    [tagStats?.relatedTags]
  );

  const handleTagChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedTagId(event.target.value as string);
  };

  // Get tag name from ID
  const getTagName = (id: string): string => {
    if (!popularTags) return id;
    const tag = popularTags.find(t => t.id === id);
    return tag ? tag.name : id;
  };

  // Trend icon based on trend value
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'rising': return <TrendingUpIcon color="success" />;
      case 'falling': return <TrendingDownIcon color="error" />;
      default: return <TrendingFlatIcon color="action" />;
    }
  };

  if (isLoadingPopular) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Tag Analytics
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth variant="outlined" size="small">
          <InputLabel>Select Tag</InputLabel>
          <Select
            value={selectedTagId || ''}
            onChange={handleTagChange}
            label="Select Tag"
            displayEmpty
          >
            <MenuItem value="" disabled>Select a tag to view analytics</MenuItem>
            {popularTags?.map(tag => (
              <MenuItem key={tag.id} value={tag.id}>{tag.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      
      {isLoadingStats ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : tagStats ? (
        <Grid container spacing={3}>
          {/* Summary Card */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">
                    {getTagName(tagStats.tagId)}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                      Trend:
                    </Typography>
                    {getTrendIcon(tagStats.trend)}
                  </Box>
                </Box>
                
                <Box sx={{ display: 'flex', mt: 2 }}>
                  <Box sx={{ mr: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      Total Users
                    </Typography>
                    <Typography variant="h5">
                      {tagStats.userCount}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Items
                    </Typography>
                    <Typography variant="h5">
                      {tagStats.itemCount}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Usage Trend Chart */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardHeader title="Usage Trend" />
              <Divider />
              <CardContent>
                <svg
                  ref={usageChartRef}
                  style={{ width: '100%', height: '200px' }}
                />
              </CardContent>
            </Card>
          </Grid>
          
          {/* Related Tags Chart */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardHeader title="Co-occurrence with Other Tags" />
              <Divider />
              <CardContent>
                <svg
                  ref={relationshipChartRef}
                  style={{ width: '100%', height: '250px' }}
                />
              </CardContent>
            </Card>
          </Grid>
          
          {/* Related Tags List */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardHeader title="Related Tags" />
              <Divider />
              <CardContent>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {tagStats.relatedTags.map(relatedTag => (
                    <Chip
                      key={relatedTag.tagId}
                      label={`${getTagName(relatedTag.tagId)} (${relatedTag.cooccurrence.toFixed(2)})`}
                      onClick={() => setSelectedTagId(relatedTag.tagId)}
                      clickable
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Typography color="text.secondary" align="center" py={4}>
          Select a tag to view analytics
        </Typography>
      )}
    </Box>
  );
};

export default TagAnalytics;