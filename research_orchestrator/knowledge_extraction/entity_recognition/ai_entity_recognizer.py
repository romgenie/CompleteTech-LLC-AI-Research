"""
AI Entity Recognizer module for the Knowledge Extraction Pipeline.

This module provides specialized functionality for identifying and categorizing
AI-specific entities within research documents, including models, algorithms,
datasets, metrics, and other AI-related concepts.
"""

import re
from typing import Dict, List, Optional, Set, Any, Tuple
import json
import logging
from pathlib import Path

from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import EntityRecognizer, Entity
from research_orchestrator.adapters.karma_adapter.karma_adapter import KARMAAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI entity types
AI_ENTITY_TYPES = [
    "model",
    "algorithm",
    "architecture",
    "dataset",
    "metric",
    "parameter",
    "hyperparameter",
    "framework",
    "library",
    "technique",
    "task",
    "benchmark"
]

# Default patterns for each entity type (simplified regex patterns for demonstration)
DEFAULT_PATTERNS = {
    "model": [
        r'\b(GPT-[0-9]+(?:-[A-Za-z]+)?)\b',
        r'\b(BERT(?:-[A-Za-z]+)?)\b',
        r'\b(T5(?:-[A-Za-z0-9]+)?)\b',
        r'\b(LLaMA(?:-[0-9]+(?:-[A-Za-z]+)?)?)\b',
        r'\b(Claude(?:-[0-9]+(?:\.[0-9]+)?(?:-[A-Za-z]+)?)?)\b',
        r'\b(Transformer(?:-[A-Za-z]+)?)\b',
        r'\b(ResNet(?:-[0-9]+)?)\b',
        r'\b(YOLO(?:v[0-9]+)?)\b'
    ],
    "dataset": [
        r'\b(ImageNet(?:-[0-9]+[K]?)?)\b',
        r'\b(COCO)\b',
        r'\b(MS-COCO)\b',
        r'\b(MNIST)\b',
        r'\b(CIFAR-[0-9]+)\b',
        r'\b(SQuAD(?:[0-9]+\.[0-9]+)?)\b',
        r'\b(GLUE)\b',
        r'\b(SuperGLUE)\b'
    ],
    "metric": [
        r'\b(accuracy)\b',
        r'\b(precision)\b',
        r'\b(recall)\b',
        r'\b(F1(?:-score)?)\b',
        r'\b(mAP)\b',
        r'\b(BLEU(?:-[0-9]+)?)\b',
        r'\b(ROUGE(?:-[LN][0-9]+)?)\b',
        r'\b(perplexity)\b'
    ],
    "framework": [
        r'\b(TensorFlow(?:[0-9]+\.[0-9]+)?)\b',
        r'\b(PyTorch(?:[0-9]+\.[0-9]+)?)\b',
        r'\b(Keras)\b',
        r'\b(Jax)\b',
        r'\b(MXNet)\b',
        r'\b(Scikit-[Ll]earn)\b',
        r'\b(Hugging Face)\b',
        r'\b(transformers)\b'
    ]
}


class AIEntityRecognizer(EntityRecognizer):
    """
    Specialized entity recognizer for AI research documents that identifies
    models, algorithms, datasets, metrics, and other AI-specific concepts.
    """
    
    def __init__(self, 
                 entity_types: Optional[List[str]] = None,
                 config_path: Optional[str] = None,
                 custom_patterns: Optional[Dict[str, List[str]]] = None,
                 use_karma: bool = False,
                 karma_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI entity recognizer.
        
        Args:
            entity_types: List of AI entity types to recognize (if None, use all)
            config_path: Path to configuration file
            custom_patterns: Dictionary of custom regex patterns for each entity type
            use_karma: Whether to use the KARMA adapter for entity recognition
            karma_config: Configuration for the KARMA adapter
        """
        self.entity_types = entity_types or AI_ENTITY_TYPES
        self.custom_patterns = custom_patterns or {}
        self.use_karma = use_karma
        
        # Initialize parent class
        super().__init__(self.entity_types, config_path)
        
        # Initialize patterns dictionary with defaults
        self.patterns = {entity_type: [] for entity_type in self.entity_types}
        self._load_patterns()
        
        # Compile regex patterns
        self.compiled_patterns = self._compile_patterns()
        
        # Initialize KARMA adapter if needed
        self.karma_adapter = None
        if self.use_karma:
            try:
                self.karma_adapter = KARMAAdapter(**(karma_config or {}))
            except Exception as e:
                logger.error(f"Failed to initialize KARMA adapter: {e}")
                self.use_karma = False
    
    def _load_patterns(self):
        """Load patterns from configuration and custom patterns."""
        # Load default patterns for the entity types we're interested in
        for entity_type in self.entity_types:
            if entity_type in DEFAULT_PATTERNS:
                self.patterns[entity_type].extend(DEFAULT_PATTERNS[entity_type])
        
        # Load patterns from configuration file
        config_patterns = self.config.get("patterns", {})
        for entity_type, patterns in config_patterns.items():
            if entity_type in self.entity_types:
                self.patterns[entity_type].extend(patterns)
        
        # Add custom patterns
        for entity_type, patterns in self.custom_patterns.items():
            if entity_type in self.entity_types:
                self.patterns[entity_type].extend(patterns)
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficiency."""
        compiled = {}
        for entity_type, patterns in self.patterns.items():
            compiled[entity_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        return compiled
    
    def recognize_entities(self, text: str) -> List[Entity]:
        """
        Recognize AI-specific entities in the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of recognized entities
        """
        entities = []
        
        # Use rule-based approach with regex patterns
        entities.extend(self._recognize_with_patterns(text))
        
        # Use KARMA adapter if available
        if self.use_karma and self.karma_adapter:
            karma_entities = self._recognize_with_karma(text)
            entities.extend(karma_entities)
        
        # Merge overlapping entities
        merged_entities = self.merge_overlapping_entities(entities)
        
        return merged_entities
    
    def _recognize_with_patterns(self, text: str) -> List[Entity]:
        """Recognize entities using regex patterns."""
        entities = []
        entity_id = 0
        
        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    start_pos, end_pos = match.span()
                    entity_text = match.group(0)
                    
                    # Simple confidence calculation based on length of entity
                    # In a real system, this would be more sophisticated
                    confidence = min(0.7 + len(entity_text) / 30, 0.95)
                    
                    entity = Entity(
                        id=f"entity_{entity_id}",
                        text=entity_text,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        metadata={"source": "pattern", "pattern": pattern.pattern}
                    )
                    
                    entities.append(entity)
                    entity_id += 1
        
        return entities
    
    def _recognize_with_karma(self, text: str) -> List[Entity]:
        """Recognize entities using the KARMA adapter."""
        entities = []
        entity_id = 0
        
        try:
            # Extract entities using KARMA
            karma_entities = self.karma_adapter.extract_entities(text)
            
            for karma_entity in karma_entities:
                # Map KARMA entity type to our entity types
                entity_type = self._map_karma_entity_type(karma_entity.get("type", ""))
                
                if entity_type in self.entity_types:
                    entity = Entity(
                        id=f"karma_entity_{entity_id}",
                        text=karma_entity.get("text", ""),
                        type=entity_type,
                        confidence=karma_entity.get("confidence", 0.8),
                        start_pos=karma_entity.get("start_pos", 0),
                        end_pos=karma_entity.get("end_pos", 0),
                        metadata={"source": "karma", "original_type": karma_entity.get("type", "")}
                    )
                    
                    entities.append(entity)
                    entity_id += 1
                    
        except Exception as e:
            logger.error(f"Error recognizing entities with KARMA: {e}")
        
        return entities
    
    def _map_karma_entity_type(self, karma_type: str) -> str:
        """Map KARMA entity type to our entity types."""
        # This is a simple mapping - in a real system this would be more comprehensive
        mapping = {
            "model": "model",
            "algorithm": "algorithm",
            "dataset": "dataset",
            "metric": "metric",
            "framework": "framework",
            "library": "framework",
            "method": "technique",
            "task": "task",
            "benchmark": "benchmark"
        }
        
        return mapping.get(karma_type.lower(), "")
    
    def add_custom_pattern(self, entity_type: str, pattern: str):
        """
        Add a custom regex pattern for an entity type.
        
        Args:
            entity_type: The entity type to add the pattern for
            pattern: The regex pattern to add
        """
        if entity_type not in self.entity_types:
            logger.warning(f"Entity type '{entity_type}' is not recognized")
            return
        
        # Add to patterns dictionary
        if entity_type not in self.patterns:
            self.patterns[entity_type] = []
        self.patterns[entity_type].append(pattern)
        
        # Compile the new pattern
        if entity_type not in self.compiled_patterns:
            self.compiled_patterns[entity_type] = []
        self.compiled_patterns[entity_type].append(re.compile(pattern, re.IGNORECASE))
        
        logger.info(f"Added custom pattern for entity type '{entity_type}': {pattern}")
        
    def analyze_entity_distribution(self, entities: List[Entity]) -> Dict[str, int]:
        """
        Analyze the distribution of entity types in the given list of entities.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            Dictionary mapping entity types to their frequencies
        """
        distribution = {entity_type: 0 for entity_type in self.entity_types}
        
        for entity in entities:
            if entity.type in distribution:
                distribution[entity.type] += 1
        
        return distribution
    
    def extract_top_entities(self, entities: List[Entity], top_n: int = 5) -> Dict[str, List[Tuple[str, float]]]:
        """
        Extract the top N entities of each type based on confidence.
        
        Args:
            entities: List of entities to analyze
            top_n: Number of top entities to extract for each type
            
        Returns:
            Dictionary mapping entity types to lists of (entity_text, confidence) tuples
        """
        # Group entities by type
        entities_by_type = {entity_type: [] for entity_type in self.entity_types}
        
        for entity in entities:
            if entity.type in entities_by_type:
                entities_by_type[entity.type].append((entity.text, entity.confidence))
        
        # Sort each group by confidence and take top N
        top_entities = {}
        for entity_type, entity_list in entities_by_type.items():
            unique_entities = {}
            for text, conf in entity_list:
                if text not in unique_entities or conf > unique_entities[text]:
                    unique_entities[text] = conf
            
            sorted_entities = sorted(unique_entities.items(), key=lambda x: x[1], reverse=True)
            top_entities[entity_type] = sorted_entities[:top_n]
        
        return top_entities