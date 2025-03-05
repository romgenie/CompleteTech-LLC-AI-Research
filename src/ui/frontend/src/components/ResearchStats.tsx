import React, { useRef, useEffect } from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent, Divider } from '@mui/material';
import * as d3 from 'd3';
import { useD3 } from '../hooks';
import { ResearchStats as ResearchStatsType } from '../types/research';

interface ResearchStatsProps {
  stats: ResearchStatsType;
}

const ResearchStats: React.FC<ResearchStatsProps> = ({ stats }) => {
  // D3 chart for queries by date
  const timeChartRef = useD3(
    (svg) => {
      // Clear any existing chart
      svg.selectAll('*').remove();

      const margin = { top: 20, right: 30, bottom: 40, left: 50 };
      const width = svg.node()?.parentElement?.clientWidth ?? 500;
      const height = 200;
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Parse dates and sort chronologically
      const data = stats.queriesByDate
        .map(d => ({ date: new Date(d.date), count: d.count }))
        .sort((a, b) => a.date.getTime() - b.date.getTime());

      // Set up scales
      const x = d3.scaleTime()
        .domain(d3.extent(data, d => d.date) as [Date, Date])
        .range([0, innerWidth]);

      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count) || 10])
        .nice()
        .range([innerHeight, 0]);

      // Create axes
      const xAxis = d3.axisBottom(x)
        .ticks(width > 500 ? 10 : 5)
        .tickSizeOuter(0);

      const yAxis = d3.axisLeft(y)
        .ticks(5)
        .tickSizeOuter(0);

      // Create line generator
      const line = d3.line<{ date: Date; count: number }>()
        .x(d => x(d.date))
        .y(d => y(d.count))
        .curve(d3.curveMonotoneX);

      // Create chart group with margin
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(xAxis)
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em');

      g.append('g')
        .call(yAxis)
        .append('text')
        .attr('fill', 'currentColor')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -innerHeight / 2)
        .attr('text-anchor', 'middle')
        .text('Queries');

      // Add line path
      g.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#1976d2')
        .attr('stroke-width', 2)
        .attr('d', line);

      // Add dots
      g.selectAll('circle')
        .data(data)
        .join('circle')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.count))
        .attr('r', 4)
        .attr('fill', '#1976d2');

      // Add tooltip
      const tooltip = d3.select('body').append('div')
        .attr('class', 'd3-tooltip')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background-color', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('padding', '5px 10px')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none');

      g.selectAll('circle')
        .on('mouseover', (event, d) => {
          tooltip
            .style('visibility', 'visible')
            .html(`Date: ${d.date.toLocaleDateString()}<br>Queries: ${d.count}`);
        })
        .on('mousemove', (event) => {
          tooltip
            .style('top', (event.pageY - 10) + 'px')
            .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
        });

      // Clean up tooltip on unmount
      return () => {
        d3.select('.d3-tooltip').remove();
      };
    },
    [stats.queriesByDate]
  );

  // D3 chart for tag distribution
  const tagChartRef = useD3(
    (svg) => {
      // Clear any existing chart
      svg.selectAll('*').remove();

      const margin = { top: 20, right: 30, bottom: 120, left: 50 };
      const width = svg.node()?.parentElement?.clientWidth ?? 500;
      const height = 300;
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Prepare tag data
      const data = Object.entries(stats.tagCounts)
        .map(([tag, count]) => ({ tag, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10); // Show top 10 tags

      // Set up scales
      const x = d3.scaleBand()
        .domain(data.map(d => d.tag))
        .range([0, innerWidth])
        .padding(0.1);

      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count) || 10])
        .nice()
        .range([innerHeight, 0]);

      // Create axes
      const xAxis = d3.axisBottom(x);
      const yAxis = d3.axisLeft(y).ticks(5);

      // Create chart group with margin
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(xAxis)
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em');

      g.append('g')
        .call(yAxis)
        .append('text')
        .attr('fill', 'currentColor')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -innerHeight / 2)
        .attr('text-anchor', 'middle')
        .text('Count');

      // Create color scale
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

      // Add bars
      g.selectAll('.bar')
        .data(data)
        .join('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.tag) || 0)
        .attr('y', d => y(d.count))
        .attr('width', x.bandwidth())
        .attr('height', d => innerHeight - y(d.count))
        .attr('fill', (d, i) => colorScale(i.toString()));

      // Add tooltip
      const tooltip = d3.select('body').append('div')
        .attr('class', 'd3-tooltip-tags')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background-color', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('padding', '5px 10px')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none');

      g.selectAll('.bar')
        .on('mouseover', (event, d) => {
          tooltip
            .style('visibility', 'visible')
            .html(`Tag: ${d.tag}<br>Count: ${d.count}`);
        })
        .on('mousemove', (event) => {
          tooltip
            .style('top', (event.pageY - 10) + 'px')
            .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
        });

      // Clean up tooltip on unmount
      return () => {
        d3.select('.d3-tooltip-tags').remove();
      };
    },
    [stats.tagCounts]
  );

  // D3 chart for top search terms
  const searchTermsChartRef = useD3(
    (svg) => {
      // Clear any existing chart
      svg.selectAll('*').remove();

      const margin = { top: 20, right: 30, bottom: 120, left: 50 };
      const width = svg.node()?.parentElement?.clientWidth ?? 500;
      const height = 300;
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Prepare search terms data
      const data = [...stats.topSearchTerms]
        .sort((a, b) => b.count - a.count)
        .slice(0, 8); // Show top 8 search terms

      // Set up scales
      const x = d3.scaleBand()
        .domain(data.map(d => d.term))
        .range([0, innerWidth])
        .padding(0.1);

      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count) || 10])
        .nice()
        .range([innerHeight, 0]);

      // Create axes
      const xAxis = d3.axisBottom(x);
      const yAxis = d3.axisLeft(y).ticks(5);

      // Create chart group with margin
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Add axes
      g.append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(xAxis)
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .style('max-width', x.bandwidth() + 'px')
        .text(d => d.length > 15 ? d.substring(0, 15) + '...' : d);

      g.append('g')
        .call(yAxis)
        .append('text')
        .attr('fill', 'currentColor')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -innerHeight / 2)
        .attr('text-anchor', 'middle')
        .text('Frequency');

      // Add bars with gradient
      g.selectAll('.bar')
        .data(data)
        .join('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.term) || 0)
        .attr('y', d => y(d.count))
        .attr('width', x.bandwidth())
        .attr('height', d => innerHeight - y(d.count))
        .attr('fill', '#2196f3');

      // Add tooltip for full text
      const tooltip = d3.select('body').append('div')
        .attr('class', 'd3-tooltip-terms')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .style('background-color', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('padding', '5px 10px')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('max-width', '300px')
        .style('word-wrap', 'break-word');

      g.selectAll('.bar')
        .on('mouseover', (event, d) => {
          tooltip
            .style('visibility', 'visible')
            .html(`Term: "${d.term}"<br>Frequency: ${d.count}`);
        })
        .on('mousemove', (event) => {
          tooltip
            .style('top', (event.pageY - 10) + 'px')
            .style('left', (event.pageX + 10) + 'px');
        })
        .on('mouseout', () => {
          tooltip.style('visibility', 'hidden');
        });

      // Clean up tooltip on unmount
      return () => {
        d3.select('.d3-tooltip-terms').remove();
      };
    },
    [stats.topSearchTerms]
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Research Statistics
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h3" align="center" color="primary">
                {stats.totalQueries}
              </Typography>
              <Typography variant="subtitle1" align="center" color="text.secondary">
                Total Queries
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h3" align="center" color="primary">
                {stats.savedQueries}
              </Typography>
              <Typography variant="subtitle1" align="center" color="text.secondary">
                Saved Queries
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h3" align="center" color="primary">
                {stats.favorites}
              </Typography>
              <Typography variant="subtitle1" align="center" color="text.secondary">
                Favorites
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h3" align="center" color="primary">
                {stats.averageResultsPerQuery.toFixed(1)}
              </Typography>
              <Typography variant="subtitle1" align="center" color="text.secondary">
                Avg Results
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Research Activity Over Time
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Number of research queries conducted over time
            </Typography>
            <Box sx={{ height: 240 }}>
              <svg
                ref={timeChartRef}
                style={{
                  width: '100%',
                  height: '100%',
                }}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Top Tags
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Most frequently used tags for organizing research
            </Typography>
            <Box sx={{ height: 300 }}>
              <svg
                ref={tagChartRef}
                style={{
                  width: '100%',
                  height: '100%',
                }}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Search Terms
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Most frequent terms used in research queries
            </Typography>
            <Box sx={{ height: 300 }}>
              <svg
                ref={searchTermsChartRef}
                style={{
                  width: '100%',
                  height: '100%',
                }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchStats;