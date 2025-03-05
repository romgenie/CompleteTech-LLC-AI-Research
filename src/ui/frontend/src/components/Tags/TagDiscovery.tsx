import React, { useState, useEffect } from 'react';
import { Box, Typography, Tabs, Tab, Divider, TextField, Button, Chip, Grid, Card, CardContent, CircularProgress, IconButton, Tooltip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import InfoIcon from '@mui/icons-material/Info';
import PersonIcon from '@mui/icons-material/Person';
import PeopleIcon from '@mui/icons-material/People';
import PublicIcon from '@mui/icons-material/Public';

import { Tag, TagSuggestion } from '../../types/research';
import { usePopularTags, useGlobalTags, useSharedTags, useTagSuggestions, useCreateTag } from '../../services/tagsService';
import { useTaxonomies } from '../../services/taxonomyService';

interface TagDiscoveryProps {
  onTagSelect?: (tag: Tag) => void;
  selectedTagIds?: string[];
}

/**
 * Component for discovering and exploring shared and popular tags
 */
const TagDiscovery: React.FC<TagDiscoveryProps> = ({ onTagSelect, selectedTagIds = [] }) => {
  const [activeTab, setActiveTab] = useState<string>('popular');
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Fetch different tag collections
  const { data: popularTags, isLoading: isLoadingPopular } = usePopularTags();
  const { data: globalTags, isLoading: isLoadingGlobal } = useGlobalTags();
  const { data: sharedTags, isLoading: isLoadingShared } = useSharedTags();
  const { data: taxonomies, isLoading: isLoadingTaxonomies } = useTaxonomies();
  const { data: suggestions, isLoading: isLoadingSuggestions } = 
    useTagSuggestions(searchQuery, undefined);
    
  const createTagMutation = useCreateTag();

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveTab(newValue);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleTagSelect = (tag: Tag) => {
    if (onTagSelect) {
      onTagSelect(tag);
    }
  };

  const handleAddSuggestion = async (suggestion: TagSuggestion) => {
    try {
      // Create new tag from suggestion
      const newTag = await createTagMutation.mutateAsync({
        name: suggestion.name,
        parentId: suggestion.parentId,
        taxonomyId: suggestion.taxonomy
      });
      
      // Select the newly created tag
      if (onTagSelect) {
        onTagSelect(newTag);
      }
    } catch (error) {
      console.error('Failed to create tag from suggestion:', error);
    }
  };

  // Filter tags based on search query
  const filterTags = (tags: Tag[] = []): Tag[] => {
    if (!searchQuery) return tags;
    return tags.filter(tag => 
      tag.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tag.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  const renderTagCard = (tag: Tag) => {
    const isSelected = selectedTagIds.includes(tag.id);
    const visibilityIcon = tag.visibility === 'private' 
      ? <PersonIcon fontSize="small" /> 
      : tag.visibility === 'shared' 
        ? <PeopleIcon fontSize="small" />
        : <PublicIcon fontSize="small" />;
    
    return (
      <Card 
        key={tag.id} 
        variant="outlined" 
        sx={{ 
          mb: 1, 
          cursor: 'pointer',
          border: isSelected ? `2px solid ${tag.color || '#1976d2'}` : undefined,
          backgroundColor: isSelected ? 'rgba(25, 118, 210, 0.08)' : undefined
        }}
        onClick={() => handleTagSelect(tag)}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="subtitle1" component="div" sx={{ display: 'flex', alignItems: 'center' }}>
              <Box 
                component="span" 
                sx={{ 
                  width: 12, 
                  height: 12, 
                  borderRadius: '50%', 
                  backgroundColor: tag.color || '#ccc',
                  display: 'inline-block',
                  mr: 1
                }} 
              />
              {tag.name}
            </Typography>
            <Box>
              <Tooltip title={`Visibility: ${tag.visibility}`}>
                {visibilityIcon}
              </Tooltip>
              <Tooltip title="Add to favorites">
                <IconButton size="small">
                  <FavoriteBorderIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          {tag.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {tag.description}
            </Typography>
          )}
          <Box mt={1}>
            {tag.usageCount && (
              <Chip 
                size="small" 
                label={`Used by ${tag.usageCount} users`} 
                variant="outlined"
                sx={{ mr: 1, mb: 1 }}
              />
            )}
            {tag.path && (
              <Chip 
                size="small" 
                label={tag.path} 
                variant="outlined"
                sx={{ mr: 1, mb: 1 }}
              />
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };

  const renderSuggestionCard = (suggestion: TagSuggestion) => {
    return (
      <Card key={suggestion.id} variant="outlined" sx={{ mb: 1 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="subtitle1" component="div">
              {suggestion.name}
            </Typography>
            <Button 
              variant="outlined" 
              size="small" 
              startIcon={<AddIcon />}
              onClick={() => handleAddSuggestion(suggestion)}
            >
              Add
            </Button>
          </Box>
          <Box mt={1}>
            <Chip 
              size="small" 
              label={`Confidence: ${Math.round(suggestion.confidence * 100)}%`} 
              color={suggestion.confidence > 0.8 ? "success" : suggestion.confidence > 0.5 ? "primary" : "default"}
              variant="outlined"
              sx={{ mr: 1 }}
            />
            <Chip 
              size="small" 
              label={`Reason: ${suggestion.reason}`} 
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Discover Tags
      </Typography>
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Search for tags..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </Box>
      
      <Tabs 
        value={activeTab} 
        onChange={handleTabChange} 
        indicatorColor="primary"
        textColor="primary"
        variant="fullWidth"
      >
        <Tab label="Popular" value="popular" />
        <Tab label="Suggestions" value="suggestions" />
        <Tab label="Global" value="global" />
        <Tab label="Shared" value="shared" />
        <Tab label="Taxonomies" value="taxonomies" />
      </Tabs>
      
      <Divider sx={{ mb: 2 }} />
      
      {/* Popular Tags Tab */}
      {activeTab === 'popular' && (
        <Box>
          {isLoadingPopular ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={32} />
            </Box>
          ) : (
            filterTags(popularTags).length > 0 ? (
              filterTags(popularTags).map(tag => renderTagCard(tag))
            ) : (
              <Typography color="text.secondary" align="center" py={4}>
                No popular tags found{searchQuery ? ` matching "${searchQuery}"` : ''}
              </Typography>
            )
          )}
        </Box>
      )}
      
      {/* Suggestions Tab */}
      {activeTab === 'suggestions' && (
        <Box>
          {isLoadingSuggestions ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={32} />
            </Box>
          ) : (
            suggestions && suggestions.length > 0 ? (
              suggestions.map(suggestion => renderSuggestionCard(suggestion))
            ) : (
              <Typography color="text.secondary" align="center" py={4}>
                No tag suggestions available{searchQuery ? ` matching "${searchQuery}"` : ''}
              </Typography>
            )
          )}
        </Box>
      )}
      
      {/* Global Tags Tab */}
      {activeTab === 'global' && (
        <Box>
          {isLoadingGlobal ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={32} />
            </Box>
          ) : (
            filterTags(globalTags).length > 0 ? (
              filterTags(globalTags).map(tag => renderTagCard(tag))
            ) : (
              <Typography color="text.secondary" align="center" py={4}>
                No global tags found{searchQuery ? ` matching "${searchQuery}"` : ''}
              </Typography>
            )
          )}
        </Box>
      )}
      
      {/* Shared Tags Tab */}
      {activeTab === 'shared' && (
        <Box>
          {isLoadingShared ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={32} />
            </Box>
          ) : (
            filterTags(sharedTags).length > 0 ? (
              filterTags(sharedTags).map(tag => renderTagCard(tag))
            ) : (
              <Typography color="text.secondary" align="center" py={4}>
                No shared tags found{searchQuery ? ` matching "${searchQuery}"` : ''}
              </Typography>
            )
          )}
        </Box>
      )}
      
      {/* Taxonomies Tab */}
      {activeTab === 'taxonomies' && (
        <Box>
          {isLoadingTaxonomies ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={32} />
            </Box>
          ) : (
            taxonomies && taxonomies.length > 0 ? (
              taxonomies.map(taxonomy => (
                <Card key={taxonomy.id} variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle1" component="div">
                        {taxonomy.name}
                        {taxonomy.isOfficial && (
                          <Chip 
                            size="small" 
                            label="Official" 
                            color="primary"
                            sx={{ ml: 1 }}
                          />
                        )}
                      </Typography>
                      <Tooltip title="View Taxonomy">
                        <IconButton size="small">
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    {taxonomy.description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {taxonomy.description}
                      </Typography>
                    )}
                    {taxonomy.domain && (
                      <Chip 
                        size="small" 
                        label={`Domain: ${taxonomy.domain}`} 
                        variant="outlined"
                        sx={{ mt: 1 }}
                      />
                    )}
                  </CardContent>
                </Card>
              ))
            ) : (
              <Typography color="text.secondary" align="center" py={4}>
                No taxonomies found
              </Typography>
            )
          )}
        </Box>
      )}
    </Box>
  );
};

export default TagDiscovery;