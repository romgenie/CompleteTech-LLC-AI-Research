import React, { useState, useEffect } from 'react';
import {
  Box, 
  Container, 
  Typography, 
  Paper, 
  Grid, 
  Chip,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
  Alert,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Breadcrumbs,
  Link,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowRightAltIcon from '@mui/icons-material/ArrowRightAlt';
import LabelIcon from '@mui/icons-material/Label';
import AddIcon from '@mui/icons-material/Add';
import MergeIcon from '@mui/icons-material/Merge';
import { ChromePicker } from 'react-color';
import { useAllTags } from '../services/researchService';
import { Tag } from '../types/research';

/**
 * Page for managing research tags
 */
const TagManagementPage: React.FC = () => {
  // For a real app, these would come from API calls
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Tag editing
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [currentTag, setCurrentTag] = useState<Tag | null>(null);
  const [tagName, setTagName] = useState<string>('');
  const [tagDescription, setTagDescription] = useState<string>('');
  const [tagColor, setTagColor] = useState<string>('#2196f3');
  
  // Merge dialog
  const [openMergeDialog, setOpenMergeDialog] = useState<boolean>(false);
  const [sourceTag, setSourceTag] = useState<string>('');
  const [targetTag, setTargetTag] = useState<string>('');
  
  // Color picker
  const [displayColorPicker, setDisplayColorPicker] = useState<boolean>(false);

  // Demo data
  const tagsQuery = useAllTags();
  const defaultTagCounts = {
    'NLP': 24,
    'Machine Learning': 37,
    'Neural Networks': 18,
    'Transformers': 42,
    'Computer Vision': 15,
    'LLM': 35,
    'GPT': 22,
    'BERT': 12,
    'Fine-tuning': 9,
    'Embeddings': 14,
    'Reinforcement Learning': 7,
    'Deep Learning': 28
  };
  
  // Generate random colors for tags
  const generateRandomColor = () => {
    const colors = [
      '#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', 
      '#03a9f4', '#00bcd4', '#009688', '#4caf50', '#8bc34a', '#cddc39',
      '#ffc107', '#ff9800', '#ff5722', '#795548', '#607d8b'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  };
  
  // Initialize with mock data
  useEffect(() => {
    const initTags = async () => {
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Create mock tags from the tag counts
        const mockTags: Tag[] = Object.entries(defaultTagCounts).map(([name, count]) => ({
          id: `tag-${name.toLowerCase().replace(/\s+/g, '-')}`,
          name,
          color: generateRandomColor(),
          description: `Tag for ${name} related research`,
          count
        }));
        
        setTags(mockTags);
        setLoading(false);
      } catch (error) {
        setError('Failed to load tags');
        setLoading(false);
      }
    };
    
    initTags();
  }, []);
  
  // Handle dialog close
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentTag(null);
    setTagName('');
    setTagDescription('');
    setTagColor('#2196f3');
    setDisplayColorPicker(false);
  };
  
  // Open edit dialog
  const handleOpenEditDialog = (tag: Tag) => {
    setCurrentTag(tag);
    setTagName(tag.name);
    setTagDescription(tag.description || '');
    setTagColor(tag.color || '#2196f3');
    setDialogMode('edit');
    setOpenDialog(true);
  };
  
  // Open create dialog
  const handleOpenCreateDialog = () => {
    setCurrentTag(null);
    setTagName('');
    setTagDescription('');
    setTagColor('#2196f3');
    setDialogMode('create');
    setOpenDialog(true);
  };
  
  // Save tag
  const handleSaveTag = () => {
    if (!tagName.trim()) return;
    
    if (dialogMode === 'create') {
      // Create new tag
      const newTag: Tag = {
        id: `tag-${Date.now()}`,
        name: tagName,
        description: tagDescription,
        color: tagColor,
        count: 0
      };
      
      setTags(prevTags => [...prevTags, newTag]);
    } else if (dialogMode === 'edit' && currentTag) {
      // Update existing tag
      setTags(prevTags => 
        prevTags.map(tag => 
          tag.id === currentTag.id 
            ? { ...tag, name: tagName, description: tagDescription, color: tagColor }
            : tag
        )
      );
    }
    
    handleCloseDialog();
  };
  
  // Delete tag
  const handleDeleteTag = (tagId: string) => {
    if (window.confirm('Are you sure you want to delete this tag? This action cannot be undone.')) {
      setTags(prevTags => prevTags.filter(tag => tag.id !== tagId));
    }
  };
  
  // Handle merge dialog
  const handleCloseMergeDialog = () => {
    setOpenMergeDialog(false);
    setSourceTag('');
    setTargetTag('');
  };
  
  // Open merge dialog
  const handleOpenMergeDialog = () => {
    setOpenMergeDialog(true);
  };
  
  // Merge tags
  const handleMergeTags = () => {
    if (!sourceTag || !targetTag || sourceTag === targetTag) {
      alert('Please select different source and target tags');
      return;
    }
    
    // Find tags
    const source = tags.find(tag => tag.id === sourceTag);
    const target = tags.find(tag => tag.id === targetTag);
    
    if (!source || !target) {
      alert('Selected tags not found');
      return;
    }
    
    // Merge by adding counts and removing source tag
    setTags(prevTags => 
      prevTags.map(tag => 
        tag.id === targetTag 
          ? { ...tag, count: (tag.count || 0) + (source.count || 0) }
          : tag
      ).filter(tag => tag.id !== sourceTag)
    );
    
    handleCloseMergeDialog();
  };
  
  return (
    <Container maxWidth="lg">
      <Box my={4}>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb" sx={{ mb: 2 }}>
          <Link component={RouterLink} to="/" color="inherit">
            Dashboard
          </Link>
          <Link component={RouterLink} to="/research" color="inherit">
            Research
          </Link>
          <Typography color="text.primary">Tag Management</Typography>
        </Breadcrumbs>
        
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            <LabelIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Tag Management
          </Typography>
          
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<MergeIcon />}
              onClick={handleOpenMergeDialog}
              sx={{ mr: 2 }}
              disabled={tags.length < 2}
            >
              Merge Tags
            </Button>
            
            <Button 
              variant="contained" 
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleOpenCreateDialog}
            >
              Create Tag
            </Button>
          </Box>
        </Box>
        
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Create, edit, and organize tags for your research queries
        </Typography>
        
        <Divider sx={{ my: 3 }} />
        
        {loading ? (
          <Box display="flex" justifyContent="center" my={5}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        ) : (
          <>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <TableContainer component={Paper} elevation={2}>
                  <Table aria-label="tags table">
                    <TableHead>
                      <TableRow>
                        <TableCell>Tag</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell align="center">Usage</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tags.map((tag) => (
                        <TableRow key={tag.id}>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              <Chip 
                                label={tag.name} 
                                size="small"
                                sx={{ 
                                  backgroundColor: tag.color,
                                  color: tag.color && isColorDark(tag.color) ? 'white' : 'black',
                                  mr: 1 
                                }}
                              />
                            </Box>
                          </TableCell>
                          <TableCell>{tag.description || '-'}</TableCell>
                          <TableCell align="center">{tag.count || 0}</TableCell>
                          <TableCell align="right">
                            <Tooltip title="Edit tag">
                              <IconButton 
                                size="small" 
                                onClick={() => handleOpenEditDialog(tag)}
                                sx={{ mr: 1 }}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            
                            <Tooltip title="Delete tag">
                              <IconButton 
                                size="small" 
                                onClick={() => handleDeleteTag(tag.id)}
                                color="error"
                                disabled={tag.count > 0}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Tag Usage Help
                  </Typography>
                  
                  <Typography variant="body2" paragraph>
                    Tags help you organize and filter your research queries and results.
                  </Typography>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Creating effective tags</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" paragraph>
                        Good tags are concise, specific, and consistent. Consider these tips:
                      </Typography>
                      <ul>
                        <li>Use specific keywords rather than general ones</li>
                        <li>Be consistent with capitalization and formatting</li>
                        <li>Use color coding for visual categorization</li>
                        <li>Consider hierarchical relationships (e.g., "ML" as parent to "Neural Networks")</li>
                      </ul>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Using tags effectively</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2">
                        Tags can be applied to:
                      </Typography>
                      <ul>
                        <li>Saved research queries</li>
                        <li>Research results and reports</li>
                        <li>Generated documents</li>
                      </ul>
                      <Typography variant="body2" sx={{ mt: 2 }}>
                        Use the filter panel in the Research page to filter by tags.
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>Managing tag relationships</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" paragraph>
                        When your tag collection grows too large:
                      </Typography>
                      <ul>
                        <li>Use the merge feature to combine similar tags</li>
                        <li>Delete unused tags to keep your system organized</li>
                        <li>Consider creating a tag hierarchy for better organization</li>
                      </ul>
                    </AccordionDetails>
                  </Accordion>
                </Paper>
              </Grid>
            </Grid>
            
            {tags.length > 0 && (
              <Box mt={4} mb={2}>
                <Typography variant="h6" gutterBottom>
                  Tag Cloud
                </Typography>
                <Paper elevation={2} sx={{ p: 3 }}>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {tags.map(tag => (
                      <Chip
                        key={tag.id}
                        label={tag.name}
                        sx={{ 
                          backgroundColor: tag.color,
                          color: tag.color && isColorDark(tag.color) ? 'white' : 'black',
                          fontSize: `${Math.max(0.8, Math.min(1.8, 0.8 + (tag.count || 0) / 50))}rem`,
                          height: 'auto',
                          '& .MuiChip-label': {
                            padding: '8px 12px',
                          }
                        }}
                      />
                    ))}
                  </Box>
                </Paper>
              </Box>
            )}
          </>
        )}
      </Box>
      
      {/* Create/Edit Tag Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' ? 'Create New Tag' : 'Edit Tag'}
        </DialogTitle>
        <DialogContent>
          <Box py={1}>
            <TextField
              label="Tag Name"
              fullWidth
              value={tagName}
              onChange={(e) => setTagName(e.target.value)}
              margin="normal"
              required
            />
            
            <TextField
              label="Description"
              fullWidth
              value={tagDescription}
              onChange={(e) => setTagDescription(e.target.value)}
              margin="normal"
              multiline
              rows={2}
            />
            
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Tag Color
              </Typography>
              
              <Box display="flex" alignItems="center">
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: 1,
                    backgroundColor: tagColor,
                    cursor: 'pointer',
                    border: '1px solid #ccc'
                  }}
                  onClick={() => setDisplayColorPicker(!displayColorPicker)}
                />
                
                <Typography variant="body2" sx={{ ml: 2 }}>
                  {tagColor}
                </Typography>
              </Box>
              
              {displayColorPicker && (
                <Box mt={2} position="relative" zIndex={1}>
                  <Box 
                    position="fixed" 
                    top={0} 
                    right={0} 
                    bottom={0} 
                    left={0} 
                    onClick={() => setDisplayColorPicker(false)} 
                  />
                  <Box position="relative">
                    <ChromePicker 
                      color={tagColor} 
                      onChange={(color) => setTagColor(color.hex)} 
                    />
                  </Box>
                </Box>
              )}
              
              <Box mt={3}>
                <Typography variant="subtitle2" gutterBottom>
                  Preview
                </Typography>
                
                <Chip
                  label={tagName || 'Tag Preview'}
                  sx={{ 
                    backgroundColor: tagColor,
                    color: isColorDark(tagColor) ? 'white' : 'black',
                  }}
                />
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSaveTag} 
            variant="contained" 
            color="primary"
            disabled={!tagName.trim()}
          >
            {dialogMode === 'create' ? 'Create' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Merge Tags Dialog */}
      <Dialog open={openMergeDialog} onClose={handleCloseMergeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Merge Tags
        </DialogTitle>
        <DialogContent>
          <Box py={1}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Merging will combine all queries from the source tag into the target tag, then delete the source tag.
            </Alert>
            
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={5}>
                <TextField
                  select
                  label="Source Tag"
                  fullWidth
                  value={sourceTag}
                  onChange={(e) => setSourceTag(e.target.value)}
                  margin="normal"
                  required
                  SelectProps={{
                    native: true,
                  }}
                >
                  <option value="">Select source tag</option>
                  {tags.map((tag) => (
                    <option key={`source-${tag.id}`} value={tag.id}>
                      {tag.name} ({tag.count || 0})
                    </option>
                  ))}
                </TextField>
              </Grid>
              
              <Grid item xs={2} sx={{ textAlign: 'center' }}>
                <ArrowRightAltIcon fontSize="large" color="action" />
              </Grid>
              
              <Grid item xs={5}>
                <TextField
                  select
                  label="Target Tag"
                  fullWidth
                  value={targetTag}
                  onChange={(e) => setTargetTag(e.target.value)}
                  margin="normal"
                  required
                  SelectProps={{
                    native: true,
                  }}
                >
                  <option value="">Select target tag</option>
                  {tags.map((tag) => (
                    <option key={`target-${tag.id}`} value={tag.id}>
                      {tag.name} ({tag.count || 0})
                    </option>
                  ))}
                </TextField>
              </Grid>
            </Grid>
            
            {sourceTag && targetTag && sourceTag !== targetTag && (
              <Box mt={3} p={2} bgcolor="background.default" borderRadius={1}>
                <Typography variant="subtitle2" gutterBottom>
                  Merge Preview
                </Typography>
                
                <Box display="flex" alignItems="center" mt={1}>
                  <Box>
                    <Chip
                      label={tags.find(t => t.id === sourceTag)?.name || ''}
                      size="small"
                      sx={{ 
                        backgroundColor: tags.find(t => t.id === sourceTag)?.color,
                        color: tags.find(t => t.id === sourceTag)?.color && 
                          isColorDark(tags.find(t => t.id === sourceTag)?.color || '') ? 'white' : 'black',
                      }}
                    />
                    <Typography variant="caption" display="block" mt={0.5}>
                      {tags.find(t => t.id === sourceTag)?.count || 0} queries
                    </Typography>
                  </Box>
                  
                  <ArrowRightAltIcon sx={{ mx: 2 }} />
                  
                  <Box>
                    <Chip
                      label={tags.find(t => t.id === targetTag)?.name || ''}
                      size="small"
                      sx={{ 
                        backgroundColor: tags.find(t => t.id === targetTag)?.color,
                        color: tags.find(t => t.id === targetTag)?.color && 
                          isColorDark(tags.find(t => t.id === targetTag)?.color || '') ? 'white' : 'black',
                      }}
                    />
                    <Typography variant="caption" display="block" mt={0.5}>
                      {(tags.find(t => t.id === targetTag)?.count || 0) + 
                       (tags.find(t => t.id === sourceTag)?.count || 0)} queries after merge
                    </Typography>
                  </Box>
                </Box>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseMergeDialog}>Cancel</Button>
          <Button 
            onClick={handleMergeTags} 
            variant="contained" 
            color="primary"
            disabled={!sourceTag || !targetTag || sourceTag === targetTag}
          >
            Merge Tags
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

// Utility function to determine if a color is dark (for text contrast)
function isColorDark(hexColor: string): boolean {
  // Remove the hash if it exists
  hexColor = hexColor.replace('#', '');
  
  // Parse the hex color
  const r = parseInt(hexColor.substr(0, 2), 16);
  const g = parseInt(hexColor.substr(2, 2), 16);
  const b = parseInt(hexColor.substr(4, 2), 16);
  
  // Calculate perceived brightness (YIQ formula)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  
  // Return true if the color is dark
  return yiq < 128;
}

export default TagManagementPage;