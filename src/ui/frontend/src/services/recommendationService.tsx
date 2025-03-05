import React from 'react';
import { 
  ResearchRecommendation, 
  ResearchRecommendationGroup, 
  ResearchInsight,
  Tag 
} from '../types/research';
import { useFetchQuery, useFetchMutation } from '../hooks';
import { SavedQuery } from './researchService';

// Mock recommendations generator based on tags and previous queries
const generateMockRecommendations = (
  tags: Tag[] = [], 
  savedQueries: SavedQuery[] = []
): ResearchRecommendationGroup[] => {
  // Extract query terms for analysis
  const queryTerms = savedQueries.map(q => q.query.toLowerCase().split(' ')).flat();
  const uniqueTerms = [...new Set(queryTerms)].filter(term => term.length > 4);
  
  // Default groups if no data is available
  if (tags.length === 0 && savedQueries.length === 0) {
    return [
      {
        id: 'default-recs',
        title: 'Getting Started with AI Research',
        description: 'Recommended starting points for AI research',
        recommendations: [
          {
            id: 'rec-1',
            title: 'Explore Large Language Models',
            description: 'Learn about the capabilities and limitations of modern LLMs like GPT-4 and Claude.',
            confidence: 0.89,
            basedOn: [
              { type: 'history', patternId: 'new-user', patternDescription: 'New user onboarding' }
            ],
            suggestedQueryText: 'Latest advancements in large language models'
          },
          {
            id: 'rec-2',
            title: 'Neural Network Architectures',
            description: 'Understand the fundamental architectures behind modern AI systems.',
            confidence: 0.78,
            basedOn: [
              { type: 'history', patternId: 'new-user', patternDescription: 'New user onboarding' }
            ],
            suggestedQueryText: 'Common neural network architectures explained'
          }
        ]
      }
    ];
  }
  
  // Create tag-based recommendations
  const tagBasedRecs: ResearchRecommendation[] = tags
    .filter(tag => tag.count && tag.count > 5)
    .slice(0, 3)
    .map(tag => {
      const suggestedQueries = [
        `Latest research in ${tag.name}`,
        `${tag.name} advancements 2025`,
        `Future of ${tag.name} technology`
      ];
      
      return {
        id: `tag-rec-${tag.id}`,
        title: `${tag.name} Research Expansion`,
        description: `Explore the latest developments in ${tag.name} based on your research interests.`,
        confidence: 0.7 + (Math.random() * 0.2),
        basedOn: [
          { type: 'tag', tagId: tag.id, tagName: tag.name }
        ],
        tags: [tag],
        suggestedQueryText: suggestedQueries[Math.floor(Math.random() * suggestedQueries.length)]
      };
    });
  
  // Create combination recommendations (pairs of tags)
  const tagPairRecs: ResearchRecommendation[] = [];
  
  if (tags.length >= 2) {
    for (let i = 0; i < Math.min(2, tags.length - 1); i++) {
      const tag1 = tags[i];
      const tag2 = tags[i + 1];
      
      tagPairRecs.push({
        id: `tag-pair-${tag1.id}-${tag2.id}`,
        title: `${tag1.name} + ${tag2.name} Intersection`,
        description: `Explore the intersection of ${tag1.name} and ${tag2.name} for unique research insights.`,
        confidence: 0.6 + (Math.random() * 0.3),
        basedOn: [
          { type: 'tag', tagId: tag1.id, tagName: tag1.name },
          { type: 'tag', tagId: tag2.id, tagName: tag2.name }
        ],
        tags: [tag1, tag2],
        suggestedQueryText: `${tag1.name} combined with ${tag2.name} applications`
      });
    }
  }
  
  // Create query-based recommendations
  const queryBasedRecs: ResearchRecommendation[] = savedQueries
    .slice(0, Math.min(3, savedQueries.length))
    .map(query => {
      // For each query, create a recommendation to extend that research
      const enhancedQuery = query.query + ' latest advancements';
      
      return {
        id: `query-rec-${query.id}`,
        title: `Continue Research on "${truncateText(query.query, 30)}"`,
        description: `Expand your existing research about ${truncateText(query.query, 50)} with the latest developments.`,
        confidence: 0.65 + (Math.random() * 0.2),
        basedOn: [
          { type: 'query', queryId: query.id, queryText: query.query }
        ],
        tags: query.tags,
        suggestedQueryText: enhancedQuery
      };
    });
  
  // Create trending topics recommendations based on user's interests
  const interestAreas = [...new Set([...tags.map(t => t.name), ...uniqueTerms.slice(0, 5)])];
  
  const trendingTopics: ResearchRecommendation[] = [
    {
      id: 'trend-rec-1',
      title: 'Multi-Modal LLMs',
      description: 'Explore the latest in models that combine text, image, and audio understanding.',
      confidence: 0.85,
      basedOn: [
        { type: 'history', patternId: 'trending', patternDescription: 'Current trending AI topic' }
      ],
      suggestedQueryText: 'Multi-modal language models capabilities'
    },
    {
      id: 'trend-rec-2',
      title: 'Foundation Models for Specialized Domains',
      description: 'Research into domain-specific adaptations of large foundation models.',
      confidence: 0.82,
      basedOn: [
        { type: 'history', patternId: 'trending', patternDescription: 'Current trending AI topic' }
      ],
      suggestedQueryText: 'Domain-specific foundation models in AI'
    },
    {
      id: 'trend-rec-3',
      title: 'AI System Agents',
      description: 'Recent developments in autonomous AI systems and multi-agent frameworks.',
      confidence: 0.79,
      basedOn: [
        { type: 'history', patternId: 'trending', patternDescription: 'Current trending AI topic' }
      ],
      suggestedQueryText: 'Autonomous AI agent systems architecture'
    }
  ];
  
  // Assemble recommendation groups
  const recommendationGroups: ResearchRecommendationGroup[] = [
    {
      id: 'based-on-tags',
      title: 'Based on Your Research Interests',
      description: 'Recommendations derived from your most-used research tags',
      recommendations: tagBasedRecs.concat(tagPairRecs).slice(0, 4)
    },
    {
      id: 'based-on-queries',
      title: 'Continue Your Research',
      description: 'Suggestions to extend your previous research queries',
      recommendations: queryBasedRecs
    },
    {
      id: 'trending-topics',
      title: 'Trending AI Research Topics',
      description: 'Hot topics in AI research you might want to explore',
      recommendations: trendingTopics
    }
  ];
  
  // Filter out empty groups
  return recommendationGroups.filter(group => group.recommendations.length > 0);
};

// Generate mock insights about research behavior
const generateMockInsights = (
  tags: Tag[] = [], 
  savedQueries: SavedQuery[] = []
): ResearchInsight[] => {
  const hasData = tags.length > 0 || savedQueries.length > 0;
  
  if (!hasData) {
    return [
      {
        id: 'insight-onboarding',
        type: 'suggestion',
        title: 'Start Your Research Journey',
        description: 'Begin by saving research queries and adding tags to get personalized insights.',
        importance: 'medium',
        iconType: 'lightbulb'
      }
    ];
  }
  
  const insights: ResearchInsight[] = [];
  
  // Tag-based insights
  if (tags.length > 0) {
    const topTags = [...tags].sort((a, b) => (b.count || 0) - (a.count || 0)).slice(0, 3);
    
    if (topTags.length > 0) {
      insights.push({
        id: 'insight-top-tag',
        type: 'pattern',
        title: `${topTags[0].name} is Your Main Research Focus`,
        description: `You've used the "${topTags[0].name}" tag most frequently, indicating a strong research interest in this area.`,
        importance: 'medium',
        relatedTags: [topTags[0]],
        iconType: 'analytics'
      });
    }
    
    // Check for tag gaps
    const tagNames = tags.map(t => t.name.toLowerCase());
    const relatedAreas = {
      'machine learning': ['neural networks', 'deep learning', 'supervised learning'],
      'nlp': ['transformers', 'bert', 'language models'],
      'computer vision': ['image recognition', 'object detection', 'cnn'],
      'reinforcement learning': ['q-learning', 'policy gradient', 'markov decision']
    };
    
    // Find potential gaps based on user's interests
    for (const [area, relatedTerms] of Object.entries(relatedAreas)) {
      if (tagNames.includes(area)) {
        const missingTerms = relatedTerms.filter(term => !tagNames.includes(term));
        if (missingTerms.length > 0) {
          insights.push({
            id: `insight-gap-${area}`,
            type: 'gap',
            title: `Potential Research Gap in ${area.toUpperCase()}`,
            description: `Your research in ${area} might benefit from exploring ${missingTerms.slice(0, 2).join(', ')}.`,
            importance: 'medium',
            relatedTags: tags.filter(t => t.name.toLowerCase() === area),
            iconType: 'explore'
          });
          break; // Just suggest one gap at a time
        }
      }
    }
  }
  
  // Query pattern insights
  if (savedQueries.length > 0) {
    // Look for repeating terms
    const allTerms = savedQueries.flatMap(q => 
      q.query.toLowerCase()
        .split(' ')
        .filter(term => term.length > 4)
    );
    
    // Count term frequency
    const termFrequency: Record<string, number> = {};
    allTerms.forEach(term => {
      termFrequency[term] = (termFrequency[term] || 0) + 1;
    });
    
    // Find top recurring terms
    const topTerms = Object.entries(termFrequency)
      .sort((a, b) => b[1] - a[1])
      .filter(([_, count]) => count > 1)
      .slice(0, 3)
      .map(([term]) => term);
    
    if (topTerms.length > 0) {
      insights.push({
        id: 'insight-recurring-terms',
        type: 'trend',
        title: 'Recurring Research Themes',
        description: `Terms like "${topTerms.join('", "')}" appear frequently in your queries, showing consistent research interests.`,
        importance: 'high',
        iconType: 'trending_up'
      });
    }
    
    // Time-based patterns
    const timestamps = savedQueries
      .map(q => new Date(q.createdAt).getTime())
      .sort((a, b) => a - b);
    
    if (timestamps.length >= 3) {
      // Check if there's a consistent research pattern (regular intervals)
      const intervals = [];
      for (let i = 1; i < timestamps.length; i++) {
        intervals.push(timestamps[i] - timestamps[i-1]);
      }
      
      const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
      const daysBetween = Math.round(avgInterval / (1000 * 60 * 60 * 24));
      
      if (daysBetween > 0 && daysBetween < 14) {  // Only suggest for patterns less than 2 weeks
        insights.push({
          id: 'insight-research-cadence',
          type: 'pattern',
          title: 'Consistent Research Pattern',
          description: `You typically conduct research every ${daysBetween} days. Setting a research schedule can improve knowledge retention.`,
          importance: 'low',
          iconType: 'schedule'
        });
      }
    }
  }
  
  // Add a suggestion if we have enough data
  if (savedQueries.length >= 5) {
    insights.push({
      id: 'insight-suggestion-export',
      type: 'suggestion',
      title: 'Create a Research Portfolio',
      description: 'You have a substantial collection of research. Consider exporting your findings into a structured document to share with others.',
      importance: 'high',
      iconType: 'assignment'
    });
  }
  
  return insights;
};

// Helper to truncate text with ellipsis
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Hook to fetch research recommendations with React Query
 */
export function useRecommendations(tags: Tag[] = [], savedQueries: SavedQuery[] = []) {
  return useFetchQuery<ResearchRecommendationGroup[]>({
    url: '/research/recommendations',
    queryOptions: {
      staleTime: 1000 * 60 * 15, // 15 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: () => {
      return generateMockRecommendations(tags, savedQueries);
    }
  });
}

/**
 * Hook to fetch research insights with React Query
 */
export function useResearchInsights(tags: Tag[] = [], savedQueries: SavedQuery[] = []) {
  return useFetchQuery<ResearchInsight[]>({
    url: '/research/insights',
    queryOptions: {
      staleTime: 1000 * 60 * 30, // 30 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: () => {
      return generateMockInsights(tags, savedQueries);
    }
  });
}

/**
 * Hook to save a recommendation for later reference
 */
export function useSaveRecommendation() {
  return useFetchMutation<{ success: boolean }, { recommendationId: string }>({
    url: '/research/recommendations/save',
    method: 'POST',
    mockData: () => {
      return { success: true };
    }
  });
}

export default {
  useRecommendations,
  useResearchInsights,
  useSaveRecommendation
};