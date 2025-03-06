"""
Concept Definition Builder module for extracting and formalizing AI concept definitions.
"""
from typing import Dict, List, Optional, Set, Any
import re
from pathlib import Path
import json
from collections import defaultdict

class ConceptDefinitionBuilder:
    """
    Extracts, formalizes, and merges concept definitions from research papers.
    
    This class provides functionality to identify AI-related concept definitions
    in research papers, extract their formal definitions, and merge related
    definitions to create comprehensive concept representations.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the ConceptDefinitionBuilder with optional configuration.
        
        Args:
            config_path: Optional path to a configuration file
        """
        # Patterns for identifying concept definitions
        self.definition_patterns = [
            # "We define X as Y"
            r'(?:we|authors)?\s*define\s+([^.,;:]+)\s+as\s+([^.;]+)[.;]',
            # "X is defined as Y"
            r'([^.,;:]+)\s+is\s+defined\s+as\s+([^.;]+)[.;]',
            # "X, which is Y"
            r'([^.,;:]+),\s+which\s+is\s+([^.;]+)[.;]',
            # "X refers to Y"
            r'([^.,;:]+)\s+refers\s+to\s+([^.;]+)[.;]',
            # "X, or Y,"
            r'([^.,;:]+),\s+or\s+([^,.;:]+)[,.]'
        ]
        
        # Concept identifiers for AI research domains
        self.concept_indicators = [
            'model', 'architecture', 'layer', 'algorithm', 'method', 'approach',
            'technique', 'framework', 'system', 'mechanism', 'procedure',
            'process', 'function', 'representation', 'embedding', 'encoding',
            'attention', 'transformer', 'neural', 'network', 'cnn', 'rnn', 'lstm',
            'gan', 'reinforcement', 'supervised', 'unsupervised', 'transfer',
            'learning', 'training', 'inference', 'prediction', 'classification',
            'regression', 'clustering', 'detection', 'generation', 'synthesis'
        ]
        
        # Load custom configuration if provided
        if config_path:
            self._load_config(config_path)
            
        # Track concepts across multiple documents
        self.concept_database = defaultdict(list)
    
    def _load_config(self, config_path: Path) -> None:
        """
        Load custom configuration for concept extraction.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update definition patterns if provided
            if 'definition_patterns' in config:
                self.definition_patterns = config['definition_patterns']
                
            # Update concept indicators if provided
            if 'concept_indicators' in config:
                self.concept_indicators = config['concept_indicators']
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading configuration: {e}")
    
    def extract_definitions(self, text: str, paper_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Extract concept definitions from the text.
        
        Args:
            text: The text to extract definitions from
            paper_id: Optional identifier for the source paper
            
        Returns:
            Dictionary mapping concept names to their definitions and metadata
        """
        # Extract raw definitions using patterns
        raw_definitions = self._extract_raw_definitions(text)
        
        # Filter to keep only AI-related concepts
        ai_definitions = self._filter_ai_concepts(raw_definitions)
        
        # Formalize the definitions
        formalized_definitions = self._formalize_definitions(ai_definitions, text)
        
        # Add metadata
        for concept, definition in formalized_definitions.items():
            definition['source'] = paper_id if paper_id else 'unknown'
            
            # Add to concept database for cross-paper analysis
            self.concept_database[concept].append(definition)
        
        return formalized_definitions
    
    def _extract_raw_definitions(self, text: str) -> Dict[str, List[str]]:
        """
        Extract raw definitions using pattern matching.
        
        Args:
            text: The text to extract definitions from
            
        Returns:
            Dictionary mapping concept names to their raw definitions
        """
        raw_definitions = defaultdict(list)
        
        # Apply each definition pattern
        for pattern in self.definition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                concept = match.group(1).strip().lower()
                definition = match.group(2).strip()
                
                # Skip very short concepts or definitions
                if len(concept) < 2 or len(definition) < 5:
                    continue
                
                # Normalize concept name
                concept = self._normalize_concept_name(concept)
                raw_definitions[concept].append(definition)
        
        return raw_definitions
    
    def _normalize_concept_name(self, concept: str) -> str:
        """
        Normalize concept name by removing articles and standardizing format.
        
        Args:
            concept: The concept name to normalize
            
        Returns:
            Normalized concept name
        """
        # Remove leading articles
        concept = re.sub(r'^(a|an|the)\s+', '', concept.lower())
        
        # Remove trailing punctuation
        concept = re.sub(r'[.,;:!?]$', '', concept)
        
        # Convert to lowercase
        concept = concept.lower()
        
        # Remove phrases like "in this paper" or "in our approach"
        concept = re.sub(r'in\s+(this|our)\s+(paper|work|approach|method|algorithm|study)\s*', '', concept)
        
        return concept.strip()
    
    def _filter_ai_concepts(self, raw_definitions: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Filter definitions to include only AI-related concepts.
        
        Args:
            raw_definitions: Dictionary of raw definitions
            
        Returns:
            Dictionary containing only AI-related concepts
        """
        ai_definitions = {}
        
        for concept, definitions in raw_definitions.items():
            # Check if the concept contains any AI-related indicators
            is_ai_concept = any(indicator in concept for indicator in self.concept_indicators)
            
            # Check if the definitions contain AI-related indicators
            contains_ai_terms = any(
                any(indicator in definition.lower() for indicator in self.concept_indicators)
                for definition in definitions
            )
            
            if is_ai_concept or contains_ai_terms:
                ai_definitions[concept] = definitions
        
        return ai_definitions
    
    def _formalize_definitions(
        self, 
        raw_definitions: Dict[str, List[str]], 
        context: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Formalize raw definitions by adding structure and context.
        
        Args:
            raw_definitions: Dictionary of raw definitions
            context: The full text for extracting additional context
            
        Returns:
            Dictionary of formalized definitions with metadata
        """
        formalized = {}
        
        for concept, definitions in raw_definitions.items():
            # Get the most comprehensive definition (usually the longest)
            primary_definition = max(definitions, key=len)
            
            # Extract related terms
            related_terms = self._extract_related_terms(concept, context)
            
            # Find examples if available
            examples = self._extract_examples(concept, context)
            
            # Create a formalized definition
            formalized[concept] = {
                'concept': concept,
                'primary_definition': primary_definition,
                'alternative_definitions': [d for d in definitions if d != primary_definition],
                'related_terms': related_terms,
                'examples': examples,
                'domain': self._categorize_domain(concept, primary_definition)
            }
        
        return formalized
    
    def _extract_related_terms(self, concept: str, text: str) -> List[str]:
        """
        Extract terms related to the given concept.
        
        Args:
            concept: The concept to find related terms for
            text: The text to search in
            
        Returns:
            List of related terms
        """
        related_terms = []
        
        # Look for "X and Y" patterns
        pattern1 = fr'({re.escape(concept)})\s+and\s+([^.,;:]+)[.,;:]'
        pattern2 = fr'([^.,;:]+)\s+and\s+({re.escape(concept)})[.,;:]'
        
        for pattern in [pattern1, pattern2]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get the other term (not the concept)
                if match.group(1).lower() == concept.lower():
                    related_term = match.group(2).strip()
                else:
                    related_term = match.group(1).strip()
                
                # Normalize and add if not too short
                if len(related_term) > 2:
                    related_term = self._normalize_concept_name(related_term)
                    if related_term != concept and related_term not in related_terms:
                        related_terms.append(related_term)
        
        # Look for "similar to X" patterns
        pattern3 = fr'similar\s+to\s+({re.escape(concept)})'
        pattern4 = fr'({re.escape(concept)})\s+is\s+similar\s+to\s+([^.,;:]+)[.,;:]'
        
        for match in re.finditer(pattern4, text, re.IGNORECASE):
            related_term = match.group(2).strip()
            related_term = self._normalize_concept_name(related_term)
            if related_term != concept and related_term not in related_terms:
                related_terms.append(related_term)
        
        return related_terms[:5]  # Limit to top 5 related terms
    
    def _extract_examples(self, concept: str, text: str) -> List[str]:
        """
        Extract examples of the given concept.
        
        Args:
            concept: The concept to find examples for
            text: The text to search in
            
        Returns:
            List of examples
        """
        examples = []
        
        # Look for "X such as Y" patterns
        pattern1 = fr'{re.escape(concept)}\s+such\s+as\s+([^.;]+)[.;]'
        
        # Look for "examples of X include Y" patterns
        pattern2 = fr'examples\s+of\s+{re.escape(concept)}\s+include\s+([^.;]+)[.;]'
        
        # Look for "X, e.g., Y" patterns
        pattern3 = fr'{re.escape(concept)},\s+e\.g\.,\s+([^.;]+)[.;]'
        
        # Look for "X (e.g., Y)" patterns
        pattern4 = fr'{re.escape(concept)}\s+\(e\.g\.,\s+([^)]+)\)'
        
        patterns = [pattern1, pattern2, pattern3, pattern4]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                example_text = match.group(1).strip()
                
                # Split into multiple examples if separated by commas or "and"
                for example in re.split(r',\s+|\s+and\s+', example_text):
                    if example and example not in examples:
                        examples.append(example.strip())
        
        return examples
    
    def _categorize_domain(self, concept: str, definition: str) -> str:
        """
        Categorize the concept into an AI research domain.
        
        Args:
            concept: The concept name
            definition: The concept definition
            
        Returns:
            Domain category
        """
        combined_text = f"{concept} {definition}".lower()
        
        # Define domain indicators
        domains = {
            'computer_vision': ['image', 'vision', 'object detection', 'segmentation', 'recognition'],
            'nlp': ['language', 'text', 'nlp', 'token', 'word', 'sentence', 'document'],
            'reinforcement_learning': ['reinforcement', 'rl', 'reward', 'policy', 'agent', 'environment'],
            'generative_models': ['generative', 'generation', 'gan', 'vae', 'diffusion'],
            'optimization': ['optimization', 'gradient', 'loss', 'objective function'],
            'neural_architecture': ['architecture', 'network', 'layer', 'activation'],
            'representation_learning': ['representation', 'embedding', 'feature', 'encoding'],
            'training_methods': ['training', 'learning', 'fine-tuning', 'pretraining']
        }
        
        # Find matching domains
        matching_domains = []
        for domain, indicators in domains.items():
            if any(indicator in combined_text for indicator in indicators):
                matching_domains.append(domain)
        
        if not matching_domains:
            return 'general_ai'
        
        # Return the most specific domain (or the first if multiple match)
        return matching_domains[0]
    
    def merge_definitions(self, concept: str) -> Dict[str, Any]:
        """
        Merge multiple definitions of the same concept from different papers.
        
        Args:
            concept: The concept to merge definitions for
            
        Returns:
            Comprehensive merged definition
        """
        if concept not in self.concept_database or not self.concept_database[concept]:
            return {}
        
        # Get all definitions for this concept
        definitions = self.concept_database[concept]
        
        # Start with the most recent or comprehensive definition
        primary_def = max(definitions, key=lambda d: len(d['primary_definition']))
        merged = {
            'concept': concept,
            'primary_definition': primary_def['primary_definition'],
            'alternative_definitions': [],
            'related_terms': set(),
            'examples': set(),
            'sources': set(),
            'domain': primary_def['domain']
        }
        
        # Merge information from all definitions
        for definition in definitions:
            # Add source
            merged['sources'].add(definition['source'])
            
            # Add alternative definitions if not duplicates
            for alt_def in definition['alternative_definitions']:
                if alt_def not in merged['alternative_definitions'] and alt_def != merged['primary_definition']:
                    merged['alternative_definitions'].append(alt_def)
            
            # Merge primary definition if different
            if (definition['primary_definition'] != merged['primary_definition'] and 
                definition['primary_definition'] not in merged['alternative_definitions']):
                merged['alternative_definitions'].append(definition['primary_definition'])
            
            # Add related terms
            merged['related_terms'].update(definition['related_terms'])
            
            # Add examples
            merged['examples'].update(definition['examples'])
        
        # Convert sets to lists
        merged['related_terms'] = list(merged['related_terms'])
        merged['examples'] = list(merged['examples'])
        merged['sources'] = list(merged['sources'])
        
        return merged
    
    def generate_concept_hierarchy(self) -> Dict[str, List[str]]:
        """
        Generate a hierarchical representation of concepts.
        
        Returns:
            Dictionary mapping domains to lists of concepts
        """
        hierarchy = defaultdict(list)
        
        # Group concepts by domain
        for concept in self.concept_database:
            merged = self.merge_definitions(concept)
            if merged:
                domain = merged['domain']
                hierarchy[domain].append(concept)
        
        return dict(hierarchy)
    
    def find_related_concepts(self, concept: str, max_distance: int = 2) -> List[str]:
        """
        Find concepts related to the given concept within a certain distance.
        
        Args:
            concept: The concept to find related concepts for
            max_distance: Maximum relationship distance
            
        Returns:
            List of related concepts
        """
        if concept not in self.concept_database:
            return []
        
        # Track discovered concepts and their distances
        discovered = {concept: 0}
        frontier = [concept]
        related = []
        
        while frontier and max(discovered.values()) < max_distance:
            current = frontier.pop(0)
            current_distance = discovered[current]
            
            # Get directly related concepts
            if current in self.concept_database:
                merged = self.merge_definitions(current)
                direct_relations = merged['related_terms']
                
                for related_concept in direct_relations:
                    if related_concept in self.concept_database and related_concept not in discovered:
                        discovered[related_concept] = current_distance + 1
                        frontier.append(related_concept)
                        related.append(related_concept)
        
        return related
    
    def format_for_knowledge_graph(self, concept: str) -> Dict[str, Any]:
        """
        Format a concept definition for knowledge graph integration.
        
        Args:
            concept: The concept to format
            
        Returns:
            Dictionary formatted for knowledge graph
        """
        if concept not in self.concept_database:
            return {}
        
        merged = self.merge_definitions(concept)
        if not merged:
            return {}
        
        # Format for knowledge graph
        formatted = {
            'type': 'Concept',
            'id': concept.replace(' ', '_'),
            'name': concept,
            'definition': merged['primary_definition'],
            'domain': merged['domain'],
            'alternative_definitions': merged['alternative_definitions'],
            'examples': merged['examples'],
            'sources': merged['sources'],
            'relationships': [
                {'type': 'RELATED_TO', 'target': term.replace(' ', '_')}
                for term in merged['related_terms'] if term in self.concept_database
            ]
        }
        
        return formatted