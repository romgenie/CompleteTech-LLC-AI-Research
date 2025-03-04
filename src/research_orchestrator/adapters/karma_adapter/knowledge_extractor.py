"""
KARMA Knowledge Extractor for AI research.

This module provides the KARMAKnowledgeExtractor class that specializes in
extracting AI research concepts, methodologies, and relationships from text.
"""

import logging
import os
import sys
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Add KARMA path to system path for importing
KARMA_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../../external_repo/KARMA'))
if KARMA_PATH not in sys.path:
    sys.path.append(KARMA_PATH)

class KARMAKnowledgeExtractor:
    """
    Specialized knowledge extractor for AI research using KARMA.
    
    This class provides functionality to extract AI-specific entities,
    relationships, and concepts from research text, specializing in
    machine learning algorithms, models, benchmarks, and methodologies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the KARMA knowledge extractor.
        
        Args:
            config: Configuration dictionary containing extraction settings.
        """
        self.config = config
        self.karma_available = self._check_karma_availability()
        
        # AI-specific entity types to extract
        self.entity_types = [
            'Algorithm', 'Model', 'Dataset', 
            'Metric', 'Task', 'Method',
            'Performance', 'Parameter', 'Feature'
        ]
        
        # AI-specific relationships to extract
        self.relationship_types = [
            'uses', 'improves', 'outperforms',
            'achieves', 'implements', 'extends',
            'applies_to', 'evaluated_on', 'introduces'
        ]
        
        if self.karma_available:
            self._initialize_karma()
        else:
            logger.warning("KARMA framework not available. Using fallback mechanisms.")
            self._initialize_fallback()
    
    def _check_karma_availability(self) -> bool:
        """
        Check if KARMA framework is available for import.
        
        Returns:
            True if KARMA is available, False otherwise.
        """
        try:
            # Try to import a basic KARMA module to check availability
            # This is a placeholder - would need to be adjusted based on actual KARMA structure
            import karma
            return True
        except ImportError:
            return False
    
    def _initialize_karma(self):
        """
        Initialize the KARMA framework components.
        """
        try:
            # Import KARMA components
            # These imports would need to be adjusted based on actual KARMA structure
            from karma import KnowledgeExtractor, EntityRecognizer
            
            # Initialize KARMA components with configuration
            self.knowledge_extractor = KnowledgeExtractor(self.config.get('extractor', {}))
            
            # Configure for AI research
            # This would need to be adjusted based on actual KARMA configuration options
            self.knowledge_extractor.configure(
                entity_types=self.entity_types,
                relationship_types=self.relationship_types,
                domain="ai_research"
            )
            
            logger.info("KARMA knowledge extractor initialized for AI research.")
        except Exception as e:
            logger.error(f"Error initializing KARMA knowledge extractor: {str(e)}")
            self.karma_available = False
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """
        Initialize fallback extraction mechanisms when KARMA is not available.
        """
        try:
            # Initialize NLP libraries for fallback
            import spacy
            
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            # Try to load transformers if available (for more advanced extraction)
            try:
                from transformers import pipeline
                self.ner_pipeline = pipeline("ner")
                self.qa_pipeline = pipeline("question-answering")
                self.has_transformers = True
            except ImportError:
                self.has_transformers = False
                
            logger.info("Fallback extraction mechanisms initialized.")
        except Exception as e:
            logger.error(f"Error initializing fallback extraction: {str(e)}")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract AI research entities from text.
        
        Args:
            text: The text to extract entities from.
            
        Returns:
            A list of entity dictionaries.
        """
        if self.karma_available:
            return self._extract_entities_with_karma(text)
        else:
            return self._extract_entities_fallback(text)
    
    def _extract_entities_with_karma(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities using KARMA.
        
        Args:
            text: The text to extract entities from.
            
        Returns:
            A list of entity dictionaries.
        """
        try:
            # Use KARMA's entity extraction capabilities
            # This call would need to be adjusted based on actual KARMA API
            entities = self.knowledge_extractor.extract_entities(text)
            
            # Format the results
            return self._format_karma_entities(entities)
        except Exception as e:
            logger.error(f"Error extracting entities with KARMA: {str(e)}")
            return self._extract_entities_fallback(text)
    
    def _format_karma_entities(self, karma_entities: List[Any]) -> List[Dict[str, Any]]:
        """
        Format KARMA entities into standardized format.
        
        Args:
            karma_entities: The entities extracted by KARMA.
            
        Returns:
            A list of standardized entity dictionaries.
        """
        # This method would need to be adjusted based on actual KARMA output format
        formatted_entities = []
        
        for entity in karma_entities:
            # This is a placeholder based on assumed KARMA structure
            formatted_entity = {
                "id": entity.id,
                "text": entity.text,
                "type": entity.type,
                "start": entity.start,
                "end": entity.end,
                "confidence": entity.confidence,
                "source": "karma"
            }
            formatted_entities.append(formatted_entity)
        
        return formatted_entities
    
    def _extract_entities_fallback(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback method for entity extraction when KARMA is not available.
        
        Args:
            text: The text to extract entities from.
            
        Returns:
            A list of entity dictionaries.
        """
        entities = []
        
        # Entity extraction using spaCy
        doc = self.nlp(text)
        
        # Extract named entities
        for ent in doc.ents:
            entity = {
                "id": f"ent_{len(entities)}",
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 0.7,  # Placeholder confidence
                "source": "spacy"
            }
            entities.append(entity)
        
        # If transformers is available, use it for more advanced extraction
        if hasattr(self, 'has_transformers') and self.has_transformers:
            try:
                # Extract entities using transformers
                ner_results = self.ner_pipeline(text)
                
                for i, result in enumerate(ner_results):
                    entity = {
                        "id": f"ent_tr_{i}",
                        "text": result["word"],
                        "type": result["entity"],
                        "start": result["start"],
                        "end": result["end"],
                        "confidence": result["score"],
                        "source": "transformers"
                    }
                    entities.append(entity)
            except Exception as e:
                logger.warning(f"Transformers entity extraction failed: {str(e)}")
        
        # Extract AI-specific concepts using pattern matching
        ai_concepts = self._extract_ai_concepts(text)
        entities.extend(ai_concepts)
        
        return entities
    
    def _extract_ai_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract AI-specific concepts using pattern matching.
        
        Args:
            text: The text to extract concepts from.
            
        Returns:
            A list of AI concept entity dictionaries.
        """
        import re
        
        concepts = []
        
        # Define AI-specific patterns
        patterns = {
            'Algorithm': [
                r'(?i)(random forest|decision tree|neural network|deep learning|reinforcement learning|supervised learning|unsupervised learning|semi-supervised learning|k-means|SVM|support vector machine|logistic regression|linear regression|gradient boosting|XGBoost|AdaBoost|k-nearest neighbors|KNN|naive bayes|LSTM|long short-term memory|GRU|gated recurrent unit|CNN|convolutional neural network|RNN|recurrent neural network|transformer|attention mechanism|BERT|GPT|T5|BART|ALBERT|RoBERTa|DeBERTa|MLP|multi-layer perceptron)',
            ],
            'Model': [
                r'(?i)(GPT-\d|BERT|RoBERTa|T5|BART|ALBERT|DeBERTa|XLNet|ELMo|ULMFiT|ELECTRA|DistilBERT|CLIP|DALL-E|Stable Diffusion|DALL-E\s+\d|GPT-Neo|GPT-J|OPT|BLOOM|Llama|Llama\s+\d|LLaMA|PaLM|Gemini|Claude|Mixtral|MoE|mixture of experts)',
            ],
            'Dataset': [
                r'(?i)(ImageNet|COCO|MS-COCO|CIFAR-10|CIFAR-100|MNIST|Fashion-MNIST|SVHN|Pascal VOC|SQuAD|GLUE|SuperGLUE|WikiText|C4|LAMBADA|Penn Treebank|CoNLL|WMT|IWSLT|WebText|CommonCrawl|MMLU|HumanEval|GSM8K|Big Bench|MATH)',
            ],
            'Metric': [
                r'(?i)(accuracy|precision|recall|F1|F1-score|AUC|ROC|ROC-AUC|PR-AUC|MAP|BLEU|ROUGE|METEOR|CIDEr|SPICE|perplexity|cross-entropy|RMSE|MAE|MSE|log loss|Dice coefficient|IoU|PSNR|SSIM)',
            ],
            'Task': [
                r'(?i)(classification|regression|clustering|segmentation|object detection|image classification|sentiment analysis|named entity recognition|machine translation|text generation|text summarization|image generation|image-to-text|text-to-image|image-to-image|text-to-text|question answering|natural language inference|coreference resolution|speech recognition|speech synthesis)',
            ]
        }
        
        concept_id = 0
        
        # Extract matches for each entity type
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    # Create entity
                    entity = {
                        "id": f"ai_concept_{concept_id}",
                        "text": match.group(0),
                        "type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.8,  # Higher confidence for specific patterns
                        "source": "pattern_matching"
                    }
                    
                    concepts.append(entity)
                    concept_id += 1
        
        return concepts
    
    def extract_relationships(self, text: str, entities: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Extract relationships between AI research entities.
        
        Args:
            text: The text to extract relationships from.
            entities: Optional list of pre-extracted entities.
            
        Returns:
            A list of relationship dictionaries.
        """
        if self.karma_available:
            return self._extract_relationships_with_karma(text, entities)
        else:
            return self._extract_relationships_fallback(text, entities)
    
    def _extract_relationships_with_karma(self, text: str, entities: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Extract relationships using KARMA.
        
        Args:
            text: The text to extract relationships from.
            entities: Optional list of pre-extracted entities.
            
        Returns:
            A list of relationship dictionaries.
        """
        try:
            # Use KARMA's relationship extraction capabilities
            # This call would need to be adjusted based on actual KARMA API
            if entities:
                # Convert entities to KARMA format if needed
                karma_entities = self._convert_to_karma_entities(entities)
                relationships = self.knowledge_extractor.extract_relationships(text, entities=karma_entities)
            else:
                relationships = self.knowledge_extractor.extract_relationships(text)
            
            # Format the results
            return self._format_karma_relationships(relationships)
        except Exception as e:
            logger.error(f"Error extracting relationships with KARMA: {str(e)}")
            return self._extract_relationships_fallback(text, entities)
    
    def _convert_to_karma_entities(self, entities: List[Dict[str, Any]]) -> List[Any]:
        """
        Convert standard entity format to KARMA entity format.
        
        Args:
            entities: List of entities in standard format.
            
        Returns:
            List of entities in KARMA format.
        """
        # This method would need to be adjusted based on actual KARMA API
        # This is a placeholder implementation
        class KARMAEntity:
            def __init__(self, entity_dict):
                self.id = entity_dict["id"]
                self.text = entity_dict["text"]
                self.type = entity_dict["type"]
                self.start = entity_dict["start"]
                self.end = entity_dict["end"]
                self.confidence = entity_dict.get("confidence", 1.0)
        
        karma_entities = [KARMAEntity(entity) for entity in entities]
        return karma_entities
    
    def _format_karma_relationships(self, karma_relationships: List[Any]) -> List[Dict[str, Any]]:
        """
        Format KARMA relationships into standardized format.
        
        Args:
            karma_relationships: The relationships extracted by KARMA.
            
        Returns:
            A list of standardized relationship dictionaries.
        """
        # This method would need to be adjusted based on actual KARMA output format
        formatted_relationships = []
        
        for relation in karma_relationships:
            # This is a placeholder based on assumed KARMA structure
            formatted_relation = {
                "id": relation.id,
                "source": relation.source.text,
                "source_id": relation.source.id,
                "source_type": relation.source.type,
                "target": relation.target.text,
                "target_id": relation.target.id,
                "target_type": relation.target.type,
                "relation_type": relation.type,
                "confidence": relation.confidence,
                "provenance": "karma"
            }
            formatted_relationships.append(formatted_relation)
        
        return formatted_relationships
    
    def _extract_relationships_fallback(self, text: str, entities: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Fallback method for relationship extraction when KARMA is not available.
        
        Args:
            text: The text to extract relationships from.
            entities: Optional list of pre-extracted entities.
            
        Returns:
            A list of relationship dictionaries.
        """
        # Extract entities if not provided
        if not entities:
            entities = self.extract_entities(text)
        
        relationships = []
        
        # Create entity lookup by ID and text
        entity_by_id = {entity["id"]: entity for entity in entities}
        entity_by_text = {}
        for entity in entities:
            entity_by_text[entity["text"].lower()] = entity
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        relation_id = 0
        
        # Extract relationships using dependency parsing
        for sent in doc.sents:
            # Find entities in this sentence
            sent_text = sent.text.lower()
            sentence_entities = [
                entity for entity in entities 
                if entity["text"].lower() in sent_text
            ]
            
            if len(sentence_entities) < 2:
                continue  # Need at least two entities to form a relationship
            
            # Look for relationship patterns
            for token in sent:
                # Subject-verb-object pattern
                if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                    subject_text = token.text.lower()
                    verb = token.head.text.lower()
                    
                    # Find direct objects
                    for child in token.head.children:
                        if child.dep_ in ["dobj", "pobj"]:
                            object_text = child.text.lower()
                            
                            # Check if subject and object are in our entities
                            subject_entity = entity_by_text.get(subject_text)
                            object_entity = entity_by_text.get(object_text)
                            
                            if subject_entity and object_entity:
                                # Map verb to relationship type
                                relation_type = self._map_verb_to_relation_type(verb)
                                
                                relation = {
                                    "id": f"relation_{relation_id}",
                                    "source": subject_entity["text"],
                                    "source_id": subject_entity["id"],
                                    "source_type": subject_entity["type"],
                                    "target": object_entity["text"],
                                    "target_id": object_entity["id"],
                                    "target_type": object_entity["type"],
                                    "relation_type": relation_type,
                                    "confidence": 0.7,
                                    "provenance": "spacy_dependency",
                                    "evidence": sent.text
                                }
                                
                                relationships.append(relation)
                                relation_id += 1
        
        # If transformers is available, use QA pipeline for relationship extraction
        if hasattr(self, 'has_transformers') and self.has_transformers:
            # Extract additional relationships using question answering
            ai_relationship_questions = [
                # Performance relationships
                {"question": "What model achieves state-of-the-art performance?", "relation": "achieves"},
                {"question": "Which model outperforms other models?", "relation": "outperforms"},
                {"question": "What performance does the model achieve?", "relation": "achieves"},
                
                # Method relationships
                {"question": "What method does the model use?", "relation": "uses"},
                {"question": "What algorithm is implemented in the model?", "relation": "implements"},
                {"question": "How does the model improve previous work?", "relation": "improves"},
                
                # Data relationships
                {"question": "What dataset is the model evaluated on?", "relation": "evaluated_on"},
                {"question": "What task does the model apply to?", "relation": "applies_to"}
            ]
            
            for qa_item in ai_relationship_questions:
                try:
                    # Get answer using QA pipeline
                    result = self.qa_pipeline(question=qa_item["question"], context=text)
                    
                    if result["score"] > 0.5:  # Only keep high confidence answers
                        answer = result["answer"]
                        
                        # Try to match answer with an entity
                        matching_entity = None
                        for entity in entities:
                            if entity["text"].lower() in answer.lower() or answer.lower() in entity["text"].lower():
                                matching_entity = entity
                                break
                        
                        if matching_entity:
                            # Look for models in the text that might be related to this answer
                            for entity in entities:
                                if entity["type"] == "Model" and entity != matching_entity:
                                    # Create relationship
                                    relation = {
                                        "id": f"relation_{relation_id}",
                                        "source": entity["text"],
                                        "source_id": entity["id"],
                                        "source_type": entity["type"],
                                        "target": matching_entity["text"],
                                        "target_id": matching_entity["id"],
                                        "target_type": matching_entity["type"],
                                        "relation_type": qa_item["relation"],
                                        "confidence": result["score"],
                                        "provenance": "qa_pipeline",
                                        "evidence": text[:200]  # First 200 chars as evidence
                                    }
                                    
                                    relationships.append(relation)
                                    relation_id += 1
                except Exception as e:
                    logger.warning(f"QA-based relationship extraction failed: {str(e)}")
        
        return relationships
    
    def _map_verb_to_relation_type(self, verb: str) -> str:
        """
        Map a verb to a relationship type.
        
        Args:
            verb: The verb to map.
            
        Returns:
            The mapped relationship type.
        """
        verb_mapping = {
            'use': 'uses',
            'uses': 'uses',
            'utilize': 'uses',
            'employ': 'uses',
            'leverage': 'uses',
            
            'improve': 'improves',
            'improves': 'improves',
            'enhance': 'improves',
            'advance': 'improves',
            'upgrade': 'improves',
            
            'outperform': 'outperforms',
            'outperforms': 'outperforms',
            'exceed': 'outperforms',
            'surpass': 'outperforms',
            'beat': 'outperforms',
            
            'achieve': 'achieves',
            'achieves': 'achieves',
            'attain': 'achieves',
            'reach': 'achieves',
            
            'implement': 'implements',
            'implements': 'implements',
            'realize': 'implements',
            'instantiate': 'implements',
            
            'extend': 'extends',
            'extends': 'extends',
            'expand': 'extends',
            'build on': 'extends',
            
            'apply to': 'applies_to',
            'applies to': 'applies_to',
            'work on': 'applies_to',
            'target': 'applies_to',
            
            'evaluate on': 'evaluated_on',
            'evaluated on': 'evaluated_on',
            'test on': 'evaluated_on',
            'benchmark on': 'evaluated_on',
            
            'introduce': 'introduces',
            'introduces': 'introduces',
            'present': 'introduces',
            'propose': 'introduces'
        }
        
        # Normalize the verb to lowercase
        verb_lower = verb.lower()
        
        # Return the mapped relation type or a default
        return verb_mapping.get(verb_lower, 'related_to')
    
    def extract_knowledge_graph(self, text: str) -> Dict[str, Any]:
        """
        Extract a complete knowledge graph from text.
        
        Args:
            text: The text to extract knowledge from.
            
        Returns:
            A dictionary containing entities, relationships, and metadata.
        """
        # Extract entities
        entities = self.extract_entities(text)
        
        # Extract relationships between entities
        relationships = self.extract_relationships(text, entities)
        
        # Create knowledge graph
        knowledge_graph = {
            "entities": entities,
            "relationships": relationships,
            "metadata": {
                "source_text_length": len(text),
                "entity_count": len(entities),
                "relationship_count": len(relationships),
                "extractor": "KARMA" if self.karma_available else "fallback"
            }
        }
        
        return knowledge_graph