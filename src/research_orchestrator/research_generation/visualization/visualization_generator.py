"""
Visualization Generator for Research Generation.

This module provides functionality for generating charts, graphs, diagrams,
and other visual representations of research data.
"""

import logging
import os
import base64
import tempfile
import uuid
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union, Tuple, Set
import json
import re
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import visualization-related modules
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib/Seaborn not available. Visualization capabilities will be limited.")

# Try to import diagram generation modules
try:
    import pydot
    PYDOT_AVAILABLE = True
except ImportError:
    PYDOT_AVAILABLE = False
    logger.warning("Pydot not available. Diagram generation capabilities will be limited.")

# Try to import networkx for graph visualization
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not available. Network visualization capabilities will be limited.")


class VisualizationType(Enum):
    """Types of visualizations that can be generated."""
    CHART = auto()     # Statistical charts (bar, line, scatter, etc.)
    DIAGRAM = auto()   # Diagrams (flowchart, architecture diagram, etc.)
    NETWORK = auto()   # Network graphs (node-edge graphs)
    TABLE = auto()     # Formatted tables


class ChartType(Enum):
    """Types of charts that can be generated."""
    BAR = auto()           # Bar chart
    LINE = auto()          # Line chart
    SCATTER = auto()       # Scatter plot
    PIE = auto()           # Pie chart
    HISTOGRAM = auto()     # Histogram
    BOX = auto()           # Box plot
    VIOLIN = auto()        # Violin plot
    HEATMAP = auto()       # Heatmap
    AREA = auto()          # Area chart
    RADAR = auto()         # Radar chart
    BUBBLE = auto()        # Bubble chart
    CANDLESTICK = auto()   # Candlestick chart
    ERRORBAR = auto()      # Error bar chart
    CONTOUR = auto()       # Contour plot
    SURFACE = auto()       # 3D surface plot


class DiagramType(Enum):
    """Types of diagrams that can be generated."""
    FLOWCHART = auto()     # Flowchart
    SEQUENCE = auto()      # Sequence diagram
    CLASS = auto()         # Class diagram
    ENTITY = auto()        # Entity-relationship diagram
    STATE = auto()         # State diagram
    ACTIVITY = auto()      # Activity diagram
    COMPONENT = auto()     # Component diagram
    DEPLOYMENT = auto()    # Deployment diagram
    GANTT = auto()         # Gantt chart
    MINDMAP = auto()       # Mind map


class VisualizationFormat(Enum):
    """Output formats for visualizations."""
    PNG = auto()       # Portable Network Graphics
    SVG = auto()       # Scalable Vector Graphics
    JPG = auto()       # JPEG image
    PDF = auto()       # Portable Document Format
    HTML = auto()      # HTML (for interactive visualizations)
    MARKDOWN = auto()  # Markdown (for embedding in documents)
    BASE64 = auto()    # Base64-encoded image (for embedding in HTML/markdown)


class VisualizationConfig:
    """Configuration for visualization generation."""
    
    def __init__(self,
                width: int = 800,
                height: int = 600,
                dpi: int = 100,
                theme: str = "default",
                palette: str = "viridis",
                title_font_size: int = 14,
                axis_font_size: int = 12,
                label_font_size: int = 10,
                legend_font_size: int = 10,
                background_color: str = "white",
                grid: bool = True,
                output_dir: Optional[str] = None,
                format: VisualizationFormat = VisualizationFormat.PNG,
                interactive: bool = False):
        """
        Initialize visualization configuration.
        
        Args:
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            dpi: Resolution in dots per inch
            theme: Visual theme for the visualization
            palette: Color palette for the visualization
            title_font_size: Font size for the title
            axis_font_size: Font size for axis labels
            label_font_size: Font size for data labels
            legend_font_size: Font size for legend
            background_color: Background color
            grid: Whether to display grid lines
            output_dir: Directory for saving visualization files
            format: Output format for the visualization
            interactive: Whether to generate an interactive visualization
        """
        self.width = width
        self.height = height
        self.dpi = dpi
        self.theme = theme
        self.palette = palette
        self.title_font_size = title_font_size
        self.axis_font_size = axis_font_size
        self.label_font_size = label_font_size
        self.legend_font_size = legend_font_size
        self.background_color = background_color
        self.grid = grid
        
        # Set output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "output",
                "visualizations"
            )
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set output format
        if isinstance(format, str):
            try:
                self.format = VisualizationFormat[format.upper()]
            except KeyError:
                self.format = VisualizationFormat.PNG
                logger.warning(f"Invalid format: {format}. Using PNG instead.")
        else:
            self.format = format
            
        self.interactive = interactive
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "width": self.width,
            "height": self.height,
            "dpi": self.dpi,
            "theme": self.theme,
            "palette": self.palette,
            "title_font_size": self.title_font_size,
            "axis_font_size": self.axis_font_size,
            "label_font_size": self.label_font_size,
            "legend_font_size": self.legend_font_size,
            "background_color": self.background_color,
            "grid": self.grid,
            "output_dir": self.output_dir,
            "format": self.format.name,
            "interactive": self.interactive
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualizationConfig':
        """
        Create configuration from dictionary.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            VisualizationConfig instance
        """
        return cls(
            width=data.get("width", 800),
            height=data.get("height", 600),
            dpi=data.get("dpi", 100),
            theme=data.get("theme", "default"),
            palette=data.get("palette", "viridis"),
            title_font_size=data.get("title_font_size", 14),
            axis_font_size=data.get("axis_font_size", 12),
            label_font_size=data.get("label_font_size", 10),
            legend_font_size=data.get("legend_font_size", 10),
            background_color=data.get("background_color", "white"),
            grid=data.get("grid", True),
            output_dir=data.get("output_dir"),
            format=data.get("format", VisualizationFormat.PNG),
            interactive=data.get("interactive", False)
        )


class VisualizationGenerator:
    """
    Visualization Generator for creating charts, diagrams, and other visual
    representations of research data.
    """
    
    def __init__(self, 
                config: Optional[VisualizationConfig] = None,
                knowledge_graph_adapter = None):
        """
        Initialize the Visualization Generator.
        
        Args:
            config: Configuration for visualization generation
            knowledge_graph_adapter: Adapter for accessing knowledge graph
        """
        self.config = config or VisualizationConfig()
        self.knowledge_graph_adapter = knowledge_graph_adapter
        self.logger = logging.getLogger(__name__)
        
        # Apply default visualization settings
        if MATPLOTLIB_AVAILABLE:
            self._initialize_matplotlib()
            
        # Create placeholder for last generated visualization
        self.last_visualization_path = None
        self.last_visualization_data = None
    
    def _initialize_matplotlib(self) -> None:
        """Initialize matplotlib with configuration settings."""
        try:
            # Set theme based on configuration
            if self.config.theme == "dark":
                plt.style.use("dark_background")
            elif self.config.theme == "seaborn":
                plt.style.use("seaborn")
            elif self.config.theme == "ggplot":
                plt.style.use("ggplot")
            elif self.config.theme == "fivethirtyeight":
                plt.style.use("fivethirtyeight")
            else:
                plt.style.use("default")
                
            # Configure seaborn if available
            if 'sns' in globals():
                sns.set_palette(self.config.palette)
                sns.set_style("whitegrid" if self.config.grid else "white")
                
            # Set default figure size
            plt.rcParams["figure.figsize"] = (self.config.width / 100, self.config.height / 100)
            plt.rcParams["figure.dpi"] = self.config.dpi
            
            # Set font sizes
            plt.rcParams["font.size"] = self.config.label_font_size
            plt.rcParams["axes.titlesize"] = self.config.title_font_size
            plt.rcParams["axes.labelsize"] = self.config.axis_font_size
            plt.rcParams["legend.fontsize"] = self.config.legend_font_size
            
            # Set background color
            plt.rcParams["figure.facecolor"] = self.config.background_color
            plt.rcParams["axes.facecolor"] = self.config.background_color
            
            self.logger.info("Matplotlib initialized with custom settings")
        except Exception as e:
            self.logger.error(f"Error initializing matplotlib: {e}")
    
    def create_visualization(self,
                           data: Union[Dict[str, Any], List[Dict[str, Any]], 'pd.DataFrame'],
                           vis_type: Union[VisualizationType, str],
                           subtype: Union[ChartType, DiagramType, str, None] = None,
                           title: str = "",
                           x_label: str = "",
                           y_label: str = "",
                           x_column: Optional[str] = None,
                           y_column: Optional[str] = None,
                           category_column: Optional[str] = None,
                           size_column: Optional[str] = None,
                           color_column: Optional[str] = None,
                           file_name: Optional[str] = None,
                           **kwargs) -> str:
        """
        Create a visualization based on the provided data.
        
        Args:
            data: Data for the visualization (dict, list of dicts, or DataFrame)
            vis_type: Type of visualization to create
            subtype: Subtype of visualization (e.g., bar chart, flowchart)
            title: Title for the visualization
            x_label: Label for the x-axis
            y_label: Label for the y-axis
            x_column: Column name for x-axis data
            y_column: Column name for y-axis data
            category_column: Column name for categories/grouping
            size_column: Column name for size values (bubble charts)
            color_column: Column name for color values
            file_name: Name for the output file (without extension)
            **kwargs: Additional parameters for specific visualization types
            
        Returns:
            Path to the generated visualization file or embedded visualization
        """
        # Convert string types to enum values
        if isinstance(vis_type, str):
            try:
                vis_type = VisualizationType[vis_type.upper()]
            except KeyError:
                raise ValueError(f"Invalid visualization type: {vis_type}")
                
        if isinstance(subtype, str):
            if vis_type == VisualizationType.CHART:
                try:
                    subtype = ChartType[subtype.upper()]
                except KeyError:
                    raise ValueError(f"Invalid chart type: {subtype}")
            elif vis_type == VisualizationType.DIAGRAM:
                try:
                    subtype = DiagramType[subtype.upper()]
                except KeyError:
                    raise ValueError(f"Invalid diagram type: {subtype}")
        
        # Create a default filename if none provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"visualization_{vis_type.name.lower()}_{timestamp}"
        
        # Convert data to DataFrame if needed
        df = self._ensure_dataframe(data)
        
        # Generate visualization based on type
        if vis_type == VisualizationType.CHART:
            return self._create_chart(
                df, subtype, title, x_label, y_label,
                x_column, y_column, category_column,
                size_column, color_column, file_name, **kwargs
            )
        elif vis_type == VisualizationType.DIAGRAM:
            return self._create_diagram(
                df, subtype, title, file_name, **kwargs
            )
        elif vis_type == VisualizationType.NETWORK:
            return self._create_network(
                df, title, file_name, **kwargs
            )
        elif vis_type == VisualizationType.TABLE:
            return self._create_table(
                df, title, file_name, **kwargs
            )
        else:
            raise ValueError(f"Unsupported visualization type: {vis_type}")
    
    def _ensure_dataframe(self, data: Union[Dict[str, Any], List[Dict[str, Any]], 'pd.DataFrame']) -> 'pd.DataFrame':
        """
        Convert data to pandas DataFrame if not already.
        
        Args:
            data: Data in various formats
            
        Returns:
            pandas DataFrame
        """
        if 'pd' not in globals():
            raise ImportError("Pandas is required for data processing")
            
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame.from_dict(data, orient='columns')
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return pd.DataFrame(data)
        else:
            raise ValueError("Data must be a DataFrame, dictionary, or list of dictionaries")
    
    def _create_chart(self,
                    df: 'pd.DataFrame',
                    chart_type: Optional[ChartType],
                    title: str,
                    x_label: str,
                    y_label: str,
                    x_column: Optional[str],
                    y_column: Optional[str],
                    category_column: Optional[str],
                    size_column: Optional[str],
                    color_column: Optional[str],
                    file_name: str,
                    **kwargs) -> str:
        """
        Create a chart visualization.
        
        Args:
            df: DataFrame with data for the chart
            chart_type: Type of chart to create
            title: Chart title
            x_label: Label for x-axis
            y_label: Label for y-axis
            x_column: Column name for x-axis data
            y_column: Column name for y-axis data
            category_column: Column name for categories/grouping
            size_column: Column name for size values (bubble charts)
            color_column: Column name for color values
            file_name: Name for the output file
            **kwargs: Additional parameters for specific chart types
            
        Returns:
            Path to the generated chart file or embedded chart
        """
        if not MATPLOTLIB_AVAILABLE:
            self.logger.error("Matplotlib is required for chart generation")
            return "ERROR: Matplotlib is required for chart generation"
        
        try:
            # Infer column names if not specified
            if not x_column and len(df.columns) > 0:
                x_column = df.columns[0]
            if not y_column and len(df.columns) > 1:
                y_column = df.columns[1]
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            
            # Set chart title and labels
            ax.set_title(title, fontsize=self.config.title_font_size)
            ax.set_xlabel(x_label or x_column, fontsize=self.config.axis_font_size)
            ax.set_ylabel(y_label or y_column, fontsize=self.config.axis_font_size)
            
            # Generate chart based on type
            if chart_type == ChartType.BAR:
                self._create_bar_chart(df, ax, x_column, y_column, category_column, color_column, **kwargs)
            elif chart_type == ChartType.LINE:
                self._create_line_chart(df, ax, x_column, y_column, category_column, color_column, **kwargs)
            elif chart_type == ChartType.SCATTER:
                self._create_scatter_chart(df, ax, x_column, y_column, category_column, color_column, size_column, **kwargs)
            elif chart_type == ChartType.PIE:
                self._create_pie_chart(df, ax, x_column, y_column, **kwargs)
            elif chart_type == ChartType.HISTOGRAM:
                self._create_histogram(df, ax, x_column, category_column, **kwargs)
            elif chart_type == ChartType.BOX:
                self._create_box_plot(df, ax, x_column, y_column, category_column, **kwargs)
            elif chart_type == ChartType.VIOLIN:
                self._create_violin_plot(df, ax, x_column, y_column, category_column, **kwargs)
            elif chart_type == ChartType.HEATMAP:
                self._create_heatmap(df, ax, **kwargs)
            elif chart_type == ChartType.AREA:
                self._create_area_chart(df, ax, x_column, y_column, category_column, **kwargs)
            else:
                # Default to bar chart if type not supported
                self._create_bar_chart(df, ax, x_column, y_column, category_column, color_column, **kwargs)
            
            # Add grid if specified
            ax.grid(self.config.grid)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save and return visualization
            return self._save_and_return_visualization(fig, file_name)
            
        except Exception as e:
            self.logger.error(f"Error creating chart: {e}")
            # Create a simple error visualization
            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            ax.text(0.5, 0.5, f"Error creating visualization: {str(e)}", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='red')
            plt.axis('off')
            return self._save_and_return_visualization(fig, f"error_{file_name}")
    
    def _create_bar_chart(self,
                         df: 'pd.DataFrame',
                         ax: 'plt.Axes',
                         x_column: str,
                         y_column: str,
                         category_column: Optional[str] = None,
                         color_column: Optional[str] = None,
                         orientation: str = 'vertical',
                         bar_width: float = 0.8,
                         **kwargs) -> None:
        """Create a bar chart on the given axis."""
        if category_column:
            # Grouped bar chart
            grouped = df.groupby([x_column, category_column])[y_column].mean().unstack()
            if orientation == 'horizontal':
                grouped.plot(kind='barh', ax=ax, width=bar_width)
            else:
                grouped.plot(kind='bar', ax=ax, width=bar_width)
        else:
            # Simple bar chart
            if orientation == 'horizontal':
                df.plot(kind='barh', x=x_column, y=y_column, ax=ax, width=bar_width, 
                      color=df[color_column] if color_column else None)
            else:
                df.plot(kind='bar', x=x_column, y=y_column, ax=ax, width=bar_width,
                      color=df[color_column] if color_column else None)
        
        # Add data labels if specified
        if kwargs.get('show_values', False):
            for container in ax.containers:
                ax.bar_label(container, fmt='%.1f', padding=3)
    
    def _create_line_chart(self,
                          df: 'pd.DataFrame',
                          ax: 'plt.Axes',
                          x_column: str,
                          y_column: str,
                          category_column: Optional[str] = None,
                          color_column: Optional[str] = None,
                          marker: Optional[str] = None,
                          **kwargs) -> None:
        """Create a line chart on the given axis."""
        if category_column:
            # Multiple lines
            for category, group in df.groupby(category_column):
                ax.plot(group[x_column], group[y_column], marker=marker, 
                       label=category, linewidth=kwargs.get('linewidth', 2))
            ax.legend()
        else:
            # Single line
            ax.plot(df[x_column], df[y_column], marker=marker, 
                   color=df[color_column].iloc[0] if color_column else None,
                   linewidth=kwargs.get('linewidth', 2))
        
        # Add markers for data points if specified
        if kwargs.get('show_points', False) and not marker:
            ax.scatter(df[x_column], df[y_column], s=kwargs.get('point_size', 30))
    
    def _create_scatter_chart(self,
                             df: 'pd.DataFrame',
                             ax: 'plt.Axes',
                             x_column: str,
                             y_column: str,
                             category_column: Optional[str] = None,
                             color_column: Optional[str] = None,
                             size_column: Optional[str] = None,
                             **kwargs) -> None:
        """Create a scatter plot on the given axis."""
        if category_column:
            # Colored by category
            for category, group in df.groupby(category_column):
                sizes = None
                if size_column:
                    sizes = group[size_column] * kwargs.get('size_factor', 1)
                ax.scatter(group[x_column], group[y_column], 
                          s=sizes, 
                          label=category,
                          alpha=kwargs.get('alpha', 0.7))
            ax.legend()
        else:
            # Single category
            sizes = None
            if size_column:
                sizes = df[size_column] * kwargs.get('size_factor', 1)
            colors = None
            if color_column:
                colors = df[color_column]
            ax.scatter(df[x_column], df[y_column], 
                      s=sizes, 
                      c=colors,
                      alpha=kwargs.get('alpha', 0.7))
            
            # Add colorbar if using color mapping
            if color_column and kwargs.get('show_colorbar', True):
                plt.colorbar(ax.collections[0], ax=ax, label=color_column)
    
    def _create_pie_chart(self,
                         df: 'pd.DataFrame',
                         ax: 'plt.Axes',
                         x_column: str,
                         y_column: str,
                         **kwargs) -> None:
        """Create a pie chart on the given axis."""
        # Get labels and values
        labels = df[x_column].tolist()
        values = df[y_column].tolist()
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=None,  # We'll add custom legend
            autopct=kwargs.get('percentage_format', '%.1f%%'),
            startangle=kwargs.get('start_angle', 90),
            shadow=kwargs.get('shadow', False),
            explode=kwargs.get('explode', None),
            wedgeprops=kwargs.get('wedgeprops', {'width': 0.5, 'edgecolor': 'w'}) if kwargs.get('donut', False) else None
        )
        
        # Customize text appearance
        for autotext in autotexts:
            autotext.set_fontsize(kwargs.get('percentage_fontsize', 10))
            autotext.set_color(kwargs.get('percentage_color', 'white'))
        
        # Add legend
        ax.legend(wedges, labels, title=x_column, loc=kwargs.get('legend_position', 'center left'),
                 bbox_to_anchor=kwargs.get('legend_bbox', (1, 0, 0.5, 1)))
        
        # Equal aspect ratio ensures circular pie
        ax.set_aspect('equal')
        
        # Remove axis
        plt.axis('off')
    
    def _create_histogram(self,
                         df: 'pd.DataFrame',
                         ax: 'plt.Axes',
                         x_column: str,
                         category_column: Optional[str] = None,
                         **kwargs) -> None:
        """Create a histogram on the given axis."""
        if category_column:
            # Multiple histograms
            for category, group in df.groupby(category_column):
                ax.hist(group[x_column], 
                       alpha=kwargs.get('alpha', 0.7),
                       bins=kwargs.get('bins', 10),
                       label=category,
                       density=kwargs.get('density', False))
            ax.legend()
        else:
            # Single histogram
            ax.hist(df[x_column], 
                   bins=kwargs.get('bins', 10),
                   density=kwargs.get('density', False),
                   alpha=kwargs.get('alpha', 0.7),
                   color=kwargs.get('color', None))
        
        # Add kernel density estimate if specified
        if kwargs.get('kde', False) and 'sns' in globals():
            for spine in ax.spines.values():
                spine.set_visible(True)
            if category_column:
                for category, group in df.groupby(category_column):
                    sns.kdeplot(group[x_column], ax=ax, label=f"KDE {category}")
            else:
                sns.kdeplot(df[x_column], ax=ax, label="KDE")
    
    def _create_box_plot(self,
                        df: 'pd.DataFrame',
                        ax: 'plt.Axes',
                        x_column: str,
                        y_column: str,
                        category_column: Optional[str] = None,
                        **kwargs) -> None:
        """Create a box plot on the given axis."""
        if 'sns' in globals() and kwargs.get('use_seaborn', True):
            # Use seaborn's boxplot for better appearance
            sns.boxplot(x=x_column, y=y_column, hue=category_column, 
                       data=df, ax=ax, 
                       palette=kwargs.get('palette', None))
        else:
            # Use matplotlib's boxplot
            if category_column:
                # Grouped box plot
                df.boxplot(column=y_column, by=x_column, ax=ax, grid=self.config.grid)
            else:
                # Simple box plot
                df.boxplot(column=y_column, ax=ax, grid=self.config.grid)
        
        # Add individual points if specified
        if kwargs.get('show_points', False) and 'sns' in globals():
            sns.stripplot(x=x_column, y=y_column, hue=category_column, 
                         data=df, ax=ax, size=kwargs.get('point_size', 4),
                         alpha=kwargs.get('alpha', 0.7),
                         jitter=kwargs.get('jitter', True))
    
    def _create_violin_plot(self,
                           df: 'pd.DataFrame',
                           ax: 'plt.Axes',
                           x_column: str,
                           y_column: str,
                           category_column: Optional[str] = None,
                           **kwargs) -> None:
        """Create a violin plot on the given axis."""
        if 'sns' not in globals():
            self.logger.warning("Seaborn is required for violin plots. Falling back to box plot.")
            self._create_box_plot(df, ax, x_column, y_column, category_column, **kwargs)
            return
        
        # Create violin plot using seaborn
        sns.violinplot(x=x_column, y=y_column, hue=category_column, 
                      data=df, ax=ax, 
                      palette=kwargs.get('palette', None),
                      inner=kwargs.get('inner', 'box'),
                      scale=kwargs.get('scale', 'width'))
        
        # Add individual points if specified
        if kwargs.get('show_points', False):
            sns.stripplot(x=x_column, y=y_column, hue=category_column, 
                         data=df, ax=ax, size=kwargs.get('point_size', 4),
                         alpha=kwargs.get('alpha', 0.7),
                         jitter=kwargs.get('jitter', True),
                         color=kwargs.get('point_color', 'black'))
    
    def _create_heatmap(self,
                       df: 'pd.DataFrame',
                       ax: 'plt.Axes',
                       **kwargs) -> None:
        """Create a heatmap on the given axis."""
        if 'sns' not in globals():
            self.logger.warning("Seaborn is required for heatmaps. Using matplotlib instead.")
            # Use matplotlib's imshow for heatmap
            im = ax.imshow(df.values, cmap=kwargs.get('colormap', 'viridis'))
            ax.set_xticks(np.arange(len(df.columns)))
            ax.set_yticks(np.arange(len(df.index)))
            ax.set_xticklabels(df.columns)
            ax.set_yticklabels(df.index)
            plt.colorbar(im, ax=ax)
        else:
            # Use seaborn's heatmap
            sns.heatmap(df, 
                       annot=kwargs.get('show_values', True),
                       fmt=kwargs.get('value_format', '.2f'),
                       cmap=kwargs.get('colormap', 'viridis'),
                       linewidths=kwargs.get('linewidths', 0.5),
                       ax=ax)
        
        # Rotate x-axis labels if needed
        if kwargs.get('rotate_xlabels', False):
            plt.setp(ax.get_xticklabels(), rotation=kwargs.get('rotation', 45), 
                    ha=kwargs.get('horizontal_alignment', 'right'))
    
    def _create_area_chart(self,
                          df: 'pd.DataFrame',
                          ax: 'plt.Axes',
                          x_column: str,
                          y_column: str,
                          category_column: Optional[str] = None,
                          **kwargs) -> None:
        """Create an area chart on the given axis."""
        if category_column:
            # Stacked area chart
            df_pivot = df.pivot(index=x_column, columns=category_column, values=y_column)
            df_pivot.plot.area(ax=ax, stacked=kwargs.get('stacked', True), 
                             alpha=kwargs.get('alpha', 0.7))
        else:
            # Simple area chart
            df.plot.area(x=x_column, y=y_column, ax=ax, 
                       alpha=kwargs.get('alpha', 0.7),
                       stacked=kwargs.get('stacked', True))
        
        # Customize area chart
        if kwargs.get('fill', True):
            ax.fill_between(df[x_column], df[y_column], alpha=kwargs.get('alpha', 0.3))
    
    def _create_diagram(self,
                       df: 'pd.DataFrame',
                       diagram_type: Optional[DiagramType],
                       title: str,
                       file_name: str,
                       **kwargs) -> str:
        """
        Create a diagram visualization.
        
        Args:
            df: DataFrame with data for the diagram
            diagram_type: Type of diagram to create
            title: Diagram title
            file_name: Name for the output file
            **kwargs: Additional parameters for specific diagram types
            
        Returns:
            Path to the generated diagram file or embedded diagram
        """
        if not PYDOT_AVAILABLE and diagram_type not in [DiagramType.GANTT, DiagramType.MINDMAP]:
            self.logger.error("Pydot is required for diagram generation")
            return "ERROR: Pydot is required for diagram generation"
        
        try:
            # Process diagram based on type
            if diagram_type == DiagramType.FLOWCHART:
                return self._create_flowchart(df, title, file_name, **kwargs)
            elif diagram_type == DiagramType.SEQUENCE:
                return self._create_sequence_diagram(df, title, file_name, **kwargs)
            elif diagram_type == DiagramType.GANTT:
                return self._create_gantt_chart(df, title, file_name, **kwargs)
            elif diagram_type == DiagramType.MINDMAP:
                return self._create_mindmap(df, title, file_name, **kwargs)
            else:
                self.logger.warning(f"Diagram type {diagram_type} not yet implemented. Using flowchart instead.")
                return self._create_flowchart(df, title, file_name, **kwargs)
                
        except Exception as e:
            self.logger.error(f"Error creating diagram: {e}")
            return f"ERROR: {str(e)}"
    
    def _create_flowchart(self,
                         df: 'pd.DataFrame',
                         title: str,
                         file_name: str,
                         **kwargs) -> str:
        """
        Create a flowchart diagram.
        
        Args:
            df: DataFrame with columns: 'id', 'label', 'shape', 'next_ids'
            title: Diagram title
            file_name: Name for the output file
            
        Returns:
            Path to the generated diagram file or embedded diagram
        """
        if not PYDOT_AVAILABLE:
            return "ERROR: Pydot is required for flowchart generation"
            
        try:
            # Create graph
            graph = pydot.Dot(graph_type='digraph', rankdir=kwargs.get('direction', 'TB'))
            graph.set_label(title)
            graph.set_fontsize(str(self.config.title_font_size))
            
            # Check required columns
            required_columns = ['id', 'label']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in data")
            
            # Create nodes
            nodes = {}
            for _, row in df.iterrows():
                node_id = str(row['id'])
                label = str(row['label'])
                shape = str(row.get('shape', 'box'))
                
                # Create node
                node = pydot.Node(node_id, label=label, shape=shape)
                
                # Apply styling based on shape
                if shape == 'decision':
                    node.set_shape('diamond')
                elif shape == 'start' or shape == 'end':
                    node.set_shape('oval')
                
                # Add custom styling
                if 'style' in row:
                    node.set_style(row['style'])
                if 'color' in row:
                    node.set_color(row['color'])
                if 'fillcolor' in row:
                    node.set_fillcolor(row['fillcolor'])
                    node.set_style('filled')
                
                graph.add_node(node)
                nodes[node_id] = node
            
            # Create edges
            if 'next_ids' in df.columns:
                for _, row in df.iterrows():
                    source_id = str(row['id'])
                    
                    # Handle different formats for next_ids
                    next_ids = row['next_ids']
                    if isinstance(next_ids, str):
                        # Comma-separated string
                        next_ids = [nid.strip() for nid in next_ids.split(',') if nid.strip()]
                    elif isinstance(next_ids, list):
                        # Already a list
                        next_ids = [str(nid) for nid in next_ids if nid]
                    else:
                        # Single value or None
                        next_ids = [str(next_ids)] if next_ids else []
                    
                    for target_id in next_ids:
                        if target_id in nodes:
                            # Create edge
                            edge = pydot.Edge(source_id, target_id)
                            
                            # Add label if available
                            if 'edge_labels' in df.columns:
                                edge_label = row.get('edge_labels', {}).get(target_id)
                                if edge_label:
                                    edge.set_label(str(edge_label))
                            
                            graph.add_edge(edge)
            
            # Save to file and return
            output_path = os.path.join(self.config.output_dir, f"{file_name}.{self.config.format.name.lower()}")
            graph.write(output_path, format=self.config.format.name.lower())
            
            # Store the path for reference
            self.last_visualization_path = output_path
            
            # Return based on format
            if self.config.format == VisualizationFormat.MARKDOWN:
                return f"![{title}]({output_path})"
            elif self.config.format == VisualizationFormat.BASE64:
                return self._get_base64_image(output_path)
            else:
                return output_path
                
        except Exception as e:
            self.logger.error(f"Error creating flowchart: {e}")
            return f"ERROR: {str(e)}"
    
    def _create_sequence_diagram(self,
                               df: 'pd.DataFrame',
                               title: str,
                               file_name: str,
                               **kwargs) -> str:
        """
        Create a sequence diagram.
        
        Args:
            df: DataFrame with columns: 'source', 'target', 'message', 'order'
            title: Diagram title
            file_name: Name for the output file
            
        Returns:
            Path to the generated diagram file or embedded diagram
        """
        if not PYDOT_AVAILABLE:
            return "ERROR: Pydot is required for sequence diagram generation"
            
        try:
            # Create graph
            graph = pydot.Dot(graph_type='digraph', rankdir='LR')
            graph.set_label(title)
            graph.set_fontsize(str(self.config.title_font_size))
            
            # Check required columns
            required_columns = ['source', 'target', 'message']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in data")
            
            # Get unique participants
            participants = set(df['source'].tolist() + df['target'].tolist())
            
            # Create participant nodes
            for participant in participants:
                node = pydot.Node(
                    participant, 
                    label=participant,
                    shape='box',
                    style='filled',
                    fillcolor=kwargs.get('participant_color', '#E5E5E5')
                )
                graph.add_node(node)
            
            # Sort messages by order if available
            if 'order' in df.columns:
                df = df.sort_values('order')
            
            # Create edges for messages
            for _, row in df.iterrows():
                source = row['source']
                target = row['target']
                message = row['message']
                
                edge = pydot.Edge(
                    source, 
                    target,
                    label=message,
                    fontsize=str(self.config.label_font_size)
                )
                
                # Apply styling for async messages
                if 'async' in row and row['async']:
                    edge.set_style('dashed')
                
                # Apply styling for return messages
                if 'return' in row and row['return']:
                    edge.set_style('dashed')
                    edge.set_arrowhead('odot')
                
                graph.add_edge(edge)
            
            # Save to file and return
            output_path = os.path.join(self.config.output_dir, f"{file_name}.{self.config.format.name.lower()}")
            graph.write(output_path, format=self.config.format.name.lower())
            
            # Store the path for reference
            self.last_visualization_path = output_path
            
            # Return based on format
            if self.config.format == VisualizationFormat.MARKDOWN:
                return f"![{title}]({output_path})"
            elif self.config.format == VisualizationFormat.BASE64:
                return self._get_base64_image(output_path)
            else:
                return output_path
                
        except Exception as e:
            self.logger.error(f"Error creating sequence diagram: {e}")
            return f"ERROR: {str(e)}"
    
    def _create_gantt_chart(self,
                           df: 'pd.DataFrame',
                           title: str,
                           file_name: str,
                           **kwargs) -> str:
        """
        Create a Gantt chart.
        
        Args:
            df: DataFrame with columns: 'task', 'start', 'end', 'category'
            title: Chart title
            file_name: Name for the output file
            
        Returns:
            Path to the generated chart file or embedded chart
        """
        if not MATPLOTLIB_AVAILABLE:
            return "ERROR: Matplotlib is required for Gantt chart generation"
            
        try:
            # Check required columns
            required_columns = ['task', 'start', 'end']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in data")
            
            # Convert dates to datetime if they are strings
            if isinstance(df['start'].iloc[0], str):
                df['start'] = pd.to_datetime(df['start'])
            if isinstance(df['end'].iloc[0], str):
                df['end'] = pd.to_datetime(df['end'])
            
            # Calculate duration
            df['duration'] = df['end'] - df['start']
            df['duration_days'] = df['duration'].dt.days
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            
            # Set chart title
            ax.set_title(title, fontsize=self.config.title_font_size)
            
            # Determine colors based on categories
            if 'category' in df.columns:
                categories = df['category'].unique()
                colors = plt.cm.tab10(np.linspace(0, 1, len(categories)))
                category_color_map = dict(zip(categories, colors))
                bar_colors = [category_color_map[cat] for cat in df['category']]
            else:
                bar_colors = 'tab:blue'
            
            # Plot Gantt chart
            y_positions = range(len(df))
            bars = ax.barh(y_positions, df['duration_days'], left=self._datetime_to_float(df['start']), 
                          color=bar_colors, height=0.6)
            
            # Set y-axis labels (task names)
            ax.set_yticks(y_positions)
            ax.set_yticklabels(df['task'])
            
            # Format x-axis as dates
            ax.xaxis_date()
            plt.gcf().autofmt_xdate()
            
            # Add grid
            ax.grid(axis='x', alpha=0.3)
            
            # Add legend if using categories
            if 'category' in df.columns:
                from matplotlib.patches import Patch
                legend_elements = [Patch(facecolor=color, label=cat) 
                                 for cat, color in category_color_map.items()]
                ax.legend(handles=legend_elements, title='Categories')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save and return visualization
            return self._save_and_return_visualization(fig, file_name)
            
        except Exception as e:
            self.logger.error(f"Error creating Gantt chart: {e}")
            return f"ERROR: {str(e)}"
    
    def _datetime_to_float(self, dt_series):
        """Convert datetime series to float for plotting."""
        return [pd.Timestamp(dt).toordinal() for dt in dt_series]
    
    def _create_mindmap(self,
                       df: 'pd.DataFrame',
                       title: str,
                       file_name: str,
                       **kwargs) -> str:
        """
        Create a mind map visualization.
        
        Args:
            df: DataFrame with columns: 'id', 'parent_id', 'text', 'level'
            title: Mind map title
            file_name: Name for the output file
            
        Returns:
            Path to the generated mind map file or embedded mind map
        """
        if not NETWORKX_AVAILABLE:
            return "ERROR: NetworkX is required for mind map generation"
            
        try:
            # Check required columns
            required_columns = ['id', 'parent_id', 'text']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in data")
            
            # Create directed graph
            G = nx.DiGraph()
            
            # Add nodes
            for _, row in df.iterrows():
                node_id = row['id']
                text = row['text']
                
                # Add node attributes
                attrs = {'label': text}
                if 'level' in df.columns:
                    attrs['level'] = row['level']
                if 'color' in df.columns:
                    attrs['color'] = row['color']
                
                G.add_node(node_id, **attrs)
            
            # Add edges
            for _, row in df.iterrows():
                node_id = row['id']
                parent_id = row['parent_id']
                
                if parent_id and parent_id in G:
                    G.add_edge(parent_id, node_id)
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            
            # Calculate layout
            if kwargs.get('layout', 'radial') == 'radial':
                # Find root node (node with no incoming edges)
                root_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
                if not root_nodes:
                    # If no clear root, use node with lowest id
                    root_nodes = [min(G.nodes())]
                
                # Create radial layout
                pos = nx.spring_layout(G, scale=10)
            else:
                # Use hierarchical layout
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            
            # Determine node colors based on level
            if 'level' in df.columns:
                max_level = df['level'].max()
                cmap = plt.cm.viridis
                node_colors = [cmap(G.nodes[n].get('level', 1) / max_level) for n in G.nodes()]
            else:
                node_colors = 'skyblue'
            
            # Draw graph
            nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, 
                  node_size=1000, font_size=8, font_weight='bold',
                  arrows=False)
            
            # Set title
            ax.set_title(title, fontsize=self.config.title_font_size)
            
            # Remove axis
            ax.axis('off')
            
            # Save and return visualization
            return self._save_and_return_visualization(fig, file_name)
            
        except Exception as e:
            self.logger.error(f"Error creating mind map: {e}")
            return f"ERROR: {str(e)}"
    
    def _create_network(self,
                       df: 'pd.DataFrame',
                       title: str,
                       file_name: str,
                       **kwargs) -> str:
        """
        Create a network graph visualization.
        
        Args:
            df: DataFrame with columns: 'source', 'target', 'weight' (optional)
            title: Network graph title
            file_name: Name for the output file
            
        Returns:
            Path to the generated network graph file or embedded graph
        """
        if not NETWORKX_AVAILABLE:
            return "ERROR: NetworkX is required for network graph generation"
            
        try:
            # Check required columns
            required_columns = ['source', 'target']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in data")
            
            # Create graph (directed or undirected)
            if kwargs.get('directed', True):
                G = nx.DiGraph()
            else:
                G = nx.Graph()
            
            # Add edges with weights if available
            if 'weight' in df.columns:
                for _, row in df.iterrows():
                    G.add_edge(row['source'], row['target'], weight=row['weight'])
            else:
                for _, row in df.iterrows():
                    G.add_edge(row['source'], row['target'])
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
            
            # Calculate layout
            layout_type = kwargs.get('layout', 'spring')
            if layout_type == 'spring':
                pos = nx.spring_layout(G, seed=kwargs.get('seed', 42))
            elif layout_type == 'circular':
                pos = nx.circular_layout(G)
            elif layout_type == 'kamada_kawai':
                pos = nx.kamada_kawai_layout(G)
            elif layout_type == 'spectral':
                pos = nx.spectral_layout(G)
            else:
                pos = nx.spring_layout(G)
            
            # Calculate node sizes based on degree or centrality
            node_size_method = kwargs.get('node_size_method', 'degree')
            if node_size_method == 'degree':
                node_sizes = [300 * (1 + G.degree(n)) for n in G.nodes()]
            elif node_size_method == 'betweenness':
                betweenness = nx.betweenness_centrality(G)
                node_sizes = [1000 * (0.1 + betweenness[n]) for n in G.nodes()]
            elif node_size_method == 'eigen':
                try:
                    eigen = nx.eigenvector_centrality(G)
                    node_sizes = [1000 * (0.1 + eigen[n]) for n in G.nodes()]
                except:
                    # Fallback to degree if eigenvector centrality fails
                    node_sizes = [300 * (1 + G.degree(n)) for n in G.nodes()]
            else:
                node_sizes = kwargs.get('node_size', 300)
            
            # Get edge weights for width
            if 'weight' in df.columns:
                edge_weights = [G[u][v].get('weight', 1.0) for u, v in G.edges()]
                
                # Normalize edge weights for better visualization
                max_weight = max(edge_weights)
                edge_weights = [1 + 2 * (w / max_weight) for w in edge_weights]
            else:
                edge_weights = 1.0
            
            # Draw network graph
            nodes = nx.draw_networkx_nodes(G, pos, ax=ax, 
                                        node_size=node_sizes,
                                        node_color=kwargs.get('node_color', 'skyblue'),
                                        alpha=kwargs.get('node_alpha', 0.8))
            
            edges = nx.draw_networkx_edges(G, pos, ax=ax,
                                        width=edge_weights,
                                        edge_color=kwargs.get('edge_color', 'gray'),
                                        alpha=kwargs.get('edge_alpha', 0.5),
                                        arrows=kwargs.get('arrows', True) if kwargs.get('directed', True) else False,
                                        arrowsize=kwargs.get('arrowsize', 10))
            
            # Add labels if requested
            if kwargs.get('show_labels', True):
                labels = nx.draw_networkx_labels(G, pos, ax=ax,
                                               font_size=kwargs.get('label_font_size', 8),
                                               font_weight=kwargs.get('label_font_weight', 'normal'))
            
            # Add edge labels if requested and weight column exists
            if kwargs.get('show_edge_labels', False) and 'weight' in df.columns:
                edge_labels = {(row['source'], row['target']): f"{row['weight']:.2f}" 
                             for _, row in df.iterrows()}
                nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=edge_labels,
                                          font_size=kwargs.get('edge_label_font_size', 6))
            
            # Set title
            ax.set_title(title, fontsize=self.config.title_font_size)
            
            # Remove axis
            ax.axis('off')
            
            # Add colorbar for node sizes if requested
            if kwargs.get('show_size_legend', False) and node_size_method != 'fixed':
                sm = plt.cm.ScalarMappable(cmap=plt.cm.Blues, norm=plt.Normalize(vmin=0, vmax=max(node_sizes)))
                sm.set_array([])
                cbar = plt.colorbar(sm, ax=ax)
                cbar.set_label(f'Node {node_size_method.capitalize()}')
            
            # Save and return visualization
            return self._save_and_return_visualization(fig, file_name)
            
        except Exception as e:
            self.logger.error(f"Error creating network graph: {e}")
            return f"ERROR: {str(e)}"
    
    def _create_table(self,
                     df: 'pd.DataFrame',
                     title: str,
                     file_name: str,
                     **kwargs) -> str:
        """
        Create a formatted table visualization.
        
        Args:
            df: DataFrame with table data
            title: Table title
            file_name: Name for the output file
            
        Returns:
            Path to the generated table file or embedded table
        """
        try:
            if self.config.format == VisualizationFormat.HTML:
                # Generate HTML table
                html_table = df.to_html(index=kwargs.get('show_index', True),
                                      classes=kwargs.get('css_classes', 'table table-striped'),
                                      border=kwargs.get('border', 0))
                
                # Add title as caption
                if title:
                    html_table = f"<caption>{title}</caption>\n{html_table}"
                
                # Save HTML to file
                output_path = os.path.join(self.config.output_dir, f"{file_name}.html")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_table)
                
                return output_path
                
            elif self.config.format == VisualizationFormat.MARKDOWN:
                # Generate markdown table
                markdown_table = df.to_markdown(index=kwargs.get('show_index', True))
                
                # Add title as header
                if title:
                    markdown_table = f"### {title}\n\n{markdown_table}"
                
                # Save markdown to file
                output_path = os.path.join(self.config.output_dir, f"{file_name}.md")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_table)
                
                return markdown_table
                
            else:
                # Create a visual table using matplotlib
                fig, ax = plt.subplots(figsize=(self.config.width / 100, self.config.height / 100))
                
                # Hide axes
                ax.axis('tight')
                ax.axis('off')
                
                # Create table
                table = ax.table(cellText=df.values,
                               colLabels=df.columns,
                               loc='center',
                               cellLoc='center',
                               colColours=[kwargs.get('header_color', '#f2f2f2')] * len(df.columns))
                
                # Set title
                ax.set_title(title, fontsize=self.config.title_font_size)
                
                # Adjust table appearance
                table.auto_set_font_size(False)
                table.set_fontsize(kwargs.get('font_size', 9))
                
                # Set table scale
                table.scale(kwargs.get('scale', 1.2), kwargs.get('scale', 1.2))
                
                # Save and return visualization
                return self._save_and_return_visualization(fig, file_name)
                
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            return f"ERROR: {str(e)}"
    
    def _save_and_return_visualization(self, fig: 'plt.Figure', file_name: str) -> str:
        """
        Save the figure and return appropriate visualization representation.
        
        Args:
            fig: Matplotlib figure
            file_name: Name for the output file (without extension)
            
        Returns:
            Path, markdown, or base64 representation based on format
        """
        try:
            # Create output path
            output_path = os.path.join(self.config.output_dir, f"{file_name}.{self.config.format.name.lower()}")
            
            # Save figure
            fig.savefig(output_path, 
                       format=self.config.format.name.lower(),
                       dpi=self.config.dpi,
                       bbox_inches='tight')
            
            # Store the path for reference
            self.last_visualization_path = output_path
            
            # Close figure to free memory
            plt.close(fig)
            
            # Return based on format
            if self.config.format == VisualizationFormat.MARKDOWN:
                return f"![{file_name}]({output_path})"
            elif self.config.format == VisualizationFormat.BASE64:
                return self._get_base64_image(output_path)
            else:
                return output_path
                
        except Exception as e:
            self.logger.error(f"Error saving visualization: {e}")
            return f"ERROR: {str(e)}"
    
    def _get_base64_image(self, file_path: str) -> str:
        """
        Convert an image file to base64 encoding for embedding in HTML/markdown.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Base64-encoded image string
        """
        try:
            with open(file_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Get image format
            img_format = os.path.splitext(file_path)[1].lstrip('.').lower()
            if img_format == 'svg':
                return f"data:image/svg+xml;base64,{encoded}"
            else:
                return f"data:image/{img_format};base64,{encoded}"
                
        except Exception as e:
            self.logger.error(f"Error encoding image as base64: {e}")
            return f"ERROR: {str(e)}"
    
    def generate_chart_from_knowledge_graph(self,
                                          query: str,
                                          chart_type: Union[ChartType, str] = ChartType.NETWORK,
                                          title: str = "",
                                          file_name: Optional[str] = None,
                                          **kwargs) -> str:
        """
        Generate a visualization based on knowledge graph query results.
        
        Args:
            query: Cypher query for Neo4j knowledge graph
            chart_type: Type of chart to create
            title: Chart title
            file_name: Name for the output file
            **kwargs: Additional parameters for visualization
            
        Returns:
            Path to the generated visualization file or embedded visualization
        """
        if not self.knowledge_graph_adapter:
            self.logger.error("Knowledge graph adapter is required for knowledge graph visualizations")
            return "ERROR: Knowledge graph adapter is required"
        
        try:
            # Execute query
            results = self.knowledge_graph_adapter.query(query)
            
            if not results:
                return "No data returned from knowledge graph query"
            
            # Convert to DataFrame
            if 'pd' not in globals():
                raise ImportError("Pandas is required for data processing")
                
            df = pd.DataFrame(results)
            
            # Generate appropriate visualization based on chart type
            if chart_type == ChartType.NETWORK or chart_type == "NETWORK":
                # Process results for network visualization
                network_data = self._prepare_network_data(df, **kwargs)
                return self.create_visualization(
                    data=network_data,
                    vis_type=VisualizationType.NETWORK,
                    title=title,
                    file_name=file_name,
                    **kwargs
                )
            else:
                # For other chart types, just use the data directly
                return self.create_visualization(
                    data=df,
                    vis_type=VisualizationType.CHART,
                    subtype=chart_type,
                    title=title,
                    file_name=file_name,
                    **kwargs
                )
                
        except Exception as e:
            self.logger.error(f"Error generating visualization from knowledge graph: {e}")
            return f"ERROR: {str(e)}"
    
    def _prepare_network_data(self, df: 'pd.DataFrame', **kwargs) -> 'pd.DataFrame':
        """
        Prepare network data from knowledge graph query results.
        
        Args:
            df: DataFrame from knowledge graph query
            **kwargs: Additional parameters for preparation
            
        Returns:
            DataFrame formatted for network visualization
        """
        # Check if data already has the right format
        if 'source' in df.columns and 'target' in df.columns:
            return df
        
        # Try to extract nodes and relationships from Neo4j results
        if 'n' in df.columns and 'r' in df.columns and 'm' in df.columns:
            # Results are likely (n)-[r]->(m) pattern
            network_data = []
            
            for _, row in df.iterrows():
                source_node = row['n']
                target_node = row['m']
                relationship = row['r']
                
                # Extract node identifiers
                source_id = source_node.get('id', source_node.get('name', str(id(source_node))))
                target_id = target_node.get('id', target_node.get('name', str(id(target_node))))
                
                # Extract relationship properties
                rel_type = relationship.get('type', 'related_to')
                weight = relationship.get('weight', 1.0)
                
                network_data.append({
                    'source': source_id,
                    'target': target_id,
                    'relationship': rel_type,
                    'weight': weight
                })
            
            return pd.DataFrame(network_data)
            
        else:
            # Try to infer the structure - this is a fallback
            self.logger.warning("Could not identify standard Neo4j pattern. Using first two columns as source and target.")
            
            if len(df.columns) < 2:
                raise ValueError("DataFrame must have at least 2 columns for network visualization")
                
            source_col = kwargs.get('source_column', df.columns[0])
            target_col = kwargs.get('target_column', df.columns[1])
            
            # Create network data
            network_data = df[[source_col, target_col]].copy()
            network_data.columns = ['source', 'target']
            
            # Add weight column if available
            if 'weight_column' in kwargs and kwargs['weight_column'] in df.columns:
                network_data['weight'] = df[kwargs['weight_column']]
            elif len(df.columns) > 2:
                # Try to use the third column as weight
                network_data['weight'] = df.iloc[:, 2]
            
            return network_data