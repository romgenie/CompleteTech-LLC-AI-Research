"""
AI Entity Recognizer for the Research Orchestration Framework.

This module provides a specialized entity recognizer for identifying AI-specific
entities in research documents, such as models, algorithms, datasets, and metrics.
"""

import re
from typing import List, Dict, Any, Set, Pattern, Optional, Tuple
import logging
import os
import json

from .base_recognizer import EntityRecognizer
from .entity import Entity, EntityType

logger = logging.getLogger(__name__)


class AIEntityRecognizer(EntityRecognizer):
    """Entity recognizer specialized for AI research concepts.
    
    This recognizer identifies AI-specific entities like models (e.g., "BERT", 
    "GPT-4"), algorithms, datasets (e.g., "ImageNet", "MNIST"), metrics, and more.
    """
    
    # Default patterns for common AI entity types
    DEFAULT_PATTERNS = {
        EntityType.MODEL: [
            # Language models
            r"\b(GPT-[0-9.]+|GPT[0-9.]+|ChatGPT|InstructGPT|LLaMA[0-9]*|PaLM[0-9]*|Gemini\s*(Pro|Ultra)?|Claude[0-9]*(\s+Opus)?|BERT|RoBERTa|DistilBERT|T5|Flan-T5|UL2|Alpaca|Vicuna)\b",
            # Vision models
            r"\b(ResNet-?[0-9]+|VGG-?[0-9]+|EfficientNet-?[A-Z][0-9]*|ViT|CLIP|DALL-E[0-9]*|Stable\s*Diffusion|Midjourney|Imagen)\b",
            # General pattern for capitalized models with version numbers
            r"\b([A-Z][a-zA-Z]*-?[0-9]*(\.[0-9]+)?)\b"
        ],
        EntityType.DATASET: [
            r"\b(ImageNet|MNIST|CIFAR-?10|CIFAR-?100|MS\s*COCO|SQuAD|WikiText-?[0-9]*|GLUE|SuperGLUE|MMLU|HumanEval|GSM8K)\b"
        ],
        EntityType.METRIC: [
            r"\b(accuracy|precision|recall|F1(-score)?|IoU|mAP|BLEU|ROUGE-[LN]?|METEOR|CIDEr|WER|perplexity|cross-entropy)\b"
        ],
        EntityType.ARCHITECTURE: [
            r"\b(Transformer|LSTM|GRU|CNN|RNN|GAN|VAE|Diffusion\s*Model|MLP|Attention\s*Mechanism|Graph\s*Neural\s*Network|GNN)\b"
        ],
        EntityType.FRAMEWORK: [
            r"\b(TensorFlow|PyTorch|Keras|JAX|Scikit-learn|Hugging\s*Face|OpenAI\s*Gym|Ray|MXNet|Caffe|Theano)\b"
        ],
        EntityType.TASK: [
            r"\b(classification|regression|segmentation|object\s*detection|NER|named\s*entity\s*recognition|machine\s*translation|summarization|question\s*answering|text\s*generation|image\s*generation|sentiment\s*analysis)\b"
        ]
    }
    
    # Common AI models with their architecture types
    KNOWN_MODELS = {
        "GPT": "Transformer",
        "BERT": "Transformer",
        "RoBERTa": "Transformer",
        "T5": "Transformer",
        "LLaMA": "Transformer",
        "ResNet": "CNN",
        "LSTM": "RNN",
        "ViT": "Transformer"
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI Entity Recognizer.
        
        Args:
            config: Configuration dictionary that can include custom patterns,
                   confidence thresholds, and other recognition parameters
        """
        # Initialize instance variables before calling super().__init__
        # Compiled regex patterns for each entity type
        self.patterns: Dict[EntityType, List[Pattern]] = {}
        # Dictionary of known entities with their types
        self.known_entities: Dict[str, Tuple[EntityType, float]] = {}
        
        # Now call the parent constructor which will call _initialize_from_config
        super().__init__(config)
    
    def _initialize_from_config(self) -> None:
        """Initialize recognizer patterns and dictionaries from configuration."""
        # Load custom patterns from config
        custom_patterns = self.config.get("patterns", {})
        
        # Compile the default and custom patterns
        for entity_type in EntityType:
            if entity_type in self.DEFAULT_PATTERNS or str(entity_type) in custom_patterns:
                type_str = str(entity_type)
                # Combine default and custom patterns
                patterns = self.DEFAULT_PATTERNS.get(entity_type, []) + custom_patterns.get(type_str, [])
                self.patterns[entity_type] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        # Load known entities from a dictionary file if specified
        dict_path = self.config.get("dictionary_path")
        if dict_path and os.path.exists(dict_path):
            self._load_entity_dictionary(dict_path)
    
    def _load_entity_dictionary(self, filepath: str) -> None:
        """Load a dictionary of known entities from a JSON file.
        
        The dictionary file should have the format:
        {
            "entity_text": {"type": "entity_type", "confidence": 0.9},
            ...
        }
        
        Args:
            filepath: Path to the entity dictionary JSON file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                entity_dict = json.load(f)
            
            for entity_text, info in entity_dict.items():
                entity_type = EntityType.from_string(info["type"])
                confidence = info.get("confidence", 1.0)
                self.known_entities[entity_text.lower()] = (entity_type, confidence)
            
            logger.info(f"Loaded {len(self.known_entities)} known entities from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load entity dictionary from {filepath}: {e}")
    
    def recognize(self, text: str) -> List[Entity]:
        """Recognize AI entities in the provided text.
        
        Args:
            text: The text to analyze for AI entities
            
        Returns:
            A list of recognized AI entities
        """
        all_entities = []
        
        # Pattern-based recognition
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entity_text = match.group(0)
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Compute confidence based on heuristics
                    confidence = self._compute_confidence(entity_text, entity_type, start_pos, end_pos, text)
                    
                    # Create and add the entity
                    entity = Entity(
                        text=entity_text,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos
                    )
                    all_entities.append(entity)
        
        # Dictionary-based recognition
        for i, word in enumerate(text.split()):
            # Clean up the word for matching
            clean_word = word.lower().strip('.,;:()[]{}"\'-')
            if clean_word in self.known_entities:
                entity_type, confidence = self.known_entities[clean_word]
                
                # Find the position in the original text
                start_pos = text.lower().find(clean_word)
                if start_pos >= 0:
                    end_pos = start_pos + len(clean_word)
                    
                    entity = Entity(
                        text=word,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos
                    )
                    all_entities.append(entity)
        
        # Apply additional recognition logic for AI-specific contexts
        self._recognize_model_related_entities(text, all_entities)
        
        # Resolve overlapping entities
        all_entities = self.merge_overlapping_entities(all_entities)
        
        # Save the entities for later use
        self.entities = all_entities
        
        return all_entities
    
    def _compute_confidence(
        self, 
        entity_text: str, 
        entity_type: EntityType, 
        start_pos: int, 
        end_pos: int,
        context: str
    ) -> float:
        """Compute confidence score for an entity based on heuristics.
        
        Args:
            entity_text: The text of the entity
            entity_type: The type of the entity
            start_pos: Start position in the original text
            end_pos: End position in the original text
            context: The surrounding text context
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.7  # Base confidence
        
        # Adjust confidence based on capitalization for models and frameworks
        if entity_type in [EntityType.MODEL, EntityType.FRAMEWORK]:
            if entity_text[0].isupper():
                confidence += 0.1
        
        # Adjust confidence based on context
        context_window = context[max(0, start_pos-50):min(len(context), end_pos+50)]
        
        # Positive context indicators
        positive_indicators = {
            EntityType.MODEL: ["model", "architecture", "trained", "fine-tuned", "pretrained"],
            EntityType.DATASET: ["dataset", "data", "trained on", "evaluated on", "test set"],
            EntityType.METRIC: ["score", "performance", "measured", "evaluated", "accuracy of", "achieved"],
            EntityType.TASK: ["task of", "problem of", "approach to", "method for"]
        }
        
        # Check for positive indicators in context
        if entity_type in positive_indicators:
            for indicator in positive_indicators[entity_type]:
                if indicator in context_window.lower():
                    confidence += 0.1
                    break
        
        # Adjust confidence based on entity length
        if len(entity_text) < 3:
            confidence -= 0.2
        elif len(entity_text) > 20:
            confidence -= 0.1
        
        # Ensure confidence is within valid range
        return max(0.0, min(1.0, confidence))
    
    def _recognize_model_related_entities(self, text: str, entities: List[Entity]) -> None:
        """Recognize additional entities related to models in the text.
        
        For example, if a model is mentioned along with its performance
        on a dataset, try to extract the dataset and metric entities.
        
        Args:
            text: The input text
            entities: List of already recognized entities (will be modified)
        """
        # Find model entities
        model_entities = [e for e in entities if e.type == EntityType.MODEL]
        
        for model in model_entities:
            # Check for architecture information
            for model_name, architecture in self.KNOWN_MODELS.items():
                if model_name in model.text:
                    # Add architecture entity
                    arch_entity = Entity(
                        text=architecture,
                        type=EntityType.ARCHITECTURE,
                        confidence=0.8,
                        metadata={"related_model": model.text}
                    )
                    entities.append(arch_entity)
            
            # Look for performance information near model mentions
            context_window = text[max(0, model.start_pos-100):min(len(text), model.end_pos+100)]
            
            # Find performance on datasets pattern
            dataset_pattern = re.compile(r"(?:on|using|with) (?:the )?([A-Z][A-Za-z0-9\-]+) (?:dataset|data|benchmark)", re.IGNORECASE)
            for match in dataset_pattern.finditer(context_window):
                dataset_name = match.group(1)
                
                # Create dataset entity
                dataset_entity = Entity(
                    text=dataset_name,
                    type=EntityType.DATASET,
                    confidence=0.75,
                    metadata={"related_model": model.text}
                )
                entities.append(dataset_entity)
            
            # Find metrics pattern
            metric_pattern = re.compile(r"(?:achieved|reached|obtained|had) (?:a |an )?([0-9.]+)(?:%| percent)? ([a-zA-Z0-9\-]+)", re.IGNORECASE)
            for match in metric_pattern.finditer(context_window):
                value = match.group(1)
                metric_name = match.group(2)
                
                # Create metric entity
                metric_entity = Entity(
                    text=metric_name,
                    type=EntityType.METRIC,
                    confidence=0.75,
                    metadata={
                        "related_model": model.text,
                        "value": value
                    }
                )
                entities.append(metric_entity)