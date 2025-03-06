"""
Performance Result Aggregator module for extracting and aggregating performance metrics from research papers.
"""
from typing import Dict, List, Optional, Union, Any
import re
from pathlib import Path
import json

class PerformanceResultAggregator:
    """
    Extracts, normalizes, and aggregates performance metrics from research papers.
    
    This class provides functionality to extract performance metrics from processed
    research paper content, normalize metrics across different papers, and aggregate
    results for comparison and analysis.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the PerformanceResultAggregator with optional configuration.
        
        Args:
            config_path: Optional path to a configuration file for metric extraction
        """
        self.metrics_patterns = {
            'accuracy': r'(?:accuracy|acc)[:\s]+(\d+\.\d+)%?',
            'precision': r'(?:precision|pr)[:\s]+(\d+\.\d+)%?',
            'recall': r'(?:recall|rec)[:\s]+(\d+\.\d+)%?',
            'f1': r'(?:f1(?:-score)?)[:\s]+(\d+\.\d+)%?',
            'bleu': r'(?:bleu(?:-\d)?)[:\s]+(\d+\.\d+)%?',
            'rouge': r'(?:rouge-[12L])[:\s]+(\d+\.\d+)%?',
            'perplexity': r'(?:perplexity|ppl)[:\s]+(\d+\.\d+)',
            'mse': r'(?:mse|mean squared error)[:\s]+(\d+\.\d+)'
        }
        
        # Dataset mappings for normalization
        self.dataset_aliases = {
            'imagenet': ['imagenet', 'ilsvrc'],
            'cifar10': ['cifar-10', 'cifar10'],
            'cifar100': ['cifar-100', 'cifar100'],
            'squad': ['squad', 'stanford question answering dataset'],
            'glue': ['glue', 'general language understanding evaluation'],
            'coco': ['coco', 'common objects in context']
        }
        
        # Load custom configuration if provided
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: Path) -> None:
        """
        Load custom configuration for metric extraction.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update metrics patterns if provided
            if 'metrics_patterns' in config:
                self.metrics_patterns.update(config['metrics_patterns'])
                
            # Update dataset aliases if provided
            if 'dataset_aliases' in config:
                self.dataset_aliases.update(config['dataset_aliases'])
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading configuration: {e}")
    
    def extract_metrics(self, text: str) -> Dict[str, Dict[str, float]]:
        """
        Extract performance metrics from the given text.
        
        Args:
            text: Text containing performance metrics
            
        Returns:
            Dictionary mapping dataset names to metrics and their values
        """
        # Extract tables containing performance information
        table_data = self._extract_tables(text)
        
        # Extract metrics from regular text
        text_metrics = self._extract_text_metrics(text)
        
        # Combine and organize results by dataset
        datasets = self._identify_datasets(text)
        result = {}
        
        # If datasets are identified, organize metrics by dataset
        if datasets:
            for dataset in datasets:
                result[dataset] = {}
                
            # Distribute metrics to appropriate datasets
            self._distribute_metrics_to_datasets(result, text_metrics, table_data)
        else:
            # If no specific datasets identified, use 'unknown' as default
            result['unknown'] = text_metrics
        
        return result
    
    def _extract_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tabular data containing performance metrics.
        
        Args:
            text: Text containing tables with performance information
            
        Returns:
            List of extracted tables with their content
        """
        # Basic pattern for identifying table structures
        # In a real implementation, this would be more sophisticated
        table_pattern = r'(?:Table|TABLE)\s+\d+[\.\:](.*?)(?:\n\n|\Z)'
        tables = []
        
        for table_match in re.finditer(table_pattern, text, re.DOTALL):
            table_content = table_match.group(1).strip()
            if any(metric in table_content.lower() for metric in self.metrics_patterns.keys()):
                # Parse table structure - simplified implementation
                rows = table_content.split('\n')
                header = rows[0] if rows else ""
                columns = [col.strip() for col in header.split('|') if col.strip()]
                
                table_data = {
                    'header': columns,
                    'rows': [],
                    'raw_content': table_content
                }
                
                for row in rows[1:]:
                    if '|' in row:
                        cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                        if cells:
                            table_data['rows'].append(cells)
                
                tables.append(table_data)
        
        return tables
    
    def _extract_text_metrics(self, text: str) -> Dict[str, float]:
        """
        Extract metrics from regular text using pattern matching.
        
        Args:
            text: Text containing performance metrics
            
        Returns:
            Dictionary mapping metric names to their values
        """
        metrics = {}
        
        # Search for each metric pattern
        for metric_name, pattern in self.metrics_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Take the last match if multiple found (often the conclusion has the final result)
                value = float(match.group(1))
                metrics[metric_name] = value
        
        return metrics
    
    def _identify_datasets(self, text: str) -> List[str]:
        """
        Identify datasets mentioned in the text.
        
        Args:
            text: Text to analyze for dataset mentions
            
        Returns:
            List of identified dataset names
        """
        datasets = []
        
        # Look for dataset aliases in the text
        for canonical_name, aliases in self.dataset_aliases.items():
            for alias in aliases:
                if re.search(r'\b' + re.escape(alias) + r'\b', text, re.IGNORECASE):
                    if canonical_name not in datasets:
                        datasets.append(canonical_name)
        
        return datasets
    
    def _distribute_metrics_to_datasets(
        self, 
        result: Dict[str, Dict[str, float]], 
        text_metrics: Dict[str, float],
        table_data: List[Dict[str, Any]]
    ) -> None:
        """
        Distribute extracted metrics to appropriate datasets.
        
        Args:
            result: Result dictionary to be populated
            text_metrics: Metrics extracted from text
            table_data: Table data extracted from the text
        """
        datasets = list(result.keys())
        
        # Handle case with single dataset - assign all metrics to it
        if len(datasets) == 1:
            result[datasets[0]] = text_metrics
            return
        
        # Look for dataset-metric associations in text
        text_lower = text.lower()
        for dataset in datasets:
            result[dataset] = {}
            aliases = self.dataset_aliases.get(dataset, [dataset])
            
            # Find metrics associated with this dataset
            for metric, value in text_metrics.items():
                for alias in aliases:
                    # Check if metric is mentioned near dataset name
                    if re.search(
                        r'\b' + re.escape(alias) + r'.{0,50}' + re.escape(metric) + r'\b',
                        text_lower
                    ):
                        result[dataset][metric] = value
                        break
        
        # Process table data for dataset-metric associations
        for table in table_data:
            self._process_table_for_datasets(result, table)
    
    def _process_table_for_datasets(self, result: Dict[str, Dict[str, float]], table: Dict[str, Any]) -> None:
        """
        Process table data to extract dataset-specific metrics.
        
        Args:
            result: Result dictionary to be populated
            table: Table data containing metrics
        """
        # Look for dataset names in table header or first column
        header = ' '.join(table['header']).lower()
        
        for dataset in result.keys():
            aliases = self.dataset_aliases.get(dataset, [dataset])
            
            # Check if dataset is in header
            dataset_in_header = any(alias.lower() in header for alias in aliases)
            
            if dataset_in_header:
                # Extract metrics from columns that match metric patterns
                for col_idx, col_name in enumerate(table['header']):
                    for metric, pattern in self.metrics_patterns.items():
                        if re.search(pattern, col_name, re.IGNORECASE):
                            # Extract values from this column
                            for row in table['rows']:
                                if col_idx < len(row):
                                    try:
                                        value = float(re.sub(r'[^\d.]', '', row[col_idx]))
                                        result[dataset][metric] = value
                                    except ValueError:
                                        pass
            else:
                # Check for dataset names in rows
                for row in table['rows']:
                    row_text = ' '.join(row).lower()
                    dataset_in_row = any(alias.lower() in row_text for alias in aliases)
                    
                    if dataset_in_row:
                        # Extract metrics from this row
                        for col_idx, col_name in enumerate(table['header']):
                            for metric, pattern in self.metrics_patterns.items():
                                if re.search(pattern, col_name, re.IGNORECASE):
                                    if col_idx < len(row):
                                        try:
                                            value = float(re.sub(r'[^\d.]', '', row[col_idx]))
                                            result[dataset][metric] = value
                                        except ValueError:
                                            pass
    
    def normalize_metrics(self, metrics: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """
        Normalize metrics to allow fair comparison (e.g., convert all to percentage).
        
        Args:
            metrics: Dictionary of metrics by dataset
            
        Returns:
            Dictionary of normalized metrics
        """
        normalized = {}
        
        for dataset, dataset_metrics in metrics.items():
            normalized[dataset] = {}
            
            for metric, value in dataset_metrics.items():
                # Handle common normalization cases
                if metric in ['accuracy', 'precision', 'recall', 'f1', 'bleu', 'rouge']:
                    # Ensure values are in percentage (0-100)
                    if 0 <= value <= 1:
                        normalized[dataset][metric] = value * 100
                    else:
                        normalized[dataset][metric] = value
                elif metric == 'perplexity':
                    # Lower is better for perplexity
                    normalized[dataset][metric] = value
                else:
                    # Default case - no normalization
                    normalized[dataset][metric] = value
        
        return normalized
    
    def aggregate_results(
        self, 
        metrics_list: List[Dict[str, Dict[str, float]]], 
        method: str = 'latest'
    ) -> Dict[str, Dict[str, float]]:
        """
        Aggregate metrics from multiple sources.
        
        Args:
            metrics_list: List of metrics dictionaries from different papers
            method: Aggregation method ('latest', 'max', 'min', 'avg')
            
        Returns:
            Aggregated metrics dictionary
        """
        if not metrics_list:
            return {}
        
        aggregated = {}
        
        # Collect all datasets and metrics
        all_datasets = set()
        for metrics in metrics_list:
            all_datasets.update(metrics.keys())
        
        for dataset in all_datasets:
            aggregated[dataset] = {}
            
            # Collect values for each metric across all papers
            metric_values = {}
            for metrics in metrics_list:
                if dataset in metrics:
                    for metric, value in metrics[dataset].items():
                        if metric not in metric_values:
                            metric_values[metric] = []
                        metric_values[metric].append(value)
            
            # Apply aggregation method
            for metric, values in metric_values.items():
                if method == 'latest':
                    aggregated[dataset][metric] = values[-1]
                elif method == 'max':
                    aggregated[dataset][metric] = max(values)
                elif method == 'min':
                    aggregated[dataset][metric] = min(values)
                elif method == 'avg':
                    aggregated[dataset][metric] = sum(values) / len(values)
        
        return aggregated
    
    def format_for_knowledge_graph(
        self, 
        metrics: Dict[str, Dict[str, float]], 
        paper_id: str, 
        model_name: str
    ) -> List[Dict[str, Any]]:
        """
        Format performance metrics for knowledge graph integration.
        
        Args:
            metrics: Dictionary of metrics by dataset
            paper_id: ID of the paper these metrics are from
            model_name: Name of the model these metrics are for
            
        Returns:
            List of structured performance records for knowledge graph
        """
        records = []
        
        for dataset, dataset_metrics in metrics.items():
            for metric, value in dataset_metrics.items():
                record = {
                    'model': model_name,
                    'paper': paper_id,
                    'dataset': dataset,
                    'metric': metric,
                    'value': value
                }
                records.append(record)
        
        return records