import React, { createContext, useContext, useState } from 'react';
import { knowledgeGraphColorSchemes } from '../theme';
import { useTheme } from '../contexts/ThemeContext';

// Define the types for visualization settings
interface VisualizationSettings {
  showLabels: boolean;
  highlightConnections: boolean;
  nodeSize: number;
  forceStrength: number;
  clusterByType: boolean;
  maxRelationshipDepth: number;
  showRelationshipLabels: boolean;
  timeBasedLayout: boolean;
  darkMode: boolean;
  filterThreshold: number;
  importanceThreshold: number;
  progressiveLoading: boolean;
  levelOfDetail: boolean;
  tableView: boolean;
}

// Define the types for analysis settings
interface AnalysisSettings {
  showCentralityMetrics: boolean;
  pathfindingEnabled: boolean;
  showDomainClusters: boolean;
  highlightTrendingEntities: boolean;
  showPublicationTimeline: boolean;
  detectCommunities: boolean;
  identifyResearchFrontiers: boolean;
}

// Define the context type
interface KnowledgeGraphSettingsContextType {
  visualizationSettings: VisualizationSettings;
  setVisualizationSettings: React.Dispatch<React.SetStateAction<VisualizationSettings>>;
  analysisSettings: AnalysisSettings;
  setAnalysisSettings: React.Dispatch<React.SetStateAction<AnalysisSettings>>;
  entityColors: Record<string, string>;
}

// Create context with a default value
const KnowledgeGraphSettingsContext = createContext<KnowledgeGraphSettingsContextType>({
  visualizationSettings: {
    showLabels: true,
    highlightConnections: true,
    nodeSize: 7,
    forceStrength: 500,
    clusterByType: false,
    maxRelationshipDepth: 2,
    showRelationshipLabels: false,
    timeBasedLayout: false,
    darkMode: false,
    filterThreshold: 100,
    importanceThreshold: 0.5,
    progressiveLoading: false,
    levelOfDetail: true,
    tableView: false
  },
  setVisualizationSettings: () => {},
  analysisSettings: {
    showCentralityMetrics: false,
    pathfindingEnabled: false,
    showDomainClusters: false,
    highlightTrendingEntities: false,
    showPublicationTimeline: false,
    detectCommunities: false,
    identifyResearchFrontiers: false
  },
  setAnalysisSettings: () => {},
  entityColors: knowledgeGraphColorSchemes.standard
});

// Provider component
export const KnowledgeGraphSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isHighContrast, isDarkMode } = useTheme();
  
  // Initialize state for visualization settings
  const [visualizationSettings, setVisualizationSettings] = useState<VisualizationSettings>({
    showLabels: true,
    highlightConnections: true,
    nodeSize: 7,
    forceStrength: 500,
    clusterByType: false,
    maxRelationshipDepth: 2,
    showRelationshipLabels: false,
    timeBasedLayout: false,
    darkMode: false,
    filterThreshold: 100,
    importanceThreshold: 0.5,
    progressiveLoading: false,
    levelOfDetail: true,
    tableView: false
  });
  
  // Initialize state for analysis settings
  const [analysisSettings, setAnalysisSettings] = useState<AnalysisSettings>({
    showCentralityMetrics: false,
    pathfindingEnabled: false,
    showDomainClusters: false,
    highlightTrendingEntities: false,
    showPublicationTimeline: false,
    detectCommunities: false,
    identifyResearchFrontiers: false
  });
  
  // Select appropriate color scheme based on theme settings
  const getColorScheme = () => {
    if (isHighContrast) {
      return isDarkMode 
        ? knowledgeGraphColorSchemes.highContrastDark
        : knowledgeGraphColorSchemes.highContrastLight;
    }
    return knowledgeGraphColorSchemes.standard;
  };
  
  // Colors for different entity types - dynamically updates with theme changes
  const entityColors = getColorScheme();
  
  return (
    <KnowledgeGraphSettingsContext.Provider 
      value={{ 
        visualizationSettings, 
        setVisualizationSettings,
        analysisSettings,
        setAnalysisSettings,
        entityColors
      }}
    >
      {children}
    </KnowledgeGraphSettingsContext.Provider>
  );
};

// Custom hook to use the context
export const useKnowledgeGraphSettings = () => useContext(KnowledgeGraphSettingsContext);

export default KnowledgeGraphSettingsProvider;