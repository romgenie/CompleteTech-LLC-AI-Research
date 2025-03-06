import React from 'react';
import PropTypes from 'prop-types';
import { Chip, Tooltip, Box, CircularProgress } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';
import HourglassTopIcon from '@mui/icons-material/HourglassTop';
import AutorenewIcon from '@mui/icons-material/Autorenew';

/**
 * StatusIndicator component for displaying processing status
 * Used for paper processing pipeline status indication
 * 
 * @component
 */
const StatusIndicator = ({ 
  status, 
  size = 'medium',
  variant = 'filled',
  showTooltip = true,
  tooltipPlacement = 'top',
  withAnimation = true 
}) => {
  // Status configuration for different states
  const statusConfig = {
    // Initial states
    uploaded: {
      label: 'Uploaded',
      color: 'secondary',
      icon: <PendingIcon fontSize="small" />,
      tooltip: 'Paper has been uploaded and is waiting to be processed'
    },
    queued: {
      label: 'Queued',
      color: 'info',
      icon: <HourglassTopIcon fontSize="small" />,
      tooltip: 'Paper is queued for processing'
    },
    
    // Processing states
    processing: {
      label: 'Processing',
      color: 'primary',
      icon: withAnimation ? (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CircularProgress size={16} thickness={6} sx={{ mr: 0.5 }} />
        </Box>
      ) : <AutorenewIcon fontSize="small" />,
      tooltip: 'Paper is being processed'
    },
    extracting_entities: {
      label: 'Extracting Entities',
      color: 'primary',
      icon: withAnimation ? (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CircularProgress size={16} thickness={6} sx={{ mr: 0.5 }} />
        </Box>
      ) : <AutorenewIcon fontSize="small" />,
      tooltip: 'Extracting entities from paper content'
    },
    extracting_relationships: {
      label: 'Extracting Relations',
      color: 'primary',
      icon: withAnimation ? (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CircularProgress size={16} thickness={6} sx={{ mr: 0.5 }} />
        </Box>
      ) : <AutorenewIcon fontSize="small" />,
      tooltip: 'Extracting relationships between entities'
    },
    building_knowledge_graph: {
      label: 'Building Graph',
      color: 'primary',
      icon: withAnimation ? (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CircularProgress size={16} thickness={6} sx={{ mr: 0.5 }} />
        </Box>
      ) : <AutorenewIcon fontSize="small" />,
      tooltip: 'Integrating extracted knowledge into the knowledge graph'
    },
    
    // Completed states
    analyzed: {
      label: 'Analyzed',
      color: 'success',
      icon: <CheckCircleIcon fontSize="small" />,
      tooltip: 'Paper has been analyzed and integrated into the knowledge graph'
    },
    implementation_ready: {
      label: 'Ready for Implementation',
      color: 'success',
      icon: <CheckCircleIcon fontSize="small" />,
      tooltip: 'Paper is ready for code implementation'
    },
    implemented: {
      label: 'Implemented',
      color: 'success',
      icon: <CheckCircleIcon fontSize="small" />,
      tooltip: 'Paper has been implemented as code'
    },
    
    // Error states
    failed: {
      label: 'Failed',
      color: 'error',
      icon: <ErrorIcon fontSize="small" />,
      tooltip: 'Processing failed'
    },
    error: {
      label: 'Error',
      color: 'error',
      icon: <ErrorIcon fontSize="small" />,
      tooltip: 'An error occurred during processing'
    }
  };
  
  // Default to a pending state if status is unknown
  const config = statusConfig[status] || {
    label: status || 'Unknown',
    color: 'default',
    icon: <PendingIcon fontSize="small" />,
    tooltip: 'Unknown status'
  };
  
  const statusChip = (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      variant={variant}
      icon={config.icon}
    />
  );
  
  return showTooltip ? (
    <Tooltip title={config.tooltip} placement={tooltipPlacement}>
      {statusChip}
    </Tooltip>
  ) : statusChip;
};

StatusIndicator.propTypes = {
  /** Status string for the paper */
  status: PropTypes.string.isRequired,
  
  /** Size of the chip component */
  size: PropTypes.oneOf(['small', 'medium']),
  
  /** Variant of the chip component */
  variant: PropTypes.oneOf(['filled', 'outlined']),
  
  /** Whether to show a tooltip with status description */
  showTooltip: PropTypes.bool,
  
  /** Placement of the tooltip */
  tooltipPlacement: PropTypes.oneOf(['top', 'bottom', 'left', 'right']),
  
  /** Whether to show animation for processing states */
  withAnimation: PropTypes.bool
};

export default StatusIndicator;