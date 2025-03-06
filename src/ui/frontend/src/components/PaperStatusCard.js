import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Box, 
  Button,
  IconButton,
  Collapse,
  Divider,
  LinearProgress
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import VisibilityIcon from '@mui/icons-material/Visibility';
import GetAppIcon from '@mui/icons-material/GetApp';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import CodeIcon from '@mui/icons-material/Code';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

import { StatusIndicator } from './index';
import { useWebSocketContext } from '../contexts/WebSocketContext';

/**
 * PaperStatusCard component for displaying paper information and processing status
 * 
 * @component
 */
const PaperStatusCard = ({
  paper,
  onView,
  onImplement,
  onViewGraph,
  showDetailedStatus = false
}) => {
  const [expanded, setExpanded] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(paper.status);
  const [prevStatus, setPrevStatus] = useState(null);
  const [progress, setProgress] = useState(calculateProgress(paper.status));
  
  const { 
    subscribeToPaperUpdates, 
    unsubscribeFromPaperUpdates,
    lastMessage 
  } = useWebSocketContext();
  
  // Calculate progress percentage based on status
  function calculateProgress(status) {
    const statuses = [
      'uploaded', 
      'queued', 
      'processing', 
      'extracting_entities',
      'extracting_relationships', 
      'building_knowledge_graph', 
      'analyzed',
      'implementation_ready', 
      'implemented'
    ];
    
    const index = statuses.indexOf(status);
    if (index === -1) return 0;
    return Math.round((index / (statuses.length - 1)) * 100);
  }
  
  // Subscribe to paper updates when component mounts
  useEffect(() => {
    if (paper?.id) {
      subscribeToPaperUpdates(paper.id);
    }
    
    // Cleanup subscription when component unmounts
    return () => {
      if (paper?.id) {
        unsubscribeFromPaperUpdates(paper.id);
      }
    };
  }, [paper?.id, subscribeToPaperUpdates, unsubscribeFromPaperUpdates]);
  
  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'paper_status_update' && lastMessage.paper_id === paper.id) {
      setPrevStatus(currentStatus);
      setCurrentStatus(lastMessage.status);
      setProgress(calculateProgress(lastMessage.status));
    }
  }, [lastMessage, paper.id, currentStatus]);
  
  // Handle expand toggle
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };
  
  return (
    <Card sx={{ mb: 2, width: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" component="h3" noWrap sx={{ maxWidth: '70%' }}>
            {paper.title}
          </Typography>
          <StatusIndicator status={currentStatus} />
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {paper.authors.join(', ')}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {paper.year}
          </Typography>
        </Box>
        
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ mt: 2, mb: 1, height: 8, borderRadius: 4 }} 
        />
        
        {prevStatus && currentStatus !== prevStatus && (
          <Typography variant="caption" color="primary" sx={{ display: 'block', textAlign: 'right' }}>
            Status updated: {prevStatus} → {currentStatus}
          </Typography>
        )}
      </CardContent>
      
      <CardActions disableSpacing>
        <Button 
          size="small" 
          startIcon={<VisibilityIcon />}
          onClick={() => onView && onView(paper)}
        >
          View
        </Button>
        
        {['analyzed', 'implementation_ready', 'implemented'].includes(currentStatus) && (
          <Button 
            size="small" 
            startIcon={<AutoGraphIcon />}
            onClick={() => onViewGraph && onViewGraph(paper)}
          >
            View Graph
          </Button>
        )}
        
        {['implementation_ready', 'implemented'].includes(currentStatus) && (
          <Button 
            size="small" 
            startIcon={<CodeIcon />}
            onClick={() => onImplement && onImplement(paper)}
          >
            Implementation
          </Button>
        )}
        
        <IconButton 
          sx={{ 
            ml: 'auto', 
            transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s'
          }}
          onClick={handleExpandClick}
          aria-expanded={expanded}
          aria-label="show more"
        >
          <ExpandMoreIcon />
        </IconButton>
      </CardActions>
      
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Divider />
        <CardContent>
          {paper.abstract && (
            <>
              <Typography variant="subtitle2" gutterBottom>Abstract</Typography>
              <Typography variant="body2" paragraph>
                {paper.abstract.length > 300 
                  ? `${paper.abstract.substring(0, 300)}...` 
                  : paper.abstract}
              </Typography>
            </>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Box>
              <Typography variant="caption" display="block" color="text.secondary">
                Uploaded: {formatDate(paper.uploaded_at)}
              </Typography>
              <Typography variant="caption" display="block" color="text.secondary">
                Updated: {formatDate(paper.updated_at)}
              </Typography>
            </Box>
            
            <Button 
              size="small" 
              startIcon={<PictureAsPdfIcon />}
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Source
            </Button>
          </Box>
          
          {showDetailedStatus && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Processing History</Typography>
              <Typography variant="body2" component="div">
                <ul style={{ paddingLeft: '1.5rem', margin: '0.5rem 0' }}>
                  {/* This would be populated from paper.processing_history in a real implementation */}
                  <li>Uploaded: {formatDate(paper.uploaded_at)}</li>
                  {currentStatus !== 'uploaded' && (
                    <li>Queued: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 120000))}</li>
                  )}
                  {['processing', 'extracting_entities', 'extracting_relationships', 'building_knowledge_graph', 'analyzed', 'implementation_ready', 'implemented'].includes(currentStatus) && (
                    <li>Processing started: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 300000))}</li>
                  )}
                  {['extracting_entities', 'extracting_relationships', 'building_knowledge_graph', 'analyzed', 'implementation_ready', 'implemented'].includes(currentStatus) && (
                    <li>Entities extraction: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 480000))}</li>
                  )}
                  {['extracting_relationships', 'building_knowledge_graph', 'analyzed', 'implementation_ready', 'implemented'].includes(currentStatus) && (
                    <li>Relationship extraction: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 600000))}</li>
                  )}
                  {['building_knowledge_graph', 'analyzed', 'implementation_ready', 'implemented'].includes(currentStatus) && (
                    <li>Knowledge graph integration: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 720000))}</li>
                  )}
                  {['analyzed', 'implementation_ready', 'implemented'].includes(currentStatus) && (
                    <li>Analysis completed: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 840000))}</li>
                  )}
                  {['implementation_ready', 'implemented'].includes(currentStatus) && (
                    <li>Ready for implementation: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 960000))}</li>
                  )}
                  {currentStatus === 'implemented' && (
                    <li>Implementation completed: {formatDate(new Date(new Date(paper.uploaded_at).getTime() + 1080000))}</li>
                  )}
                </ul>
              </Typography>
            </Box>
          )}
        </CardContent>
      </Collapse>
    </Card>
  );
};

PaperStatusCard.propTypes = {
  /** Paper object with metadata and status */
  paper: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    authors: PropTypes.arrayOf(PropTypes.string).isRequired,
    year: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    status: PropTypes.string.isRequired,
    abstract: PropTypes.string,
    url: PropTypes.string,
    uploaded_at: PropTypes.string,
    updated_at: PropTypes.string
  }).isRequired,
  
  /** Function to call when View button is clicked */
  onView: PropTypes.func,
  
  /** Function to call when Implement button is clicked */
  onImplement: PropTypes.func,
  
  /** Function to call when View Graph button is clicked */
  onViewGraph: PropTypes.func,
  
  /** Whether to show detailed processing history */
  showDetailedStatus: PropTypes.bool
};

export default PaperStatusCard;