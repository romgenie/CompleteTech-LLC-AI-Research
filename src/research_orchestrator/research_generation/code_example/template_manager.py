"""
Template Manager for Code Example Generation.

This module provides functionality for managing code templates
for different programming languages and use cases.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union

from .code_example_generator import ProgrammingLanguage, CodeStyle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeTemplate:
    """
    Code template for generating code examples.
    
    Templates contain parameterized code snippets that can be filled
    with specific implementation details for different algorithms
    and techniques.
    """
    
    def __init__(self,
                name: str,
                description: str,
                language: ProgrammingLanguage,
                category: str,
                template_code: str,
                parameters: Optional[List[Dict[str, Any]]] = None,
                imports: Optional[List[str]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize code template.
        
        Args:
            name: Template name
            description: Description of the template
            language: Programming language for this template
            category: Category (algorithm type, data structure, etc.)
            template_code: Template code with placeholders
            parameters: Parameters for filling the template
            imports: Required imports/libraries
            metadata: Additional metadata for the template
        """
        self.name = name
        self.description = description
        self.language = language
        self.category = category
        self.template_code = template_code
        self.parameters = parameters or []
        self.imports = imports or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            "name": self.name,
            "description": self.description,
            "language": self.language.name,
            "category": self.category,
            "template_code": self.template_code,
            "parameters": self.parameters,
            "imports": self.imports,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeTemplate':
        """
        Create template from dictionary.
        
        Args:
            data: Dictionary representation of the template
            
        Returns:
            CodeTemplate instance
        """
        # Convert language string to enum
        language_str = data.get("language", "PYTHON")
        try:
            language = ProgrammingLanguage[language_str]
        except (KeyError, TypeError):
            language = ProgrammingLanguage.PYTHON
            logger.warning(f"Invalid language: {language_str}. Using Python instead.")
        
        return cls(
            name=data.get("name", "Unnamed Template"),
            description=data.get("description", ""),
            language=language,
            category=data.get("category", "General"),
            template_code=data.get("template_code", ""),
            parameters=data.get("parameters", []),
            imports=data.get("imports", []),
            metadata=data.get("metadata", {})
        )


class CodeTemplateManager:
    """
    Manager for code templates.
    
    Provides functionality for loading, saving, and retrieving
    templates for code example generation.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize template manager.
        
        Args:
            template_dir: Directory for template files (optional)
        """
        # Set template directory
        if template_dir:
            self.template_dir = template_dir
        else:
            self.template_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "templates",
                "code_templates"
            )
            
        # Create directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Initialize templates
        self.templates: Dict[str, CodeTemplate] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load templates
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load templates from files."""
        if not os.path.exists(self.template_dir):
            self.logger.warning(f"Template directory does not exist: {self.template_dir}")
            return
        
        # Load all JSON files in the template directory
        for filename in os.listdir(self.template_dir):
            if filename.endswith(".json"):
                try:
                    file_path = os.path.join(self.template_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        
                    template = CodeTemplate.from_dict(template_data)
                    self.templates[template.name] = template
                    
                except Exception as e:
                    self.logger.error(f"Error loading template {filename}: {e}")
        
        self.logger.info(f"Loaded {len(self.templates)} templates")
    
    def save_template(self, template: CodeTemplate) -> None:
        """
        Save template to file.
        
        Args:
            template: Template to save
        """
        # Generate filename from template name
        safe_name = "".join(c if c.isalnum() else "_" for c in template.name)
        filename = f"{safe_name}_{template.language.name.lower()}.json"
        file_path = os.path.join(self.template_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2)
            
            # Add to templates dictionary
            self.templates[template.name] = template
            
            self.logger.info(f"Saved template to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving template {template.name}: {e}")
    
    def get_template(self, 
                    name: Optional[str] = None,
                    language: Optional[ProgrammingLanguage] = None,
                    category: Optional[str] = None) -> Optional[CodeTemplate]:
        """
        Get a template by name, language, or category.
        
        Args:
            name: Template name (optional)
            language: Programming language (optional)
            category: Template category (optional)
            
        Returns:
            CodeTemplate if found, None otherwise
        """
        # If name is provided, try to get directly
        if name and name in self.templates:
            return self.templates[name]
        
        # Otherwise filter by language and category
        matching_templates = list(self.templates.values())
        
        if language:
            matching_templates = [t for t in matching_templates if t.language == language]
        
        if category:
            matching_templates = [t for t in matching_templates if t.category == category]
        
        # Return first match if any
        return matching_templates[0] if matching_templates else None
    
    def get_templates_by_language(self, language: ProgrammingLanguage) -> List[CodeTemplate]:
        """
        Get all templates for a specific language.
        
        Args:
            language: Programming language
            
        Returns:
            List of matching templates
        """
        return [t for t in self.templates.values() if t.language == language]
    
    def get_templates_by_category(self, category: str) -> List[CodeTemplate]:
        """
        Get all templates in a specific category.
        
        Args:
            category: Template category
            
        Returns:
            List of matching templates
        """
        return [t for t in self.templates.values() if t.category == category]
    
    def get_all_templates(self) -> List[CodeTemplate]:
        """
        Get all templates.
        
        Returns:
            List of all templates
        """
        return list(self.templates.values())
    
    def get_categories(self) -> List[str]:
        """
        Get all template categories.
        
        Returns:
            List of unique categories
        """
        return sorted(set(t.category for t in self.templates.values()))
    
    def create_default_templates(self) -> None:
        """Create default templates for common algorithms and data structures."""
        # Python templates
        self._create_python_templates()
        
        # JavaScript templates
        self._create_javascript_templates()
        
        # Java templates
        self._create_java_templates()
        
        # C++ templates
        self._create_cpp_templates()
        
        # R templates
        self._create_r_templates()
    
    def _create_python_templates(self) -> None:
        """Create default Python templates."""
        # Sorting algorithm template
        sorting_template = CodeTemplate(
            name="Python Sorting Algorithm",
            description="Template for implementing sorting algorithms in Python",
            language=ProgrammingLanguage.PYTHON,
            category="Sorting Algorithms",
            template_code="""def {algorithm_name}_sort(arr: list) -> list:
    \"\"\"
    {algorithm_description}
    
    Args:
        arr: List to sort
        
    Returns:
        Sorted list
    \"\"\"
    # Implementation of {algorithm_name} sort
    {implementation}
    
    return arr


# Example usage
if __name__ == "__main__":
    test_arr = [5, 2, 9, 1, 5, 6]
    sorted_arr = {algorithm_name}_sort(test_arr)
    print(f"Original array: {test_arr}")
    print(f"Sorted array: {sorted_arr}")
""",
            parameters=[
                {
                    "name": "algorithm_name",
                    "description": "Name of the sorting algorithm",
                    "type": "string"
                },
                {
                    "name": "algorithm_description",
                    "description": "Description of how the algorithm works",
                    "type": "string"
                },
                {
                    "name": "implementation",
                    "description": "Implementation code for the sorting algorithm",
                    "type": "string"
                }
            ],
            imports=["typing"]
        )
        self.save_template(sorting_template)
        
        # Machine learning model template
        ml_template = CodeTemplate(
            name="Python Machine Learning Model",
            description="Template for implementing a machine learning model in Python",
            language=ProgrammingLanguage.PYTHON,
            category="Machine Learning",
            template_code="""import numpy as np
from typing import Tuple, Optional, Any

class {model_name}:
    \"\"\"
    {model_description}
    \"\"\"
    
    def __init__(self, {init_parameters}):
        \"\"\"
        Initialize the model.
        
        Args:
            {init_param_descriptions}
        \"\"\"
        {init_implementation}
        
    def fit(self, X: np.ndarray, y: np.ndarray, {fit_parameters}) -> '{model_name}':
        \"\"\"
        Train the model.
        
        Args:
            X: Training data features
            y: Training data targets
            {fit_param_descriptions}
            
        Returns:
            Self (trained model)
        \"\"\"
        {fit_implementation}
        return self
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        \"\"\"
        Make predictions with the model.
        
        Args:
            X: Data features
            
        Returns:
            Predicted values
        \"\"\"
        {predict_implementation}


# Example usage
if __name__ == "__main__":
    # Generate sample data
    X = np.random.randn(100, 2)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    # Create and train model
    model = {model_name}({example_init_params})
    model.fit(X, y{example_fit_params})
    
    # Make predictions
    predictions = model.predict(X)
    accuracy = np.mean(predictions == y)
    print(f"Model accuracy: {accuracy:.2f}")
""",
            parameters=[
                {
                    "name": "model_name",
                    "description": "Name of the machine learning model",
                    "type": "string"
                },
                {
                    "name": "model_description",
                    "description": "Description of the model and how it works",
                    "type": "string"
                },
                {
                    "name": "init_parameters",
                    "description": "Parameters for the model constructor",
                    "type": "string"
                },
                {
                    "name": "init_param_descriptions",
                    "description": "Descriptions of constructor parameters",
                    "type": "string"
                },
                {
                    "name": "init_implementation",
                    "description": "Implementation code for the constructor",
                    "type": "string"
                },
                {
                    "name": "fit_parameters",
                    "description": "Additional parameters for the fit method",
                    "type": "string"
                },
                {
                    "name": "fit_param_descriptions",
                    "description": "Descriptions of fit method parameters",
                    "type": "string"
                },
                {
                    "name": "fit_implementation",
                    "description": "Implementation code for the fit method",
                    "type": "string"
                },
                {
                    "name": "predict_implementation",
                    "description": "Implementation code for the predict method",
                    "type": "string"
                },
                {
                    "name": "example_init_params",
                    "description": "Example values for constructor parameters",
                    "type": "string"
                },
                {
                    "name": "example_fit_params",
                    "description": "Example values for fit method parameters",
                    "type": "string"
                }
            ],
            imports=["numpy", "typing"]
        )
        self.save_template(ml_template)
        
        # Data structure template
        ds_template = CodeTemplate(
            name="Python Data Structure",
            description="Template for implementing a data structure in Python",
            language=ProgrammingLanguage.PYTHON,
            category="Data Structures",
            template_code="""from typing import Any, Optional, List, Iterator

class {data_structure_name}:
    \"\"\"
    {data_structure_description}
    \"\"\"
    
    def __init__(self):
        \"\"\"
        Initialize the data structure.
        \"\"\"
        {init_implementation}
        
    def {add_method_name}(self, value: Any) -> None:
        \"\"\"
        Add an element to the data structure.
        
        Args:
            value: Element to add
        \"\"\"
        {add_implementation}
        
    def {remove_method_name}(self, value: Any) -> bool:
        \"\"\"
        Remove an element from the data structure.
        
        Args:
            value: Element to remove
            
        Returns:
            True if element was removed, False otherwise
        \"\"\"
        {remove_implementation}
        
    def __len__(self) -> int:
        \"\"\"
        Get the number of elements in the data structure.
        
        Returns:
            Number of elements
        \"\"\"
        {len_implementation}
        
    def __iter__(self) -> Iterator[Any]:
        \"\"\"
        Get an iterator over the elements in the data structure.
        
        Returns:
            Iterator over elements
        \"\"\"
        {iter_implementation}
        
    def __str__(self) -> str:
        \"\"\"
        Get a string representation of the data structure.
        
        Returns:
            String representation
        \"\"\"
        {str_implementation}


# Example usage
if __name__ == "__main__":
    ds = {data_structure_name}()
    
    # Add elements
    for value in [1, 2, 3, 4, 5]:
        ds.{add_method_name}(value)
    
    print(f"Data structure: {ds}")
    print(f"Size: {len(ds)}")
    
    # Iterate over elements
    print("Elements:", end=" ")
    for value in ds:
        print(value, end=" ")
    print()
    
    # Remove an element
    ds.{remove_method_name}(3)
    print(f"After removing 3: {ds}")
""",
            parameters=[
                {
                    "name": "data_structure_name",
                    "description": "Name of the data structure",
                    "type": "string"
                },
                {
                    "name": "data_structure_description",
                    "description": "Description of the data structure and its properties",
                    "type": "string"
                },
                {
                    "name": "init_implementation",
                    "description": "Implementation code for the constructor",
                    "type": "string"
                },
                {
                    "name": "add_method_name",
                    "description": "Name of the method to add elements",
                    "type": "string"
                },
                {
                    "name": "add_implementation",
                    "description": "Implementation code for the add method",
                    "type": "string"
                },
                {
                    "name": "remove_method_name",
                    "description": "Name of the method to remove elements",
                    "type": "string"
                },
                {
                    "name": "remove_implementation",
                    "description": "Implementation code for the remove method",
                    "type": "string"
                },
                {
                    "name": "len_implementation",
                    "description": "Implementation code for the __len__ method",
                    "type": "string"
                },
                {
                    "name": "iter_implementation",
                    "description": "Implementation code for the __iter__ method",
                    "type": "string"
                },
                {
                    "name": "str_implementation",
                    "description": "Implementation code for the __str__ method",
                    "type": "string"
                }
            ],
            imports=["typing"]
        )
        self.save_template(ds_template)
    
    def _create_javascript_templates(self) -> None:
        """Create default JavaScript templates."""
        # Sorting algorithm template
        sorting_template = CodeTemplate(
            name="JavaScript Sorting Algorithm",
            description="Template for implementing sorting algorithms in JavaScript",
            language=ProgrammingLanguage.JAVASCRIPT,
            category="Sorting Algorithms",
            template_code="""/**
 * {algorithm_description}
 * 
 * @param {Array} arr - Array to sort
 * @returns {Array} - Sorted array
 */
function {algorithm_name}Sort(arr) {
  // Create a copy of the array to avoid modifying the original
  const result = [...arr];
  
  // Implementation of {algorithm_name} sort
  {implementation}
  
  return result;
}

// Example usage
const testArr = [5, 2, 9, 1, 5, 6];
const sortedArr = {algorithm_name}Sort(testArr);
console.log(`Original array: ${testArr}`);
console.log(`Sorted array: ${sortedArr}`);

export default {algorithm_name}Sort;
""",
            parameters=[
                {
                    "name": "algorithm_name",
                    "description": "Name of the sorting algorithm",
                    "type": "string"
                },
                {
                    "name": "algorithm_description",
                    "description": "Description of how the algorithm works",
                    "type": "string"
                },
                {
                    "name": "implementation",
                    "description": "Implementation code for the sorting algorithm",
                    "type": "string"
                }
            ],
            imports=[]
        )
        self.save_template(sorting_template)
        
        # Data structure template
        ds_template = CodeTemplate(
            name="JavaScript Data Structure",
            description="Template for implementing a data structure in JavaScript",
            language=ProgrammingLanguage.JAVASCRIPT,
            category="Data Structures",
            template_code="""/**
 * {data_structure_description}
 */
class {data_structure_name} {
  /**
   * Create a new {data_structure_name}
   */
  constructor() {
    {init_implementation}
  }
  
  /**
   * Add an element to the data structure
   * 
   * @param {*} value - Element to add
   */
  {add_method_name}(value) {
    {add_implementation}
  }
  
  /**
   * Remove an element from the data structure
   * 
   * @param {*} value - Element to remove
   * @returns {boolean} - True if element was removed, false otherwise
   */
  {remove_method_name}(value) {
    {remove_implementation}
  }
  
  /**
   * Get the number of elements in the data structure
   * 
   * @returns {number} - Number of elements
   */
  size() {
    {size_implementation}
  }
  
  /**
   * Check if the data structure is empty
   * 
   * @returns {boolean} - True if empty, false otherwise
   */
  isEmpty() {
    return this.size() === 0;
  }
  
  /**
   * Convert the data structure to an array
   * 
   * @returns {Array} - Array containing all elements
   */
  toArray() {
    {to_array_implementation}
  }
  
  /**
   * Get a string representation of the data structure
   * 
   * @returns {string} - String representation
   */
  toString() {
    {to_string_implementation}
  }
}

// Example usage
const ds = new {data_structure_name}();

// Add elements
[1, 2, 3, 4, 5].forEach(value => ds.{add_method_name}(value));

console.log(`Data structure: ${ds.toString()}`);
console.log(`Size: ${ds.size()}`);

// Convert to array and iterate
const elements = ds.toArray();
console.log('Elements:', elements.join(' '));

// Remove an element
ds.{remove_method_name}(3);
console.log(`After removing 3: ${ds.toString()}`);

export default {data_structure_name};
""",
            parameters=[
                {
                    "name": "data_structure_name",
                    "description": "Name of the data structure",
                    "type": "string"
                },
                {
                    "name": "data_structure_description",
                    "description": "Description of the data structure and its properties",
                    "type": "string"
                },
                {
                    "name": "init_implementation",
                    "description": "Implementation code for the constructor",
                    "type": "string"
                },
                {
                    "name": "add_method_name",
                    "description": "Name of the method to add elements",
                    "type": "string"
                },
                {
                    "name": "add_implementation",
                    "description": "Implementation code for the add method",
                    "type": "string"
                },
                {
                    "name": "remove_method_name",
                    "description": "Name of the method to remove elements",
                    "type": "string"
                },
                {
                    "name": "remove_implementation",
                    "description": "Implementation code for the remove method",
                    "type": "string"
                },
                {
                    "name": "size_implementation",
                    "description": "Implementation code for the size method",
                    "type": "string"
                },
                {
                    "name": "to_array_implementation",
                    "description": "Implementation code for the toArray method",
                    "type": "string"
                },
                {
                    "name": "to_string_implementation",
                    "description": "Implementation code for the toString method",
                    "type": "string"
                }
            ],
            imports=[]
        )
        self.save_template(ds_template)
    
    def _create_java_templates(self) -> None:
        """Create default Java templates."""
        # Algorithm template
        algorithm_template = CodeTemplate(
            name="Java Algorithm",
            description="Template for implementing algorithms in Java",
            language=ProgrammingLanguage.JAVA,
            category="Algorithms",
            template_code="""/**
 * {algorithm_description}
 */
public class {algorithm_name} {
    
    /**
     * Private constructor to prevent instantiation
     */
    private {algorithm_name}() {
        // Private constructor to prevent instantiation
    }
    
    /**
     * Main algorithm implementation
     * 
     * @param {input_param_name} {input_param_description}
     * @return {return_description}
     */
    public static {return_type} {method_name}({input_type} {input_param_name}) {
        // Implementation of the algorithm
        {implementation}
    }
    
    /**
     * Main method for demonstration
     * 
     * @param args command line arguments
     */
    public static void main(String[] args) {
        // Example usage
        {example_usage}
    }
}
""",
            parameters=[
                {
                    "name": "algorithm_name",
                    "description": "Name of the algorithm class",
                    "type": "string"
                },
                {
                    "name": "algorithm_description",
                    "description": "Description of how the algorithm works",
                    "type": "string"
                },
                {
                    "name": "method_name",
                    "description": "Name of the algorithm method",
                    "type": "string"
                },
                {
                    "name": "input_type",
                    "description": "Type of the input parameter",
                    "type": "string"
                },
                {
                    "name": "input_param_name",
                    "description": "Name of the input parameter",
                    "type": "string"
                },
                {
                    "name": "input_param_description",
                    "description": "Description of the input parameter",
                    "type": "string"
                },
                {
                    "name": "return_type",
                    "description": "Return type of the algorithm",
                    "type": "string"
                },
                {
                    "name": "return_description",
                    "description": "Description of the return value",
                    "type": "string"
                },
                {
                    "name": "implementation",
                    "description": "Implementation code for the algorithm",
                    "type": "string"
                },
                {
                    "name": "example_usage",
                    "description": "Example code for using the algorithm",
                    "type": "string"
                }
            ],
            imports=[]
        )
        self.save_template(algorithm_template)
        
        # Data structure template
        ds_template = CodeTemplate(
            name="Java Data Structure",
            description="Template for implementing a data structure in Java",
            language=ProgrammingLanguage.JAVA,
            category="Data Structures",
            template_code="""import java.util.Iterator;
import java.util.NoSuchElementException;

/**
 * {data_structure_description}
 * 
 * @param <T> the type of elements in this data structure
 */
public class {data_structure_name}<T> implements Iterable<T> {
    
    /**
     * {node_description}
     */
    private class Node {
        T data;
        Node next;
        
        Node(T data) {
            this.data = data;
            this.next = null;
        }
    }
    
    private Node head;
    private int size;
    
    /**
     * Constructs an empty {data_structure_name}
     */
    public {data_structure_name}() {
        {init_implementation}
    }
    
    /**
     * Adds an element to the data structure
     * 
     * @param value element to add
     */
    public void {add_method_name}(T value) {
        {add_implementation}
    }
    
    /**
     * Removes an element from the data structure
     * 
     * @param value element to remove
     * @return true if the element was removed, false otherwise
     */
    public boolean {remove_method_name}(T value) {
        {remove_implementation}
    }
    
    /**
     * Returns the number of elements in the data structure
     * 
     * @return the number of elements
     */
    public int size() {
        return size;
    }
    
    /**
     * Returns true if the data structure is empty
     * 
     * @return true if empty, false otherwise
     */
    public boolean isEmpty() {
        return size == 0;
    }
    
    /**
     * Returns an iterator over the elements in the data structure
     * 
     * @return an iterator
     */
    @Override
    public Iterator<T> iterator() {
        return new Iterator<T>() {
            private Node current = head;
            
            @Override
            public boolean hasNext() {
                return current != null;
            }
            
            @Override
            public T next() {
                if (!hasNext()) {
                    throw new NoSuchElementException();
                }
                T data = current.data;
                current = current.next;
                return data;
            }
        };
    }
    
    /**
     * Returns a string representation of the data structure
     * 
     * @return string representation
     */
    @Override
    public String toString() {
        {to_string_implementation}
    }
    
    /**
     * Main method for demonstration
     * 
     * @param args command line arguments
     */
    public static void main(String[] args) {
        // Example usage
        {data_structure_name}<Integer> ds = new {data_structure_name}<>();
        
        // Add elements
        for (int i = 1; i <= 5; i++) {
            ds.{add_method_name}(i);
        }
        
        System.out.println("Data structure: " + ds);
        System.out.println("Size: " + ds.size());
        
        // Iterate over elements
        System.out.print("Elements: ");
        for (Integer value : ds) {
            System.out.print(value + " ");
        }
        System.out.println();
        
        // Remove an element
        ds.{remove_method_name}(3);
        System.out.println("After removing 3: " + ds);
    }
}
""",
            parameters=[
                {
                    "name": "data_structure_name",
                    "description": "Name of the data structure",
                    "type": "string"
                },
                {
                    "name": "data_structure_description",
                    "description": "Description of the data structure and its properties",
                    "type": "string"
                },
                {
                    "name": "node_description",
                    "description": "Description of the Node class",
                    "type": "string"
                },
                {
                    "name": "init_implementation",
                    "description": "Implementation code for the constructor",
                    "type": "string"
                },
                {
                    "name": "add_method_name",
                    "description": "Name of the method to add elements",
                    "type": "string"
                },
                {
                    "name": "add_implementation",
                    "description": "Implementation code for the add method",
                    "type": "string"
                },
                {
                    "name": "remove_method_name",
                    "description": "Name of the method to remove elements",
                    "type": "string"
                },
                {
                    "name": "remove_implementation",
                    "description": "Implementation code for the remove method",
                    "type": "string"
                },
                {
                    "name": "to_string_implementation",
                    "description": "Implementation code for the toString method",
                    "type": "string"
                }
            ],
            imports=["java.util.Iterator", "java.util.NoSuchElementException"]
        )
        self.save_template(ds_template)
    
    def _create_cpp_templates(self) -> None:
        """Create default C++ templates."""
        # Algorithm template
        algorithm_template = CodeTemplate(
            name="C++ Algorithm",
            description="Template for implementing algorithms in C++",
            language=ProgrammingLanguage.CPP,
            category="Algorithms",
            template_code="""#include <iostream>
#include <vector>
#include <string>

/**
 * {algorithm_description}
 * 
 * @param {input_param_name} {input_param_description}
 * @return {return_description}
 */
{return_type} {algorithm_name}({input_type} {input_param_name}) {
    // Implementation of the algorithm
    {implementation}
}

/**
 * Main function for demonstration
 */
int main() {
    // Example usage
    {example_usage}
    
    return 0;
}
""",
            parameters=[
                {
                    "name": "algorithm_name",
                    "description": "Name of the algorithm",
                    "type": "string"
                },
                {
                    "name": "algorithm_description",
                    "description": "Description of how the algorithm works",
                    "type": "string"
                },
                {
                    "name": "input_type",
                    "description": "Type of the input parameter",
                    "type": "string"
                },
                {
                    "name": "input_param_name",
                    "description": "Name of the input parameter",
                    "type": "string"
                },
                {
                    "name": "input_param_description",
                    "description": "Description of the input parameter",
                    "type": "string"
                },
                {
                    "name": "return_type",
                    "description": "Return type of the algorithm",
                    "type": "string"
                },
                {
                    "name": "return_description",
                    "description": "Description of the return value",
                    "type": "string"
                },
                {
                    "name": "implementation",
                    "description": "Implementation code for the algorithm",
                    "type": "string"
                },
                {
                    "name": "example_usage",
                    "description": "Example code for using the algorithm",
                    "type": "string"
                }
            ],
            imports=["<iostream>", "<vector>", "<string>"]
        )
        self.save_template(algorithm_template)
        
        # Data structure template
        ds_template = CodeTemplate(
            name="C++ Data Structure",
            description="Template for implementing a data structure in C++",
            language=ProgrammingLanguage.CPP,
            category="Data Structures",
            template_code="""#include <iostream>
#include <string>
#include <sstream>
#include <stdexcept>

/**
 * {data_structure_description}
 * 
 * @tparam T the type of elements in this data structure
 */
template <typename T>
class {data_structure_name} {
private:
    /**
     * {node_description}
     */
    struct Node {
        T data;
        Node* next;
        
        Node(const T& data) : data(data), next(nullptr) {}
    };
    
    Node* head;
    int count;
    
public:
    /**
     * Constructs an empty {data_structure_name}
     */
    {data_structure_name}() {
        {init_implementation}
    }
    
    /**
     * Destructor
     */
    ~{data_structure_name}() {
        // Clean up allocated memory
        Node* current = head;
        while (current != nullptr) {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }
    
    /**
     * Adds an element to the data structure
     * 
     * @param value element to add
     */
    void {add_method_name}(const T& value) {
        {add_implementation}
    }
    
    /**
     * Removes an element from the data structure
     * 
     * @param value element to remove
     * @return true if the element was removed, false otherwise
     */
    bool {remove_method_name}(const T& value) {
        {remove_implementation}
    }
    
    /**
     * Returns the number of elements in the data structure
     * 
     * @return the number of elements
     */
    int size() const {
        return count;
    }
    
    /**
     * Returns true if the data structure is empty
     * 
     * @return true if empty, false otherwise
     */
    bool isEmpty() const {
        return count == 0;
    }
    
    /**
     * Returns a string representation of the data structure
     * 
     * @return string representation
     */
    std::string toString() const {
        {to_string_implementation}
    }
    
    // Iterator implementation
    class Iterator {
    private:
        Node* current;
        
    public:
        Iterator(Node* node) : current(node) {}
        
        T& operator*() {
            if (current == nullptr) {
                throw std::out_of_range("Iterator out of range");
            }
            return current->data;
        }
        
        Iterator& operator++() {
            if (current != nullptr) {
                current = current->next;
            }
            return *this;
        }
        
        bool operator!=(const Iterator& other) const {
            return current != other.current;
        }
    };
    
    Iterator begin() {
        return Iterator(head);
    }
    
    Iterator end() {
        return Iterator(nullptr);
    }
};

/**
 * Main function for demonstration
 */
int main() {
    // Example usage
    {data_structure_name}<int> ds;
    
    // Add elements
    for (int i = 1; i <= 5; i++) {
        ds.{add_method_name}(i);
    }
    
    std::cout << "Data structure: " << ds.toString() << std::endl;
    std::cout << "Size: " << ds.size() << std::endl;
    
    // Iterate over elements
    std::cout << "Elements: ";
    for (const auto& value : ds) {
        std::cout << value << " ";
    }
    std::cout << std::endl;
    
    // Remove an element
    ds.{remove_method_name}(3);
    std::cout << "After removing 3: " << ds.toString() << std::endl;
    
    return 0;
}
""",
            parameters=[
                {
                    "name": "data_structure_name",
                    "description": "Name of the data structure",
                    "type": "string"
                },
                {
                    "name": "data_structure_description",
                    "description": "Description of the data structure and its properties",
                    "type": "string"
                },
                {
                    "name": "node_description",
                    "description": "Description of the Node struct",
                    "type": "string"
                },
                {
                    "name": "init_implementation",
                    "description": "Implementation code for the constructor",
                    "type": "string"
                },
                {
                    "name": "add_method_name",
                    "description": "Name of the method to add elements",
                    "type": "string"
                },
                {
                    "name": "add_implementation",
                    "description": "Implementation code for the add method",
                    "type": "string"
                },
                {
                    "name": "remove_method_name",
                    "description": "Name of the method to remove elements",
                    "type": "string"
                },
                {
                    "name": "remove_implementation",
                    "description": "Implementation code for the remove method",
                    "type": "string"
                },
                {
                    "name": "to_string_implementation",
                    "description": "Implementation code for the toString method",
                    "type": "string"
                }
            ],
            imports=["<iostream>", "<string>", "<sstream>", "<stdexcept>"]
        )
        self.save_template(ds_template)
    
    def _create_r_templates(self) -> None:
        """Create default R templates."""
        # Statistical analysis template
        stats_template = CodeTemplate(
            name="R Statistical Analysis",
            description="Template for implementing statistical analysis in R",
            language=ProgrammingLanguage.R,
            category="Statistical Analysis",
            template_code="""#' {analysis_description}
#'
#' @param {data_param_name} {data_param_description}
#' @param {options_param_name} {options_param_description}
#' @return {return_description}
#' @export
{function_name} <- function({data_param_name}, {options_param_name} = list()) {
  # Validate inputs
  if (!is.data.frame({data_param_name})) {
    stop("{data_param_name} must be a data frame")
  }
  
  # Implementation of the analysis
  {implementation}
  
  # Return results
  return(results)
}

# Example usage
# Load example data
data(mtcars)

# Run analysis
results <- {function_name}(mtcars, list(
  {example_options}
))

# Print results
print(results)

# Plot results if applicable
if (!is.null(results$plot)) {
  print(results$plot)
}
""",
            parameters=[
                {
                    "name": "function_name",
                    "description": "Name of the analysis function",
                    "type": "string"
                },
                {
                    "name": "analysis_description",
                    "description": "Description of the statistical analysis",
                    "type": "string"
                },
                {
                    "name": "data_param_name",
                    "description": "Name of the data parameter",
                    "type": "string"
                },
                {
                    "name": "data_param_description",
                    "description": "Description of the data parameter",
                    "type": "string"
                },
                {
                    "name": "options_param_name",
                    "description": "Name of the options parameter",
                    "type": "string"
                },
                {
                    "name": "options_param_description",
                    "description": "Description of the options parameter",
                    "type": "string"
                },
                {
                    "name": "return_description",
                    "description": "Description of the return value",
                    "type": "string"
                },
                {
                    "name": "implementation",
                    "description": "Implementation code for the analysis",
                    "type": "string"
                },
                {
                    "name": "example_options",
                    "description": "Example options for the analysis",
                    "type": "string"
                }
            ],
            imports=[]
        )
        self.save_template(stats_template)
        
        # Data visualization template
        viz_template = CodeTemplate(
            name="R Data Visualization",
            description="Template for implementing data visualization in R",
            language=ProgrammingLanguage.R,
            category="Data Visualization",
            template_code="""#' {visualization_description}
#'
#' @param {data_param_name} {data_param_description}
#' @param {x_param_name} {x_param_description}
#' @param {y_param_name} {y_param_description}
#' @param {color_param_name} {color_param_description}
#' @param {title_param_name} {title_param_description}
#' @return {return_description}
#' @export
{function_name} <- function({data_param_name}, {x_param_name}, {y_param_name}, 
                            {color_param_name} = NULL, {title_param_name} = "Visualization") {
  # Validate inputs
  if (!is.data.frame({data_param_name})) {
    stop("{data_param_name} must be a data frame")
  }
  if (!({x_param_name} %in% names({data_param_name}))) {
    stop("{x_param_name} must be a column in {data_param_name}")
  }
  if (!({y_param_name} %in% names({data_param_name}))) {
    stop("{y_param_name} must be a column in {data_param_name}")
  }
  if (!is.null({color_param_name}) && !({color_param_name} %in% names({data_param_name}))) {
    stop("{color_param_name} must be a column in {data_param_name}")
  }
  
  # Create plot
  {implementation}
  
  # Return plot
  return(p)
}

# Example usage
# Load required libraries
library(ggplot2)

# Load example data
data(mtcars)

# Create visualization
p <- {function_name}(mtcars, "mpg", "hp", "cyl", "Car Mileage vs Horsepower")

# Display plot
print(p)
""",
            parameters=[
                {
                    "name": "function_name",
                    "description": "Name of the visualization function",
                    "type": "string"
                },
                {
                    "name": "visualization_description",
                    "description": "Description of the visualization",
                    "type": "string"
                },
                {
                    "name": "data_param_name",
                    "description": "Name of the data parameter",
                    "type": "string"
                },
                {
                    "name": "data_param_description",
                    "description": "Description of the data parameter",
                    "type": "string"
                },
                {
                    "name": "x_param_name",
                    "description": "Name of the x-axis parameter",
                    "type": "string"
                },
                {
                    "name": "x_param_description",
                    "description": "Description of the x-axis parameter",
                    "type": "string"
                },
                {
                    "name": "y_param_name",
                    "description": "Name of the y-axis parameter",
                    "type": "string"
                },
                {
                    "name": "y_param_description",
                    "description": "Description of the y-axis parameter",
                    "type": "string"
                },
                {
                    "name": "color_param_name",
                    "description": "Name of the color parameter",
                    "type": "string"
                },
                {
                    "name": "color_param_description",
                    "description": "Description of the color parameter",
                    "type": "string"
                },
                {
                    "name": "title_param_name",
                    "description": "Name of the title parameter",
                    "type": "string"
                },
                {
                    "name": "title_param_description",
                    "description": "Description of the title parameter",
                    "type": "string"
                },
                {
                    "name": "return_description",
                    "description": "Description of the return value",
                    "type": "string"
                },
                {
                    "name": "implementation",
                    "description": "Implementation code for the visualization",
                    "type": "string"
                }
            ],
            imports=["ggplot2"]
        )
        self.save_template(viz_template)