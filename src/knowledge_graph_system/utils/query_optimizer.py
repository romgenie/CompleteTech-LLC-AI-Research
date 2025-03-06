"""
Neo4j Query Optimizer

This module provides utilities for optimizing Neo4j queries used in the 
Knowledge Graph System. It includes functions to:

1. Profile existing queries and identify performance bottlenecks
2. Add appropriate indexes to improve query performance
3. Rewrite queries for better performance
4. Cache frequently used query results
"""

import re
import time
import logging
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass

from ..core.neo4j_manager import Neo4jManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryProfile:
    """Profile information about a Neo4j query."""
    query: str
    parameters: Dict[str, Any]
    execution_time_ms: float
    db_hits: int
    rows_returned: int
    cached: bool
    plan: Dict[str, Any]
    problematic_operations: List[str]
    missing_indexes: List[str]

class QueryOptimizer:
    """Utility for optimizing Neo4j queries and database configuration."""
    
    def __init__(self, neo4j_manager: Neo4jManager):
        """Initialize with a Neo4j connection."""
        self.neo4j = neo4j_manager
        self.query_cache = {}
        self.query_stats = {}
    
    def profile_query(self, query: str, parameters: Dict[str, Any] = None) -> QueryProfile:
        """
        Profile a Cypher query to analyze its performance characteristics.
        
        Args:
            query: The Cypher query to profile
            parameters: Parameters for the query
            
        Returns:
            QueryProfile object with performance metrics
        """
        if parameters is None:
            parameters = {}
        
        # Add PROFILE keyword if not present
        if not query.strip().upper().startswith("PROFILE "):
            profile_query = f"PROFILE {query}"
        else:
            profile_query = query
        
        start_time = time.time()
        result = self.neo4j.run_query(profile_query, **parameters)
        end_time = time.time()
        
        execution_time_ms = (end_time - start_time) * 1000
        
        # Extract profile information
        profile_info = result.summary().profile
        db_hits = profile_info.db_hits
        rows = profile_info.rows
        
        # Extract plan information
        plan = self._extract_plan_info(profile_info)
        
        # Analyze for problems
        problematic_ops = self._identify_problematic_operations(plan)
        missing_indexes = self._identify_missing_indexes(plan, query)
        
        # Check if result was cached by Neo4j
        cached = hasattr(result.summary(), 'result_available_after') and result.summary().result_available_after < 1
        
        # Update query statistics
        query_key = self._normalize_query(query)
        if query_key not in self.query_stats:
            self.query_stats[query_key] = {
                'count': 0,
                'total_time_ms': 0,
                'avg_time_ms': 0,
                'max_time_ms': 0,
                'min_time_ms': float('inf'),
                'last_parameters': None
            }
        
        stats = self.query_stats[query_key]
        stats['count'] += 1
        stats['total_time_ms'] += execution_time_ms
        stats['avg_time_ms'] = stats['total_time_ms'] / stats['count']
        stats['max_time_ms'] = max(stats['max_time_ms'], execution_time_ms)
        stats['min_time_ms'] = min(stats['min_time_ms'], execution_time_ms)
        stats['last_parameters'] = parameters
        
        return QueryProfile(
            query=query,
            parameters=parameters,
            execution_time_ms=execution_time_ms,
            db_hits=db_hits,
            rows_returned=rows,
            cached=cached,
            plan=plan,
            problematic_operations=problematic_ops,
            missing_indexes=missing_indexes
        )
    
    def _extract_plan_info(self, profile_info) -> Dict[str, Any]:
        """Extract plan information from Neo4j profile result."""
        # This is a simplified implementation - full implementation would
        # recursively process the plan tree
        plan = {
            'operator': profile_info.operator_type,
            'db_hits': profile_info.db_hits,
            'rows': profile_info.rows,
            'identifiers': profile_info.identifiers
        }
        
        # Add children if present
        if hasattr(profile_info, 'children') and profile_info.children:
            plan['children'] = [
                self._extract_plan_info(child) for child in profile_info.children
            ]
        
        return plan
    
    def _identify_problematic_operations(self, plan: Dict[str, Any]) -> List[str]:
        """Identify problematic operations in a query execution plan."""
        problematic = []
        
        # Check this operation
        operator = plan.get('operator', '')
        db_hits = plan.get('db_hits', 0)
        rows = plan.get('rows', 0)
        
        # High DB hits relative to rows is problematic (expensive filtering)
        if rows > 0 and db_hits / rows > 100:
            problematic.append(f"High DB hits per row in {operator}: {db_hits} hits for {rows} rows")
        
        # Cartesian product is often problematic
        if 'CartesianProduct' in operator:
            problematic.append(f"Cartesian product detected in {operator}")
        
        # NodeByLabelScan without filtering can be expensive
        if 'NodeByLabelScan' in operator and db_hits > 10000:
            problematic.append(f"Large NodeByLabelScan in {operator}: {db_hits} DB hits")
        
        # AllNodesScan is very expensive
        if 'AllNodesScan' in operator:
            problematic.append(f"AllNodesScan detected: consider adding labels and predicates")
        
        # Recursive check for children
        if 'children' in plan:
            for child in plan['children']:
                problematic.extend(self._identify_problematic_operations(child))
        
        return problematic
    
    def _identify_missing_indexes(self, plan: Dict[str, Any], query: str) -> List[str]:
        """Identify potential missing indexes based on query and plan."""
        missing_indexes = []
        
        # Extract node labels and properties used in query
        node_patterns = self._extract_node_patterns(query)
        
        # Check if plan has operations that would benefit from an index
        if self._has_label_scan_without_index(plan):
            for label, props in node_patterns.items():
                for prop in props:
                    missing_indexes.append(f"Consider index on :{label}({prop})")
        
        return missing_indexes
    
    def _has_label_scan_without_index(self, plan: Dict[str, Any]) -> bool:
        """Check if plan contains a label scan without using an index."""
        operator = plan.get('operator', '')
        
        if 'NodeByLabelScan' in operator:
            return True
        
        # Check children recursively
        if 'children' in plan:
            for child in plan['children']:
                if self._has_label_scan_without_index(child):
                    return True
        
        return False
    
    def _extract_node_patterns(self, query: str) -> Dict[str, List[str]]:
        """Extract node labels and properties from a Cypher query."""
        # This is a simplified implementation using regex
        # A full parser would be more accurate but more complex
        result = {}
        
        # Match patterns like (n:Label) or (n:Label {prop: value})
        node_pattern = r'\([\w\d]*:(\w+)(?:\s*\{([^}]+)\})?\)'
        for match in re.finditer(node_pattern, query):
            label = match.group(1)
            if label not in result:
                result[label] = []
            
            # Extract properties if present
            if match.group(2):
                props = match.group(2)
                prop_pattern = r'(\w+)\s*:'
                for prop_match in re.finditer(prop_pattern, props):
                    prop_name = prop_match.group(1)
                    if prop_name not in result[label]:
                        result[label].append(prop_name)
        
        return result
    
    def _normalize_query(self, query: str) -> str:
        """Normalize a query by removing parameter values for caching."""
        # Remove literals
        q = re.sub(r'"[^"]*"', '""', query)  # Replace string literals
        q = re.sub(r"'[^']*'", "''", q)      # Replace string literals (single quotes)
        q = re.sub(r"\b\d+\b", "0", q)       # Replace numbers
        
        # Remove extra whitespace
        q = re.sub(r'\s+', ' ', q).strip()
        
        return q
    
    def get_index_recommendations(self) -> List[str]:
        """
        Analyze query statistics and provide index recommendations.
        
        Returns:
            List of recommended indexes to create
        """
        recommendations = []
        
        # Find frequent and slow queries
        slow_queries = [
            (query, stats) for query, stats in self.query_stats.items()
            if stats['avg_time_ms'] > 100 and stats['count'] > 5
        ]
        
        # For each slow query, profile it and check for missing indexes
        for query, stats in slow_queries:
            # Use the last parameters used with this query
            profile = self.profile_query(query, stats['last_parameters'])
            recommendations.extend(profile.missing_indexes)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def create_recommended_indexes(self, confirm: bool = True) -> int:
        """
        Create all recommended indexes.
        
        Args:
            confirm: If True, require confirmation before creating each index
            
        Returns:
            Number of indexes created
        """
        recommendations = self.get_index_recommendations()
        created = 0
        
        for rec in recommendations:
            # Parse the recommendation
            match = re.match(r'Consider index on :(\w+)\((\w+)\)', rec)
            if not match:
                continue
                
            label = match.group(1)
            property = match.group(2)
            
            # Check if this index already exists
            exists = self._index_exists(label, property)
            if exists:
                logger.info(f"Index already exists for :{label}({property})")
                continue
            
            # Confirm creation if required
            if confirm:
                user_input = input(f"Create index on :{label}({property})? (y/n): ")
                if user_input.lower() != 'y':
                    logger.info(f"Skipping index creation for :{label}({property})")
                    continue
            
            # Create the index
            self.create_index(label, property)
            created += 1
            logger.info(f"Created index on :{label}({property})")
        
        return created
    
    def _index_exists(self, label: str, property: str) -> bool:
        """Check if an index exists for a label and property."""
        query = """
        SHOW INDEXES 
        WHERE type = 'RANGE' 
        AND labelsOrTypes = [$label] 
        AND properties = [$property]
        """
        result = self.neo4j.run_query(query, label=label, property=property)
        return len(result.data()) > 0
    
    def create_index(self, label: str, property: str) -> None:
        """Create an index on a label and property."""
        # Ensure names are properly escaped
        query = f"CREATE INDEX ON :{label}({property})"
        self.neo4j.run_query(query)
    
    def optimize_query(self, query: str, parameters: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Optimize a Cypher query for better performance.
        
        Args:
            query: The original Cypher query
            parameters: Query parameters
            
        Returns:
            Tuple of (optimized_query, parameters)
        """
        if parameters is None:
            parameters = {}
        
        # First, profile the query to understand its performance
        profile = self.profile_query(query, parameters)
        
        # Only optimize if the query is slow enough to warrant it
        if profile.execution_time_ms < 50:
            return query, parameters
        
        optimized_query = query
        optimized_params = parameters.copy()
        
        # Apply various optimization strategies
        optimized_query = self._optimize_match_clauses(optimized_query)
        optimized_query = self._optimize_where_clauses(optimized_query)
        optimized_query = self._add_query_hints(optimized_query, profile)
        
        return optimized_query, optimized_params
    
    def _optimize_match_clauses(self, query: str) -> str:
        """Optimize MATCH clauses in a query."""
        # Reorder MATCH clauses for better performance
        # Start with more specific matches (fewer nodes)
        
        # This is a very simplified implementation
        # A full implementation would parse the query and analyze cardinality
        
        # Extract MATCH clauses
        match_pattern = r'(MATCH\s+[^;]+?(?=MATCH|WHERE|RETURN|WITH|ORDER|SKIP|LIMIT|$))'
        matches = re.findall(match_pattern, query, re.IGNORECASE | re.DOTALL)
        
        if len(matches) <= 1:
            return query  # No multiple MATCH clauses to reorder
        
        # Score each MATCH clause for specificity
        # Higher score = more specific = should come earlier
        scored_matches = []
        for match in matches:
            score = 0
            # More relationships = more specific
            score += match.count('->')
            score += match.count('<-')
            score += match.count('--')
            
            # More property conditions = more specific
            score += match.count('{')
            
            # More WHERE conditions = more specific
            score += 2 * match.count('WHERE')
            
            scored_matches.append((score, match))
        
        # Sort by score descending
        scored_matches.sort(reverse=True)
        
        # Replace in the original query
        optimized = query
        for original_match in matches:
            optimized = optimized.replace(original_match, '')
        
        # Add the reordered matches at the beginning
        reordered_matches = ' '.join([m[1] for m in scored_matches])
        optimized = reordered_matches + ' ' + optimized
        
        # Clean up whitespace
        optimized = re.sub(r'\s+', ' ', optimized).strip()
        
        return optimized
    
    def _optimize_where_clauses(self, query: str) -> str:
        """Optimize WHERE clauses in a query."""
        # Promote equality conditions for indexed properties
        # This simple implementation assumes we know what's indexed
        
        # Indexed properties (in a real implementation, these would be dynamically queried)
        indexed_props = {
            'Paper': ['title', 'doi'],
            'AIModel': ['name'],
            'Dataset': ['name'],
            'Author': ['name']
        }
        
        # Find WHERE clauses
        where_pattern = r'(WHERE\s+[^;]+?(?=RETURN|WITH|ORDER|SKIP|LIMIT|$))'
        where_clauses = re.findall(where_pattern, query, re.IGNORECASE | re.DOTALL)
        
        if not where_clauses:
            return query
        
        for where_clause in where_clauses:
            optimized_clause = where_clause
            
            # Extract conditions
            conditions = re.findall(r'([\w.]+)\s*(=|<>|<|>|<=|>=)\s*([^AND|OR]+)', where_clause)
            
            # Prioritize indexed equality conditions
            if conditions:
                indexed_conditions = []
                other_conditions = []
                
                for prop, op, value in conditions:
                    # Check if this is an indexed property
                    is_indexed = False
                    for label, props in indexed_props.items():
                        for indexed_prop in props:
                            if prop.endswith(f'.{indexed_prop}'):
                                is_indexed = True
                                break
                    
                    # Prioritize indexed equality conditions
                    if is_indexed and op == '=':
                        indexed_conditions.append(f"{prop} {op} {value}")
                    else:
                        other_conditions.append(f"{prop} {op} {value}")
                
                # Reconstruct the WHERE clause with indexed conditions first
                if indexed_conditions and other_conditions:
                    new_conditions = ' AND '.join(indexed_conditions + other_conditions)
                    new_where = f"WHERE {new_conditions}"
                    query = query.replace(where_clause, new_where)
        
        return query
    
    def _add_query_hints(self, query: str, profile: QueryProfile) -> str:
        """Add USING hints to the query based on profile information."""
        # This is a simplified implementation
        hints_to_add = []
        
        # Identify potential indexes to use
        for missing_index in profile.missing_indexes:
            match = re.match(r'Consider index on :(\w+)\((\w+)\)', missing_index)
            if match:
                label = match.group(1)
                property = match.group(2)
                
                # Check if the index exists
                if self._index_exists(label, property):
                    # Determine the variable name used for this label in the query
                    var_pattern = rf'\((\w+):{label}[^\)]*\)'
                    var_match = re.search(var_pattern, query)
                    if var_match:
                        var_name = var_match.group(1)
                        hints_to_add.append(f"USING INDEX {var_name}:{label}({property})")
        
        if not hints_to_add:
            return query
        
        # Insert hints after the first MATCH
        match_pos = query.upper().find("MATCH")
        if match_pos >= 0:
            match_end = query.find('\n', match_pos)
            if match_end < 0:
                match_end = len(query)
            
            # Insert hints
            hints_text = ' ' + ' '.join(hints_to_add)
            optimized = query[:match_end] + hints_text + query[match_end:]
            return optimized
        
        return query
    
    def enable_query_caching(self, max_size: int = 100) -> None:
        """
        Enable caching for frequently executed queries.
        
        Args:
            max_size: Maximum number of query results to cache
        """
        self.max_cache_size = max_size
        self.caching_enabled = True
    
    def disable_query_caching(self) -> None:
        """Disable query caching."""
        self.caching_enabled = False
    
    def clear_query_cache(self) -> None:
        """Clear the query cache."""
        self.query_cache = {}
    
    def execute_with_cache(self, query: str, parameters: Dict[str, Any] = None, ttl: int = 300) -> Any:
        """
        Execute a query with caching if enabled.
        
        Args:
            query: The Cypher query to execute
            parameters: Query parameters
            ttl: Time-to-live for cache entry in seconds (default 5 minutes)
            
        Returns:
            Query results
        """
        if not self.caching_enabled:
            return self.neo4j.run_query(query, **(parameters or {}))
        
        # Normalize the query for cache lookup
        cache_key = self._get_cache_key(query, parameters)
        
        # Check if we have a cached result
        now = time.time()
        if cache_key in self.query_cache:
            cache_entry = self.query_cache[cache_key]
            if now - cache_entry['timestamp'] < ttl:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cache_entry['result']
        
        # Execute the query
        result = self.neo4j.run_query(query, **(parameters or {}))
        
        # Cache the result if it's not too large
        try:
            result_data = result.data()
            if len(result_data) < 1000:  # Don't cache very large results
                self.query_cache[cache_key] = {
                    'timestamp': now,
                    'result': result,
                    'size': len(result_data)
                }
                
                # Prune cache if it exceeds max size
                if len(self.query_cache) > self.max_cache_size:
                    self._prune_cache()
        except Exception as e:
            logger.warning(f"Failed to cache query result: {str(e)}")
        
        return result
    
    def _get_cache_key(self, query: str, parameters: Dict[str, Any] = None) -> str:
        """Generate a cache key for a query and its parameters."""
        import hashlib
        import json
        
        # Normalize the query
        norm_query = self._normalize_query(query)
        
        # Serialize and hash the parameters
        params_str = json.dumps(parameters or {}, sort_keys=True)
        combined = f"{norm_query}|{params_str}"
        
        # Create a hash
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _prune_cache(self) -> None:
        """Remove oldest entries from the cache."""
        # Sort by timestamp
        sorted_entries = sorted(
            [(k, v['timestamp']) for k, v in self.query_cache.items()],
            key=lambda x: x[1]
        )
        
        # Remove the oldest third
        to_remove = sorted_entries[:len(sorted_entries) // 3]
        for key, _ in to_remove:
            del self.query_cache[key]
    
    def get_query_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all executed queries."""
        return self.query_stats
    
    def print_query_statistics(self, min_count: int = 1, min_avg_time: float = 0) -> None:
        """
        Print statistics for queries matching criteria.
        
        Args:
            min_count: Minimum execution count to include
            min_avg_time: Minimum average execution time (ms) to include
        """
        print("\n=== Query Statistics ===")
        print(f"{'Query':<60} {'Count':<8} {'Avg Time (ms)':<15} {'Min Time (ms)':<15} {'Max Time (ms)':<15}")
        print("-" * 115)
        
        for query, stats in sorted(
            self.query_stats.items(),
            key=lambda x: x[1]['avg_time_ms'],
            reverse=True
        ):
            if stats['count'] >= min_count and stats['avg_time_ms'] >= min_avg_time:
                # Truncate long queries
                display_query = query[:57] + "..." if len(query) > 60 else query
                print(f"{display_query:<60} {stats['count']:<8} {stats['avg_time_ms']:<15.2f} {stats['min_time_ms']:<15.2f} {stats['max_time_ms']:<15.2f}")