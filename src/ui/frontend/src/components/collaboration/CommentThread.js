import React, { useState, useEffect } from 'react';
import { 
  Box, Button, Typography, Paper, Avatar, 
  TextField, Chip, IconButton, Menu, MenuItem,
  Divider, Tooltip, CircularProgress
} from '@mui/material';
import { 
  MoreVert as MoreIcon, 
  Reply as ReplyIcon, 
  Check as CheckIcon,
  ThumbUp as LikeIcon,
  ThumbUpOutlined as LikeOutlinedIcon,
  Comment as CommentIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';
import collaborationService from '../../services/collaborationService';

/**
 * Component for displaying a comment thread with replies and actions
 */
const CommentThread = ({ comment, targetType, targetId, onCommentResolved }) => {
  const { currentUser } = useAuth();
  
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [replyContent, setReplyContent] = useState('');
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [likes, setLikes] = useState([]);
  const [userLiked, setUserLiked] = useState(false);

  // State for menu
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const menuOpen = Boolean(menuAnchorEl);

  // Load replies on component mount
  useEffect(() => {
    const fetchReplies = async () => {
      if (!comment.id) return;
      
      try {
        setLoading(true);
        const data = await collaborationService.getCommentReplies(comment.id);
        setReplies(data);
        
        // Get reactions (likes)
        const reactions = await collaborationService.getCommentReactions(comment.id);
        setLikes(reactions.filter(r => r.reaction === 'like'));
        
        // Check if current user liked this comment
        setUserLiked(reactions.some(r => r.reaction === 'like' && r.user_id === currentUser?.id));
        
        setError(null);
      } catch (err) {
        setError('Failed to load replies');
        console.error('Error loading comment replies:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReplies();
  }, [comment.id, currentUser?.id]);

  // Handle submitting a reply
  const handleSubmitReply = async () => {
    if (!replyContent.trim()) return;
    
    try {
      setSubmitting(true);
      
      const newReply = await collaborationService.createComment({
        content: replyContent,
        type: 'ANSWER',
        target_type: targetType,
        target_id: targetId,
        parent_id: comment.id
      });
      
      // Add the new reply to the replies list
      setReplies([...replies, newReply]);
      
      // Reset form
      setReplyContent('');
      setShowReplyForm(false);
    } catch (err) {
      console.error('Error submitting reply:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // Handle resolving a comment
  const handleResolveComment = async () => {
    try {
      await collaborationService.resolveComment(comment.id);
      
      // Notify parent component
      if (onCommentResolved) {
        onCommentResolved(comment.id);
      }
    } catch (err) {
      console.error('Error resolving comment:', err);
    } finally {
      setMenuAnchorEl(null);
    }
  };

  // Handle toggling like status
  const handleToggleLike = async () => {
    try {
      if (userLiked) {
        // Unlike
        await collaborationService.removeReaction(comment.id, 'like');
        setLikes(likes.filter(like => like.user_id !== currentUser?.id));
      } else {
        // Like
        const newReaction = await collaborationService.addReaction(comment.id, 'like');
        setLikes([...likes, newReaction]);
      }
      
      setUserLiked(!userLiked);
    } catch (err) {
      console.error('Error toggling like status:', err);
    }
  };

  // Check if current user is the comment author
  const isAuthor = currentUser?.id === comment.author_id;

  // Format comment type for display
  const getCommentTypeChip = () => {
    switch (comment.type) {
      case 'GENERAL':
        return <Chip size="small" label="Comment" icon={<CommentIcon />} />;
      case 'ANNOTATION':
        return <Chip size="small" label="Annotation" color="primary" />;
      case 'SUGGESTION':
        return <Chip size="small" label="Suggestion" color="secondary" />;
      default:
        return null;
    }
  };

  return (
    <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
      {/* Comment header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
            {comment.author_name?.[0] || '?'}
          </Avatar>
          <Box>
            <Typography variant="subtitle2">
              {comment.author_name || 'Unknown User'}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
              <TimeIcon fontSize="inherit" sx={{ mr: 0.5 }} />
              {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {getCommentTypeChip()}
          
          {comment.status === 'RESOLVED' ? (
            <Tooltip title="Resolved">
              <Chip 
                size="small" 
                label="Resolved" 
                color="success" 
                icon={<CheckIcon />} 
                sx={{ ml: 1 }} 
              />
            </Tooltip>
          ) : (
            <IconButton
              aria-label="more"
              aria-controls="comment-menu"
              aria-haspopup="true"
              onClick={(e) => setMenuAnchorEl(e.currentTarget)}
              size="small"
            >
              <MoreIcon />
            </IconButton>
          )}
        </Box>
      </Box>
      
      {/* Comment menu */}
      <Menu
        id="comment-menu"
        anchorEl={menuAnchorEl}
        open={menuOpen}
        onClose={() => setMenuAnchorEl(null)}
      >
        <MenuItem onClick={handleResolveComment}>
          <CheckIcon fontSize="small" sx={{ mr: 1 }} />
          Mark as Resolved
        </MenuItem>
        {isAuthor && (
          <MenuItem>
            Edit Comment
          </MenuItem>
        )}
        {isAuthor && (
          <MenuItem>
            Delete Comment
          </MenuItem>
        )}
      </Menu>

      {/* Comment content */}
      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', my: 1 }}>
        {comment.content}
      </Typography>
      
      {/* Comment actions */}
      <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
        <Tooltip title={userLiked ? "Unlike" : "Like"}>
          <Button 
            size="small"
            startIcon={userLiked ? <LikeIcon /> : <LikeOutlinedIcon />}
            onClick={handleToggleLike}
          >
            {likes.length > 0 && likes.length}
          </Button>
        </Tooltip>

        <Tooltip title="Reply">
          <Button 
            size="small" 
            startIcon={<ReplyIcon />}
            onClick={() => setShowReplyForm(true)}
            sx={{ ml: 1 }}
          >
            Reply
          </Button>
        </Tooltip>
      </Box>
      
      {/* Replies section */}
      {(replies.length > 0 || loading) && (
        <Box sx={{ mt: 2, ml: 4, borderLeft: '2px solid #e0e0e0', pl: 2 }}>
          {loading ? (
            <CircularProgress size={20} />
          ) : (
            replies.map(reply => (
              <Box key={reply.id} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                    {reply.author_name?.[0] || '?'}
                  </Avatar>
                  <Typography variant="subtitle2">
                    {reply.author_name || 'Unknown User'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    {formatDistanceToNow(new Date(reply.created_at), { addSuffix: true })}
                  </Typography>
                </Box>
                
                <Typography variant="body2" sx={{ mt: 0.5, ml: 4 }}>
                  {reply.content}
                </Typography>
              </Box>
            ))
          )}
        </Box>
      )}
      
      {/* Reply form */}
      {showReplyForm && (
        <Box sx={{ mt: 2, ml: 4 }}>
          <TextField
            fullWidth
            multiline
            rows={2}
            placeholder="Write a reply..."
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            variant="outlined"
            size="small"
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
            <Button 
              onClick={() => setShowReplyForm(false)} 
              sx={{ mr: 1 }}
            >
              Cancel
            </Button>
            <Button 
              variant="contained" 
              onClick={handleSubmitReply}
              disabled={!replyContent.trim() || submitting}
            >
              {submitting ? <CircularProgress size={24} /> : 'Reply'}
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default CommentThread;