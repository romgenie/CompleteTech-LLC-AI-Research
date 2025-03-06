import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Badge,
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  Tooltip,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import CloseIcon from '@mui/icons-material/Close';
import ArticleIcon from '@mui/icons-material/Article';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import NewReleasesIcon from '@mui/icons-material/NewReleases';
import { useNavigate } from 'react-router-dom';

import { useWebSocketContext } from '../contexts/WebSocketContext';

/**
 * NotificationCenter component for displaying real-time notifications
 * 
 * @component
 */
const NotificationCenter = ({ maxNotifications = 10 }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const { notifications, clearNotifications, removeNotification } = useWebSocketContext();
  const [displayedNotifications, setDisplayedNotifications] = useState([]);
  const navigate = useNavigate();
  
  // Update displayed notifications when notifications change
  useEffect(() => {
    // Sort notifications by date (newest first) and limit the number
    const sorted = [...notifications]
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, maxNotifications);
    
    setDisplayedNotifications(sorted);
  }, [notifications, maxNotifications]);
  
  // Handle menu open
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  // Handle menu close
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  // Handle notification click
  const handleNotificationClick = (notification) => {
    handleMenuClose();
    removeNotification(notification.id);
    
    // Navigate based on notification type
    if (notification.action?.type === 'navigate' && notification.action.path) {
      navigate(notification.action.path);
    }
  };
  
  // Clear all notifications
  const handleClearAll = () => {
    clearNotifications();
    handleMenuClose();
  };
  
  // Format relative time
  const formatRelativeTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInSeconds = Math.floor((now - date) / 1000);
      
      if (diffInSeconds < 60) {
        return 'just now';
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
      }
    } catch (e) {
      return 'unknown time';
    }
  };
  
  // Get icon for notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <NewReleasesIcon color="warning" />;
      case 'paper_status':
        return <ArticleIcon color="primary" />;
      default:
        return <NotificationsIcon color="action" />;
    }
  };
  
  const hasNotifications = displayedNotifications.length > 0;
  const open = Boolean(anchorEl);
  
  return (
    <>
      <Tooltip title="Notifications">
        <IconButton
          color="inherit"
          aria-label={`${displayedNotifications.length} notifications`}
          onClick={handleMenuOpen}
        >
          <Badge badgeContent={displayedNotifications.length} color="error">
            {hasNotifications ? <NotificationsActiveIcon /> : <NotificationsIcon />}
          </Badge>
        </IconButton>
      </Tooltip>
      
      <Menu
        id="notifications-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        PaperProps={{
          style: {
            width: 350,
            maxHeight: 400,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 1, px: 2 }}>
          <Typography variant="subtitle1">Notifications</Typography>
          {hasNotifications && (
            <Tooltip title="Clear all">
              <IconButton size="small" onClick={handleClearAll}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        <Divider />
        
        {!hasNotifications && (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No notifications
            </Typography>
          </Box>
        )}
        
        {displayedNotifications.map((notification) => (
          <MenuItem 
            key={notification.id} 
            onClick={() => handleNotificationClick(notification)}
            sx={{ 
              whiteSpace: 'normal',
              py: 1.5,
              borderBottom: '1px solid rgba(0, 0, 0, 0.08)'
            }}
          >
            <ListItemIcon>
              {getNotificationIcon(notification.category)}
            </ListItemIcon>
            <ListItemText
              primary={notification.title}
              secondary={
                <>
                  <Typography variant="body2" component="span" color="text.primary">
                    {notification.message}
                  </Typography>
                  <Typography variant="caption" component="p" color="text.secondary" sx={{ mt: 0.5 }}>
                    {formatRelativeTime(notification.timestamp)}
                  </Typography>
                </>
              }
            />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

NotificationCenter.propTypes = {
  /** Maximum number of notifications to display */
  maxNotifications: PropTypes.number
};

export default NotificationCenter;