"""
Timeline Visualizer for the Temporal Evolution Layer.

This module provides visualization capabilities for temporal knowledge graphs,
including timeline views, evolution path visualizations, and temporal snapshots.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import networkx as nx
from matplotlib.figure import Figure
from io import BytesIO
import base64

from src.knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)
from src.knowledge_graph_system.temporal_evolution.query_engine.temporal_query_engine import (
    TemporalQueryEngine
)
from src.knowledge_graph_system.temporal_evolution.analyzer.evolution_analyzer import (
    EvolutionAnalyzer, ResearchField
)


class TimelineVisualizer:
    """
    Visualizer for temporal knowledge graph data, providing timeline views and evolution visualizations.
    """

    def __init__(self, 
                query_engine: TemporalQueryEngine, 
                evolution_analyzer: Optional[EvolutionAnalyzer] = None):
        """
        Initialize the Timeline Visualizer.
        
        Args:
            query_engine: The temporal query engine for retrieving data
            evolution_analyzer: Optional evolution analyzer for advanced visualizations
        """
        self.query_engine = query_engine
        self.evolution_analyzer = evolution_analyzer
        self.fig_size = (12, 8)
        self.dpi = 100
        self.default_colors = {
            'entity': 'dodgerblue',
            'evolution': 'green',
            'relationship': 'gray',
            'highlight': 'red',
            'background': 'white',
            'text': 'black',
            'grid': 'lightgray'
        }
    
    def visualize_entity_timeline(self, 
                                 entity_ids: List[str], 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 include_relationships: bool = True,
                                 highlight_events: List[datetime] = None) -> str:
        """
        Visualize the timeline of selected entities with their evolution events.
        
        Args:
            entity_ids: List of entity IDs to visualize
            start_date: Optional start date for the timeline
            end_date: Optional end date for the timeline
            include_relationships: Whether to include relationships in the visualization
            highlight_events: Optional list of dates to highlight on the timeline
            
        Returns:
            Base64 encoded string of the visualization image
        """
        if not entity_ids:
            raise ValueError("At least one entity ID must be provided")
            
        # Get entities and their evolution history
        entities = []
        for entity_id in entity_ids:
            entity = self.query_engine.get_entity_by_id(entity_id)
            if entity:
                entities.append(entity)
                
                # Get the previous and next versions
                prev_versions = self.query_engine.get_previous_versions(entity_id)
                next_versions = self.query_engine.get_next_versions(entity_id)
                
                entities.extend(prev_versions)
                entities.extend(next_versions)
        
        if not entities:
            raise ValueError("No valid entities found with the provided IDs")
            
        # Determine date range if not provided
        if not start_date:
            start_date = min(entity.created_at for entity in entities)
            # Add a 5% buffer before the start date
            date_range = (max(entity.created_at for entity in entities) - start_date)
            start_date = start_date - date_range * 0.05
            
        if not end_date:
            # Find the latest date among created_at and updated_at
            latest_dates = [entity.created_at for entity in entities]
            latest_dates.extend([entity.updated_at for entity in entities if entity.updated_at])
            
            end_date = max(latest_dates)
            # Add a 5% buffer after the end date
            date_range = (end_date - start_date)
            end_date = end_date + date_range * 0.05
        
        # Get relevant relationships if requested
        relationships = []
        if include_relationships:
            for entity in entities:
                # Get relationships where this entity is source or target
                entity_relationships = self.query_engine.query_relationships(
                    source_ids=[entity.id],
                    time_window=(start_date, end_date)
                )
                entity_relationships.extend(self.query_engine.query_relationships(
                    target_ids=[entity.id],
                    time_window=(start_date, end_date)
                ))
                relationships.extend(entity_relationships)
        
        # Create the figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor(self.default_colors['background'])
        ax.set_facecolor(self.default_colors['background'])
        
        # Setup the timeline
        ax.set_xlim(start_date, end_date)
        ax.set_ylim(0, len(entities) + 1)
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        
        # Hide y-axis ticks but keep the labels
        ax.yaxis.set_ticks([])
        
        # Draw grid
        ax.grid(True, axis='x', linestyle='--', color=self.default_colors['grid'], alpha=0.7)
        
        # Sort entities for better visualization (e.g., by creation date)
        entities.sort(key=lambda e: e.created_at)
        
        # Map entities to y-positions
        entity_positions = {entity.id: i + 1 for i, entity in enumerate(entities)}
        
        # Plot entities
        for entity in entities:
            y_pos = entity_positions[entity.id]
            
            # Plot creation event
            ax.scatter(entity.created_at, y_pos, color=self.default_colors['entity'], 
                      s=100, zorder=10, label=f"{entity.name} created")
            
            # Add label
            ax.text(entity.created_at, y_pos + 0.1, f"{entity.name} v{entity.version_id}", 
                   verticalalignment='bottom', horizontalalignment='center',
                   color=self.default_colors['text'], fontsize=9)
            
            # Plot update events if any
            if entity.updated_at:
                ax.scatter(entity.updated_at, y_pos, color=self.default_colors['entity'], 
                          s=80, marker='s', zorder=10, label=f"{entity.name} updated")
        
        # Plot relationships
        for rel in relationships:
            if rel.source_id in entity_positions and rel.target_id in entity_positions:
                source_y = entity_positions[rel.source_id]
                target_y = entity_positions[rel.target_id]
                
                # Draw an arc connecting the two entities at the relationship creation time
                ax.plot([rel.created_at, rel.created_at], [source_y, target_y], 
                       color=self.default_colors['relationship'], linestyle='-', alpha=0.7,
                       marker='o', markersize=3)
                
                # Add a small label for the relationship type
                mid_y = (source_y + target_y) / 2
                ax.text(rel.created_at, mid_y, rel.type, 
                       color=self.default_colors['text'], fontsize=7,
                       verticalalignment='center', horizontalalignment='left',
                       bbox=dict(facecolor=self.default_colors['background'], alpha=0.7, 
                                boxstyle='round,pad=0.3'))
        
        # Plot evolution relationships
        for i, entity in enumerate(entities):
            # Find any evolution relationships (next versions)
            next_versions = self.query_engine.get_next_versions(entity.id)
            for next_ver in next_versions:
                if next_ver.id in entity_positions:
                    source_y = entity_positions[entity.id]
                    target_y = entity_positions[next_ver.id]
                    
                    # Draw an arrow from this entity to its next version
                    ax.annotate('', 
                               xy=(next_ver.created_at, target_y), 
                               xytext=(entity.created_at, source_y),
                               arrowprops=dict(arrowstyle='->', color=self.default_colors['evolution'], 
                                              connectionstyle='arc3,rad=0.2', linewidth=2))
        
        # Highlight specific events if provided
        if highlight_events:
            for event_date in highlight_events:
                if start_date <= event_date <= end_date:
                    ax.axvline(x=event_date, color=self.default_colors['highlight'], linestyle='--', 
                              alpha=0.7, zorder=5)
        
        # Add title and labels
        ax.set_title('Entity Evolution Timeline', fontsize=14, color=self.default_colors['text'])
        ax.set_xlabel('Time', fontsize=12, color=self.default_colors['text'])
        
        # Create y-axis labels from entity names
        entity_labels = [f"{entity.name} v{entity.version_id}" for entity in entities]
        ax.set_yticks(range(1, len(entities) + 1))
        ax.set_yticklabels(entity_labels, fontsize=9, color=self.default_colors['text'])
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    def visualize_concept_evolution_tree(self, 
                                        root_entity_id: str,
                                        include_attributes: bool = False,
                                        max_depth: int = 5) -> str:
        """
        Visualize the evolution tree of a concept, showing its branches and descendants.
        
        Args:
            root_entity_id: The ID of the root entity to start with
            include_attributes: Whether to include entity attributes in nodes
            max_depth: Maximum depth of the evolution tree to visualize
            
        Returns:
            Base64 encoded string of the visualization image
        """
        # Get the evolution tree starting from root_entity_id
        evolution_tree = self.query_engine.trace_concept_evolution(
            root_entity_id, max_depth=max_depth
        )
        
        if not evolution_tree:
            raise ValueError(f"No evolution data found for entity ID {root_entity_id}")
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes for each entity in the tree
        for entity_id in evolution_tree.keys():
            entity = self.query_engine.get_entity_by_id(entity_id)
            if entity:
                # Create node label
                if include_attributes:
                    # Include selected attributes in the label
                    attrs = [f"{key}: {val}" for key, val in entity.attributes.items()
                            if key in ['version_id', 'year', 'performance']]
                    label = f"{entity.name}\n" + "\n".join(attrs)
                else:
                    label = f"{entity.name} v{entity.version_id}"
                
                # Add node with attributes
                G.add_node(entity_id, 
                          label=label,
                          created_at=entity.created_at,
                          name=entity.name,
                          version=entity.version_id)
        
        # Add edges for evolution relationships
        for parent_id, children in evolution_tree.items():
            for child_id in children:
                # Get relationship type if available
                relationship_type = "evolved_to"  # Default
                relationships = self.query_engine.query_relationships(
                    source_ids=[parent_id],
                    target_ids=[child_id],
                    relationship_types=["EVOLVED_INTO", "REPLACED_BY", "INSPIRED", "MERGED_WITH"]
                )
                
                if relationships:
                    relationship_type = relationships[0].type.lower()
                
                G.add_edge(parent_id, child_id, type=relationship_type)
        
        # Create the figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor(self.default_colors['background'])
        
        # Define node colors based on creation date
        # Use a color gradient from old (blue) to new (red)
        node_dates = [G.nodes[node]['created_at'] for node in G.nodes if 'created_at' in G.nodes[node]]
        if node_dates:
            min_date = min(node_dates)
            max_date = max(node_dates)
            date_range = (max_date - min_date).total_seconds()
            
            node_colors = []
            for node in G.nodes:
                if 'created_at' in G.nodes[node]:
                    # Calculate a value between 0 and 1 based on the date
                    if date_range > 0:
                        value = (G.nodes[node]['created_at'] - min_date).total_seconds() / date_range
                    else:
                        value = 0.5
                    node_colors.append((1-value, 0, value))  # RGB from (1,0,0) to (0,0,1)
                else:
                    node_colors.append((0.5, 0.5, 0.5))  # Gray for nodes without dates
        else:
            node_colors = [self.default_colors['entity']] * len(G.nodes)
        
        # Define edge colors based on relationship type
        edge_colors = []
        for u, v, data in G.edges(data=True):
            if data['type'] == 'evolved_to' or data['type'] == 'evolved_into':
                edge_colors.append('green')
            elif data['type'] == 'replaced_by':
                edge_colors.append('red')
            elif data['type'] == 'inspired':
                edge_colors.append('blue')
            elif data['type'] == 'merged_with':
                edge_colors.append('purple')
            else:
                edge_colors.append('gray')
        
        # Define layout - hierarchical layouts work well for evolution trees
        layout = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR')
        
        # Draw the graph
        nx.draw_networkx_nodes(G, layout, ax=ax, node_size=2000, node_color=node_colors, 
                              alpha=0.8, linewidths=1, edgecolors='black')
        
        nx.draw_networkx_edges(G, layout, ax=ax, edgelist=G.edges(), edge_color=edge_colors,
                              width=2, arrowsize=20, connectionstyle='arc3,rad=0.1')
        
        nx.draw_networkx_labels(G, layout, ax=ax, labels=nx.get_node_attributes(G, 'label'),
                               font_size=8, font_family='sans-serif', font_color='black')
        
        # Add a title
        root_entity = self.query_engine.get_entity_by_id(root_entity_id)
        if root_entity:
            ax.set_title(f"Evolution Tree for {root_entity.name}", fontsize=14)
        else:
            ax.set_title("Concept Evolution Tree", fontsize=14)
        
        # Remove axis
        ax.set_axis_off()
        
        # Add a legend for edge types
        legend_elements = [
            plt.Line2D([0], [0], color='green', lw=2, label='Evolved Into'),
            plt.Line2D([0], [0], color='red', lw=2, label='Replaced By'),
            plt.Line2D([0], [0], color='blue', lw=2, label='Inspired'),
            plt.Line2D([0], [0], color='purple', lw=2, label='Merged With')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    def visualize_field_activity(self, 
                               field_name: str,
                               time_period: int = 90,
                               num_periods: int = 8) -> str:
        """
        Visualize the activity in a research field over time.
        
        Args:
            field_name: Name of the research field to visualize
            time_period: Time period length in days
            num_periods: Number of time periods to analyze
            
        Returns:
            Base64 encoded string of the visualization image
        """
        if not self.evolution_analyzer:
            raise ValueError("Evolution analyzer is required for field activity visualization")
            
        if field_name not in self.evolution_analyzer.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
        
        # Get activity trend data
        trend, activity_data = self.evolution_analyzer.analyze_activity_trend(
            field_name, time_period, num_periods
        )
        
        if not activity_data:
            raise ValueError(f"No activity data available for field '{field_name}'")
        
        # Create the figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor(self.default_colors['background'])
        
        # Extract dates and activity values
        dates = list(activity_data.keys())
        values = list(activity_data.values())
        
        # Plot activity over time
        ax.plot(dates, values, marker='o', linestyle='-', color='blue', 
               linewidth=2, markersize=8)
        
        # Fill area under the curve
        ax.fill_between(dates, values, alpha=0.2, color='blue')
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels and title
        ax.set_title(f"Activity Trend for {field_name} - {trend.value.capitalize()}", 
                    fontsize=14)
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Activity Level", fontsize=12)
        
        # Add trend information
        trend_colors = {
            'accelerating': 'green',
            'decelerating': 'orange',
            'steady': 'blue',
            'stagnant': 'gray',
            'reviving': 'purple',
            'declining': 'red'
        }
        
        ax.text(0.02, 0.95, f"Trend: {trend.value.capitalize()}", 
               transform=ax.transAxes, fontsize=12,
               verticalalignment='top', horizontalalignment='left',
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'),
               color=trend_colors.get(trend.value, 'black'))
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    def visualize_research_waves(self, field_name: str) -> str:
        """
        Visualize research waves (periods of increased and decreased activity).
        
        Args:
            field_name: Name of the research field to visualize
            
        Returns:
            Base64 encoded string of the visualization image
        """
        if not self.evolution_analyzer:
            raise ValueError("Evolution analyzer is required for research wave visualization")
            
        if field_name not in self.evolution_analyzer.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
        
        # Get research waves
        waves = self.evolution_analyzer.identify_research_waves(field_name)
        if not waves:
            raise ValueError(f"No research waves identified for field '{field_name}'")
        
        # Get activity data
        field = self.evolution_analyzer.research_fields[field_name]
        activity_data = sorted(field.activity_history.items())
        
        if not activity_data:
            raise ValueError(f"No activity data available for field '{field_name}'")
        
        # Create the figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor(self.default_colors['background'])
        
        # Extract dates and activity values
        dates = [t for t, _ in activity_data]
        values = [a for _, a in activity_data]
        
        # Plot activity over time
        ax.plot(dates, values, marker='o', linestyle='-', color='blue', 
               linewidth=2, markersize=6, label="Activity")
        
        # Highlight research waves
        for i, wave in enumerate(waves):
            # Create a span for each wave
            ax.axvspan(wave['start_date'], wave['end_date'], 
                      alpha=0.2, color=f'C{i % 10}', 
                      label=f"Wave {i+1}: {wave['duration_days']:.0f} days")
            
            # Mark peak and valley points
            ax.scatter([wave['start_date'], wave['valley_date'], wave['end_date']], 
                      [wave['start_activity'], wave['valley_activity'], wave['end_activity']],
                      color=f'C{i % 10}', s=100, zorder=10)
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels and title
        ax.set_title(f"Research Waves in {field_name}", fontsize=14)
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Activity Level", fontsize=12)
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Add wave information
        text_info = "\n".join([
            f"Wave {i+1}: {wave['duration_days']:.0f} days, "
            f"Amplitude: {wave['amplitude']:.1f}" 
            for i, wave in enumerate(waves[:3])  # Show info for top 3 waves
        ])
        
        ax.text(0.02, 0.95, text_info, 
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top', horizontalalignment='left',
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    def visualize_field_convergence(self, 
                                  field_names: List[str],
                                  time_period: int = 90,
                                  num_periods: int = 8) -> str:
        """
        Visualize whether research fields are converging or diverging over time.
        
        Args:
            field_names: List of research field names to compare
            time_period: Time period length in days
            num_periods: Number of time periods to analyze
            
        Returns:
            Base64 encoded string of the visualization image
        """
        if not self.evolution_analyzer:
            raise ValueError("Evolution analyzer is required for field convergence visualization")
        
        # Check if all fields exist
        for name in field_names:
            if name not in self.evolution_analyzer.research_fields:
                raise ValueError(f"Research field '{name}' not found")
        
        # Get convergence data
        convergence_data = self.evolution_analyzer.analyze_convergence_divergence(
            field_names, time_period, num_periods
        )
        
        if not convergence_data:
            raise ValueError("No convergence data available for the specified fields")
        
        # Create the figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=self.dpi)
        fig.patch.set_facecolor(self.default_colors['background'])
        
        # Sort time windows chronologically
        time_windows = sorted(convergence_data.keys())
        
        # Get all field pairs
        field_pairs = set()
        for window in convergence_data.values():
            field_pairs.update(window.keys())
        
        # Plot similarities for each field pair over time
        for pair in field_pairs:
            # Extract similarities for this pair across all time windows
            similarities = []
            for window in time_windows:
                if pair in convergence_data[window]:
                    similarities.append(convergence_data[window][pair])
                else:
                    similarities.append(0)  # Default to 0 if data is missing
            
            # Convert time windows to datetime objects
            dates = [datetime.strptime(window, "%Y-%m-%d") for window in time_windows]
            
            # Plot the convergence trend for this pair
            ax.plot(dates, similarities, marker='o', linestyle='-', 
                   label=pair.replace('_', ' vs '))
        
        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add labels and title
        ax.set_title("Research Field Convergence/Divergence Over Time", fontsize=14)
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Similarity", fontsize=12)
        
        # Set y-axis limits
        ax.set_ylim(0, 1)
        
        # Add threshold lines
        ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.7,
                  label="High Convergence (0.7)")
        ax.axhline(y=0.3, color='red', linestyle='--', alpha=0.7,
                  label="Low Convergence (0.3)")
        
        # Add legend
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Add interpretation note
        ax.text(0.02, 0.02, 
               "Increasing trend = Convergence\nDecreasing trend = Divergence", 
               transform=ax.transAxes, fontsize=10,
               verticalalignment='bottom', horizontalalignment='left',
               bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Adjust layout
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    def generate_time_series_animation(self, 
                                     entity_ids: List[str],
                                     start_date: datetime,
                                     end_date: datetime,
                                     num_frames: int = 20,
                                     output_format: str = 'html') -> str:
        """
        Generate an animation showing how entities and relationships evolve over time.
        
        Args:
            entity_ids: List of entity IDs to include
            start_date: Start date for the animation
            end_date: End date for the animation
            num_frames: Number of frames in the animation
            output_format: Output format ('html' or 'gif')
            
        Returns:
            HTML string or base64 encoded GIF depending on output_format
        """
        # This is a placeholder for animation generation
        # In a real implementation, this would create an animation using matplotlib's animation
        # functionality or a similar library
        
        # For now, create a simple HTML with explanation
        if output_format == 'html':
            return """
            <div style="text-align: center; padding: 20px; border: 1px solid #ccc; border-radius: 5px;">
                <h2>Time Series Animation</h2>
                <p>This would be an animation showing the temporal evolution of the selected entities.</p>
                <p>The animation would display how entities and their relationships change over time.</p>
                <p>Implementation pending - animation generation requires client-side libraries.</p>
            </div>
            """
        else:
            # Return a placeholder image
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "Animation feature coming soon", 
                   horizontalalignment='center', verticalalignment='center',
                   fontsize=14, transform=ax.transAxes)
            ax.set_axis_off()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return image_base64
            
    def visualize_snapshot_comparison(self,
                                    field_name: str,
                                    date1: datetime,
                                    date2: datetime) -> str:
        """
        Visualize a comparison between two snapshots of a research field at different times.
        
        Args:
            field_name: Name of the research field to compare
            date1: First snapshot date
            date2: Second snapshot date
            
        Returns:
            Base64 encoded string of the visualization image
        """
        if not self.evolution_analyzer:
            raise ValueError("Evolution analyzer is required for snapshot comparison")
            
        if field_name not in self.evolution_analyzer.research_fields:
            raise ValueError(f"Research field '{field_name}' not found")
        
        # Get snapshot data
        snapshot1 = self.query_engine.get_snapshot(date1)
        snapshot2 = self.query_engine.get_snapshot(date2)
        
        if not snapshot1 or not snapshot2:
            raise ValueError("Could not retrieve snapshots for the specified dates")
        
        # Create the figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(2*self.fig_size[0], self.fig_size[1]), 
                                      dpi=self.dpi)
        fig.patch.set_facecolor(self.default_colors['background'])
        
        # Filter entities and relationships for the field
        field = self.evolution_analyzer.research_fields[field_name]
        field_entity_ids = set(entity.id for entity in field.entities)
        
        # Create graphs for each snapshot
        G1 = nx.Graph()
        G2 = nx.Graph()
        
        # Add nodes and edges for snapshot 1
        for entity_id, entity_data in snapshot1['entities'].items():
            if entity_id in field_entity_ids:
                G1.add_node(entity_id, label=entity_data['name'], 
                           type=entity_data.get('type', 'unknown'))
        
        for rel in snapshot1['relationships']:
            if rel['source_id'] in field_entity_ids and rel['target_id'] in field_entity_ids:
                G1.add_edge(rel['source_id'], rel['target_id'], type=rel['type'])
        
        # Add nodes and edges for snapshot 2
        for entity_id, entity_data in snapshot2['entities'].items():
            if entity_id in field_entity_ids:
                G2.add_node(entity_id, label=entity_data['name'], 
                           type=entity_data.get('type', 'unknown'))
        
        for rel in snapshot2['relationships']:
            if rel['source_id'] in field_entity_ids and rel['target_id'] in field_entity_ids:
                G2.add_edge(rel['source_id'], rel['target_id'], type=rel['type'])
        
        # Calculate node positions - use the same layout algorithm for both
        # to make comparison easier
        if len(G1.nodes) > 0 and len(G2.nodes) > 0:
            # Find common nodes to maintain positions
            common_nodes = set(G1.nodes).intersection(set(G2.nodes))
            
            if common_nodes:
                # Calculate positions for the union of both graphs
                G_union = nx.Graph()
                G_union.add_nodes_from(list(G1.nodes) + [n for n in G2.nodes if n not in G1.nodes])
                G_union.add_edges_from(list(G1.edges) + [e for e in G2.edges if e not in G1.edges])
                
                layout = nx.spring_layout(G_union, seed=42)
            else:
                # Calculate separate layouts but with the same parameters
                layout1 = nx.spring_layout(G1, seed=42)
                layout2 = nx.spring_layout(G2, seed=42)
                layout = {**layout1, **layout2}
        elif len(G1.nodes) > 0:
            layout = nx.spring_layout(G1, seed=42)
        elif len(G2.nodes) > 0:
            layout = nx.spring_layout(G2, seed=42)
        else:
            # No nodes in either graph
            return "No data available for the specified snapshots"
        
        # Draw the first snapshot
        ax1.set_title(f"Snapshot at {date1.strftime('%Y-%m-%d')}", fontsize=14)
        
        if len(G1.nodes) > 0:
            nx.draw_networkx_nodes(G1, layout, ax=ax1, node_size=300, 
                                  node_color='skyblue', alpha=0.8)
            nx.draw_networkx_edges(G1, layout, ax=ax1, edge_color='gray', width=1)
            nx.draw_networkx_labels(G1, layout, ax=ax1, 
                                   labels={n: G1.nodes[n]['label'] for n in G1.nodes},
                                   font_size=8)
        else:
            ax1.text(0.5, 0.5, "No data available", 
                    horizontalalignment='center', verticalalignment='center')
        
        ax1.set_axis_off()
        
        # Draw the second snapshot
        ax2.set_title(f"Snapshot at {date2.strftime('%Y-%m-%d')}", fontsize=14)
        
        if len(G2.nodes) > 0:
            nx.draw_networkx_nodes(G2, layout, ax=ax2, node_size=300, 
                                  node_color='lightgreen', alpha=0.8)
            nx.draw_networkx_edges(G2, layout, ax=ax2, edge_color='gray', width=1)
            nx.draw_networkx_labels(G2, layout, ax=ax2, 
                                   labels={n: G2.nodes[n]['label'] for n in G2.nodes},
                                   font_size=8)
        else:
            ax2.text(0.5, 0.5, "No data available", 
                    horizontalalignment='center', verticalalignment='center')
        
        ax2.set_axis_off()
        
        # Add comparison information
        fig.suptitle(f"Comparison of {field_name} Research Field", fontsize=16)
        
        # Add stats below the plots
        stats_text = (
            f"Snapshot 1: {len(G1.nodes)} entities, {len(G1.edges)} relationships\n"
            f"Snapshot 2: {len(G2.nodes)} entities, {len(G2.edges)} relationships\n"
            f"New entities: {len(set(G2.nodes) - set(G1.nodes))}\n"
            f"Removed entities: {len(set(G1.nodes) - set(G2.nodes))}\n"
            f"New relationships: {len(set(G2.edges) - set(G1.edges))}\n"
            f"Removed relationships: {len(set(G1.edges) - set(G2.edges))}"
        )
        
        fig.text(0.5, 0.01, stats_text, horizontalalignment='center', 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64