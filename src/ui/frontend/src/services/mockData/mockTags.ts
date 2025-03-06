import { Tag, TagUsageStats, TagConflict } from '../../types/research';

export const mockTags: Tag[] = [
  {
    id: 'tag-1',
    name: 'Machine Learning',
    color: '#2196f3',
    description: 'Topics related to machine learning and AI',
    count: 150,
    visibility: 'public',
    usageCount: 250,
    popularity: 0.85
  },
  {
    id: 'tag-2',
    name: 'Neural Networks',
    color: '#f44336',
    description: 'Neural network architectures and training',
    parentId: 'tag-1',
    count: 75,
    visibility: 'public',
    usageCount: 120,
    popularity: 0.75
  },
  {
    id: 'tag-3',
    name: 'Computer Vision',
    color: '#4caf50',
    description: 'Image and video processing with AI',
    count: 90,
    visibility: 'public',
    usageCount: 180,
    popularity: 0.8
  }
];

export const mockTagStats: TagUsageStats = {
  tagId: 'tag-1',
  userCount: 250,
  itemCount: 150,
  dailyUse: Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    count: Math.floor(Math.random() * 20) + 1
  })),
  relatedTags: [
    { tagId: 'tag-2', cooccurrence: 0.75 },
    { tagId: 'tag-3', cooccurrence: 0.6 }
  ],
  trend: 'rising'
};

export const mockTagConflicts: TagConflict[] = [
  {
    id: 'conflict-1',
    tagId: 'tag-2',
    conflictType: 'hierarchy',
    description: 'Tag appears in multiple hierarchies',
    options: [
      {
        id: 'opt-1',
        description: 'Keep under Machine Learning',
        action: 'move',
        tagIds: ['tag-2'],
        newParentId: 'tag-1'
      },
      {
        id: 'opt-2',
        description: 'Create separate tag',
        action: 'split',
        tagIds: ['tag-2']
      }
    ],
    resolved: false,
    createdAt: new Date().toISOString()
  }
];