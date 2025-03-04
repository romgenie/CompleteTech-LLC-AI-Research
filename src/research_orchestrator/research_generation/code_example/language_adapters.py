"""
Language Adapters for Code Example Generation.

This module provides adapters for different programming languages
to ensure proper formatting, syntax, and best practices.
"""

import logging
import re
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union, Set

from .code_example_generator import ProgrammingLanguage, CodeStyle, CodeExample

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LanguageAdapter(ABC):
    """
    Base class for language-specific adapters.
    
    Language adapters ensure that generated code follows best practices,
    proper syntax, and formatting for the specific language.
    """
    
    def __init__(self, style: CodeStyle = CodeStyle.STANDARD):
        """
        Initialize language adapter.
        
        Args:
            style: Code style to use for formatting
        """
        self.style = style
        self.logger = logging.getLogger(__name__)
    
    @property
    @abstractmethod
    def language(self) -> ProgrammingLanguage:
        """The programming language for this adapter."""
        pass
    
    @property
    def file_extension(self) -> str:
        """
        Get the file extension for this language.
        
        Returns:
            File extension with dot prefix
        """
        extensions = {
            ProgrammingLanguage.PYTHON: ".py",
            ProgrammingLanguage.JAVASCRIPT: ".js",
            ProgrammingLanguage.TYPESCRIPT: ".ts",
            ProgrammingLanguage.JAVA: ".java",
            ProgrammingLanguage.CSHARP: ".cs",
            ProgrammingLanguage.CPP: ".cpp",
            ProgrammingLanguage.C: ".c",
            ProgrammingLanguage.GO: ".go",
            ProgrammingLanguage.RUST: ".rs",
            ProgrammingLanguage.RUBY: ".rb",
            ProgrammingLanguage.PHP: ".php",
            ProgrammingLanguage.SWIFT: ".swift",
            ProgrammingLanguage.KOTLIN: ".kt",
            ProgrammingLanguage.R: ".R",
            ProgrammingLanguage.MATLAB: ".m",
            ProgrammingLanguage.SCALA: ".scala",
            ProgrammingLanguage.JULIA: ".jl",
            ProgrammingLanguage.SHELL: ".sh",
            ProgrammingLanguage.SQL: ".sql",
            ProgrammingLanguage.OTHER: ".txt"
        }
        return extensions.get(self.language, ".txt")
    
    @abstractmethod
    def format_code(self, code: str) -> str:
        """
        Format code according to language-specific standards.
        
        Args:
            code: Raw code to format
            
        Returns:
            Formatted code
        """
        pass
    
    @abstractmethod
    def generate_class_definition(self, 
                                 class_name: str, 
                                 attributes: List[Dict[str, str]], 
                                 methods: List[Dict[str, Any]]) -> str:
        """
        Generate a class definition in this language.
        
        Args:
            class_name: Name of the class
            attributes: List of attributes with name, type, and description
            methods: List of methods with name, parameters, return type, and description
            
        Returns:
            Class definition as a string
        """
        pass
    
    @abstractmethod
    def generate_function_definition(self,
                                    function_name: str,
                                    parameters: List[Dict[str, str]],
                                    return_type: str,
                                    description: str,
                                    code: str) -> str:
        """
        Generate a function definition in this language.
        
        Args:
            function_name: Name of the function
            parameters: List of parameters with name, type, and description
            return_type: Return type of the function
            description: Description of the function
            code: Function implementation
            
        Returns:
            Function definition as a string
        """
        pass
    
    def generate_imports(self, packages: List[str]) -> str:
        """
        Generate import statements for the required packages.
        
        Args:
            packages: List of package names to import
            
        Returns:
            Import statements as a string
        """
        # Default implementation (override in subclasses)
        return "\n".join([f"import {package}" for package in packages])
    
    def add_documentation(self, code: str, description: str) -> str:
        """
        Add documentation to code snippet.
        
        Args:
            code: Code to document
            description: Description to add
            
        Returns:
            Code with documentation added
        """
        # Default implementation (override in subclasses)
        lines = [f"# {line}" for line in description.strip().split('\n')]
        return "\n".join(lines) + "\n\n" + code
    
    def wrap_with_main(self, code: str) -> str:
        """
        Wrap code with a main function or entry point.
        
        Args:
            code: Code to wrap
            
        Returns:
            Code wrapped with main entry point
        """
        # Default implementation (override in subclasses)
        return code


class PythonAdapter(LanguageAdapter):
    """
    Python language adapter for code generation.
    """
    
    @property
    def language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.PYTHON
    
    def format_code(self, code: str) -> str:
        """Format Python code."""
        # Try to use autopep8 if available
        try:
            import autopep8
            return autopep8.fix_code(code)
        except ImportError:
            # Simple indentation fix if autopep8 is not available
            return code
    
    def generate_imports(self, packages: List[str]) -> str:
        """Generate Python import statements."""
        imports = []
        
        for package in packages:
            if '.' in package:
                # Handle module.submodule.class format
                parts = package.split('.')
                if len(parts) == 2:
                    imports.append(f"from {parts[0]} import {parts[1]}")
                else:
                    imports.append(f"import {package}")
            else:
                imports.append(f"import {package}")
        
        return "\n".join(imports)
    
    def generate_class_definition(self, 
                                 class_name: str, 
                                 attributes: List[Dict[str, str]], 
                                 methods: List[Dict[str, Any]]) -> str:
        """Generate Python class definition."""
        # Start with class docstring
        result = f"class {class_name}:\n"
        result += '    """\n'
        result += f"    {class_name} class for [description].\n"
        result += '    """\n\n'
        
        # Generate __init__ method
        result += "    def __init__(self"
        
        # Add parameters
        for attr in attributes:
            attr_name = attr["name"]
            attr_type = attr.get("type", "Any")
            
            # Add parameter with type hint
            result += f", {attr_name}: {attr_type}"
            
            # Add default value if provided
            if "default" in attr:
                result += f" = {attr['default']}"
        
        result += "):\n"
        
        # Add docstring for __init__
        result += '        """\n'
        result += f"        Initialize {class_name}.\n\n"
        
        # Add parameter descriptions
        for attr in attributes:
            result += f"        Args:\n            {attr['name']}: {attr.get('description', 'Description')}\n"
        
        result += '        """\n'
        
        # Initialize attributes
        for attr in attributes:
            result += f"        self.{attr['name']} = {attr['name']}\n"
        
        # Add other methods
        for method in methods:
            result += "\n"
            
            method_name = method["name"]
            params = method.get("parameters", [])
            return_type = method.get("return_type", "None")
            description = method.get("description", "Method description.")
            
            # Method signature with type hints
            result += f"    def {method_name}(self"
            
            # Add parameters
            for param in params:
                param_name = param["name"]
                param_type = param.get("type", "Any")
                
                # Add parameter with type hint
                result += f", {param_name}: {param_type}"
                
                # Add default value if provided
                if "default" in param:
                    result += f" = {param['default']}"
            
            # Add return type
            result += f") -> {return_type}:\n"
            
            # Add docstring
            result += '        """\n'
            result += f"        {description}\n\n"
            
            # Add parameter descriptions
            if params:
                result += "        Args:\n"
                for param in params:
                    result += f"            {param['name']}: {param.get('description', 'Parameter description')}\n"
                result += "\n"
            
            # Add return description if not None
            if return_type != "None":
                result += "        Returns:\n"
                result += f"            {method.get('return_description', 'Return value description')}\n"
            
            result += '        """\n'
            
            # Add method implementation (placeholder)
            result += "        # TODO: Implement method\n"
            result += "        pass\n"
        
        return result
    
    def generate_function_definition(self,
                                    function_name: str,
                                    parameters: List[Dict[str, str]],
                                    return_type: str,
                                    description: str,
                                    code: str) -> str:
        """Generate Python function definition."""
        # Function signature with type hints
        result = f"def {function_name}("
        
        # Add parameters
        param_strs = []
        for i, param in enumerate(parameters):
            param_name = param["name"]
            param_type = param.get("type", "Any")
            
            # Add parameter with type hint
            param_str = f"{param_name}: {param_type}"
            
            # Add default value if provided
            if "default" in param:
                param_str += f" = {param['default']}"
            
            param_strs.append(param_str)
        
        result += ", ".join(param_strs)
        
        # Add return type
        result += f") -> {return_type}:\n"
        
        # Add docstring
        result += '    """\n'
        result += f"    {description}\n\n"
        
        # Add parameter descriptions
        if parameters:
            result += "    Args:\n"
            for param in parameters:
                result += f"        {param['name']}: {param.get('description', 'Parameter description')}\n"
            result += "\n"
        
        # Add return description if not None
        if return_type != "None":
            result += "    Returns:\n"
            result += f"        {return_type}: Return value description\n"
        
        result += '    """\n'
        
        # Add function implementation
        indented_code = "\n".join(["    " + line for line in code.strip().split("\n")])
        result += indented_code + "\n"
        
        return result
    
    def add_documentation(self, code: str, description: str) -> str:
        """Add Python-style documentation to code."""
        # Convert description to docstring
        docstring = f'"""\n{description}\n"""\n\n'
        return docstring + code
    
    def wrap_with_main(self, code: str) -> str:
        """Wrap Python code with if __name__ == '__main__' block."""
        main_code = code.strip()
        return f"{main_code}\n\nif __name__ == '__main__':\n    # Example usage\n    pass\n"


class JavaScriptAdapter(LanguageAdapter):
    """
    JavaScript language adapter for code generation.
    """
    
    @property
    def language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.JAVASCRIPT
    
    def format_code(self, code: str) -> str:
        """Format JavaScript code."""
        # Simple formatting (indentation fix)
        return code
    
    def generate_imports(self, packages: List[str]) -> str:
        """Generate JavaScript import statements."""
        imports = []
        
        for package in packages:
            if package.startswith("@"):
                # Handle npm scoped packages
                imports.append(f"import {package.split('/')[-1]} from '{package}';")
            elif '/' in package:
                # Handle path-based imports
                module_name = package.split('/')[-1]
                imports.append(f"import {module_name} from '{package}';")
            else:
                # Handle simple imports
                imports.append(f"import {package} from '{package}';")
        
        return "\n".join(imports)
    
    def generate_class_definition(self, 
                                 class_name: str, 
                                 attributes: List[Dict[str, str]], 
                                 methods: List[Dict[str, Any]]) -> str:
        """Generate JavaScript class definition."""
        # Class definition
        result = f"/**\n * {class_name} class for [description].\n */\nclass {class_name} {{\n"
        
        # Constructor
        result += "  /**\n"
        result += "   * Create a new instance of " + class_name + "\n"
        
        # Add parameter descriptions
        for attr in attributes:
            param_type = attr.get("type", "")
            type_comment = f" {{{param_type}}}" if param_type else ""
            result += f"   * @param{type_comment} {attr['name']} {attr.get('description', '')}\n"
        
        result += "   */\n"
        result += "  constructor("
        
        # Constructor parameters
        param_list = [attr["name"] for attr in attributes]
        result += ", ".join(param_list)
        
        result += ") {\n"
        
        # Initialize properties
        for attr in attributes:
            result += f"    this.{attr['name']} = {attr['name']};\n"
        
        result += "  }\n\n"
        
        # Add methods
        for method in methods:
            method_name = method["name"]
            params = method.get("parameters", [])
            return_type = method.get("return_type", "")
            description = method.get("description", "Method description.")
            
            # Method JSDoc
            result += "  /**\n"
            result += f"   * {description}\n"
            
            # Add parameter descriptions
            for param in params:
                param_type = param.get("type", "")
                type_comment = f" {{{param_type}}}" if param_type else ""
                result += f"   * @param{type_comment} {param['name']} {param.get('description', '')}\n"
            
            # Add return description
            if return_type:
                result += f"   * @returns {{{return_type}}} Return value description\n"
            
            result += "   */\n"
            
            # Method signature
            result += f"  {method_name}("
            param_list = [param["name"] for param in params]
            result += ", ".join(param_list)
            result += ") {\n"
            
            # Method implementation
            result += "    // TODO: Implement method\n"
            result += "  }\n\n"
        
        # Close class
        result += "}\n\n"
        result += "export default " + class_name + ";\n"
        
        return result
    
    def generate_function_definition(self,
                                    function_name: str,
                                    parameters: List[Dict[str, str]],
                                    return_type: str,
                                    description: str,
                                    code: str) -> str:
        """Generate JavaScript function definition."""
        # Function JSDoc
        result = "/**\n"
        result += f" * {description}\n"
        
        # Add parameter descriptions
        for param in parameters:
            param_type = param.get("type", "")
            type_comment = f" {{{param_type}}}" if param_type else ""
            result += f" * @param{type_comment} {param['name']} {param.get('description', '')}\n"
        
        # Add return description
        if return_type:
            result += f" * @returns {{{return_type}}} Return value description\n"
        
        result += " */\n"
        
        # Function signature
        result += f"function {function_name}("
        param_list = [param["name"] for param in parameters]
        result += ", ".join(param_list)
        result += ") {\n"
        
        # Function implementation
        indented_code = "\n".join(["  " + line for line in code.strip().split("\n")])
        result += indented_code + "\n"
        
        result += "}\n\n"
        result += f"export default {function_name};\n"
        
        return result
    
    def add_documentation(self, code: str, description: str) -> str:
        """Add JavaScript-style documentation to code."""
        # Convert description to JSDoc
        jsdoc = "/**\n"
        for line in description.strip().split('\n'):
            jsdoc += f" * {line}\n"
        jsdoc += " */\n"
        return jsdoc + code
    
    def wrap_with_main(self, code: str) -> str:
        """Wrap JavaScript code with example usage."""
        main_code = code.strip()
        return f"{main_code}\n\n// Example usage\n// Add example code here\n"


class JavaAdapter(LanguageAdapter):
    """
    Java language adapter for code generation.
    """
    
    @property
    def language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.JAVA
    
    def format_code(self, code: str) -> str:
        """Format Java code."""
        # Simple formatting (indentation fix)
        return code
    
    def generate_imports(self, packages: List[str]) -> str:
        """Generate Java import statements."""
        imports = []
        
        for package in packages:
            imports.append(f"import {package};")
        
        return "\n".join(imports)
    
    def generate_class_definition(self, 
                                 class_name: str, 
                                 attributes: List[Dict[str, str]], 
                                 methods: List[Dict[str, Any]]) -> str:
        """Generate Java class definition."""
        # Class definition with Javadoc
        result = f"/**\n * {class_name} class for [description].\n */\npublic class {class_name} {{\n\n"
        
        # Declare attributes
        for attr in attributes:
            attr_name = attr["name"]
            attr_type = attr.get("type", "Object")
            description = attr.get("description", "")
            
            # Add Javadoc for attribute
            result += f"    /** {description} */\n"
            
            # Declare attribute
            result += f"    private {attr_type} {attr_name};\n\n"
        
        # Constructor
        result += "    /**\n"
        result += f"     * Create a new instance of {class_name}\n"
        
        # Add parameter descriptions
        for attr in attributes:
            result += f"     * @param {attr['name']} {attr.get('description', '')}\n"
        
        result += "     */\n"
        result += f"    public {class_name}("
        
        # Constructor parameters
        param_strs = []
        for attr in attributes:
            param_strs.append(f"{attr.get('type', 'Object')} {attr['name']}")
        
        result += ", ".join(param_strs)
        
        result += ") {\n"
        
        # Initialize attributes
        for attr in attributes:
            result += f"        this.{attr['name']} = {attr['name']};\n"
        
        result += "    }\n\n"
        
        # Generate getters and setters
        for attr in attributes:
            attr_name = attr["name"]
            attr_type = attr.get("type", "Object")
            capitalized_name = attr_name[0].upper() + attr_name[1:]
            
            # Getter
            result += f"    /**\n     * Get the {attr_name}\n     * @return the {attr_name}\n     */\n"
            result += f"    public {attr_type} get{capitalized_name}() {{\n"
            result += f"        return {attr_name};\n"
            result += "    }\n\n"
            
            # Setter
            result += f"    /**\n     * Set the {attr_name}\n     * @param {attr_name} the {attr_name} to set\n     */\n"
            result += f"    public void set{capitalized_name}({attr_type} {attr_name}) {{\n"
            result += f"        this.{attr_name} = {attr_name};\n"
            result += "    }\n\n"
        
        # Add other methods
        for method in methods:
            method_name = method["name"]
            params = method.get("parameters", [])
            return_type = method.get("return_type", "void")
            description = method.get("description", "Method description.")
            
            # Method Javadoc
            result += "    /**\n"
            result += f"     * {description}\n"
            
            # Add parameter descriptions
            for param in params:
                result += f"     * @param {param['name']} {param.get('description', '')}\n"
            
            # Add return description
            if return_type != "void":
                result += "     * @return Return value description\n"
            
            result += "     */\n"
            
            # Method signature
            result += f"    public {return_type} {method_name}("
            
            # Method parameters
            param_strs = []
            for param in params:
                param_strs.append(f"{param.get('type', 'Object')} {param['name']}")
            
            result += ", ".join(param_strs)
            
            result += ") {\n"
            
            # Method implementation
            if return_type != "void":
                result += f"        // TODO: Implement method\n"
                default_values = {
                    "int": "0",
                    "double": "0.0",
                    "float": "0.0f",
                    "long": "0L",
                    "boolean": "false",
                    "byte": "0",
                    "char": "'\\0'",
                    "short": "0"
                }
                default_value = default_values.get(return_type, "null")
                result += f"        return {default_value};\n"
            else:
                result += "        // TODO: Implement method\n"
            
            result += "    }\n\n"
        
        # Add main method if specified
        result += "    /**\n"
        result += "     * Main method for demonstration\n"
        result += "     * @param args command line arguments\n"
        result += "     */\n"
        result += "    public static void main(String[] args) {\n"
        result += "        // Example usage\n"
        result += "        System.out.println(\"Example usage\");\n"
        result += "    }\n"
        
        # Close class
        result += "}\n"
        
        return result
    
    def generate_function_definition(self,
                                    function_name: str,
                                    parameters: List[Dict[str, str]],
                                    return_type: str,
                                    description: str,
                                    code: str) -> str:
        """
        Generate Java method definition.
        
        Note: Java doesn't have standalone functions, so this creates a static method
        in a utility class.
        """
        class_name = function_name[0].upper() + function_name[1:] + "Util"
        
        # Create utility class with static method
        result = f"/**\n * Utility class for {function_name} operation.\n */\n"
        result += f"public class {class_name} {{\n\n"
        
        # Private constructor to prevent instantiation
        result += "    /**\n"
        result += "     * Private constructor to prevent instantiation\n"
        result += "     */\n"
        result += "    private " + class_name + "() {\n"
        result += "        // Private constructor to prevent instantiation\n"
        result += "    }\n\n"
        
        # Method Javadoc
        result += "    /**\n"
        result += f"     * {description}\n"
        
        # Add parameter descriptions
        for param in parameters:
            result += f"     * @param {param['name']} {param.get('description', '')}\n"
        
        # Add return description
        if return_type != "void":
            result += "     * @return Return value description\n"
        
        result += "     */\n"
        
        # Method signature
        result += f"    public static {return_type} {function_name}("
        
        # Method parameters
        param_strs = []
        for param in parameters:
            param_strs.append(f"{param.get('type', 'Object')} {param['name']}")
        
        result += ", ".join(param_strs)
        
        result += ") {\n"
        
        # Method implementation
        indented_code = "\n".join(["        " + line for line in code.strip().split("\n")])
        result += indented_code + "\n"
        
        result += "    }\n\n"
        
        # Add main method for demonstration
        result += "    /**\n"
        result += "     * Main method for demonstration\n"
        result += "     * @param args command line arguments\n"
        result += "     */\n"
        result += "    public static void main(String[] args) {\n"
        result += "        // Example usage\n"
        result += "        System.out.println(\"Example usage\");\n"
        result += "    }\n"
        
        # Close class
        result += "}\n"
        
        return result
    
    def add_documentation(self, code: str, description: str) -> str:
        """Add Java-style documentation to code."""
        # Convert description to Javadoc
        javadoc = "/**\n"
        for line in description.strip().split('\n'):
            javadoc += f" * {line}\n"
        javadoc += " */\n"
        return javadoc + code


class CppAdapter(LanguageAdapter):
    """
    C++ language adapter for code generation.
    """
    
    @property
    def language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.CPP
    
    def format_code(self, code: str) -> str:
        """Format C++ code."""
        # Simple formatting (indentation fix)
        return code
    
    def generate_imports(self, packages: List[str]) -> str:
        """Generate C++ include statements."""
        includes = []
        
        for package in packages:
            if package.startswith("<") and package.endswith(">"):
                # System header
                includes.append(f"#include {package}")
            elif package.startswith("\"") and package.endswith("\""):
                # Local header
                includes.append(f"#include {package}")
            elif '/' in package or '\\' in package:
                # Local header with path
                includes.append(f"#include \"{package}\"")
            else:
                # System header
                includes.append(f"#include <{package}>")
        
        return "\n".join(includes)
    
    def generate_class_definition(self, 
                                 class_name: str, 
                                 attributes: List[Dict[str, str]], 
                                 methods: List[Dict[str, Any]]) -> str:
        """Generate C++ class definition."""
        # Start with class docstring
        result = f"/**\n * {class_name} class for [description].\n */\nclass {class_name} {{\npublic:\n"
        
        # Constructor
        result += f"    /**\n"
        result += f"     * Create a new instance of {class_name}\n"
        
        # Add parameter descriptions
        for attr in attributes:
            result += f"     * @param {attr['name']} {attr.get('description', '')}\n"
        
        result += "     */\n"
        result += f"    {class_name}("
        
        # Constructor parameters
        param_strs = []
        for attr in attributes:
            param_strs.append(f"{attr.get('type', 'auto')} {attr['name']}")
        
        result += ", ".join(param_strs)
        
        result += ");\n\n"
        
        # Destructor
        result += f"    /**\n"
        result += f"     * Destructor for {class_name}\n"
        result += "     */\n"
        result += f"    ~{class_name}();\n\n"
        
        # Add methods (declarations)
        for method in methods:
            method_name = method["name"]
            params = method.get("parameters", [])
            return_type = method.get("return_type", "void")
            description = method.get("description", "Method description.")
            
            # Method documentation
            result += f"    /**\n"
            result += f"     * {description}\n"
            
            # Add parameter descriptions
            for param in params:
                result += f"     * @param {param['name']} {param.get('description', '')}\n"
            
            # Add return description
            if return_type != "void":
                result += "     * @return Return value description\n"
            
            result += "     */\n"
            
            # Method declaration
            result += f"    {return_type} {method_name}("
            
            # Method parameters
            param_strs = []
            for param in params:
                param_strs.append(f"{param.get('type', 'auto')} {param['name']}")
            
            result += ", ".join(param_strs)
            
            result += ");\n\n"
        
        # Private section for attributes
        result += "private:\n"
        
        # Declare attributes
        for attr in attributes:
            attr_name = attr["name"]
            attr_type = attr.get("type", "auto")
            description = attr.get("description", "")
            
            # Add documentation for attribute
            result += f"    /** {description} */\n"
            
            # Declare attribute
            result += f"    {attr_type} {attr_name};\n"
        
        # Close class declaration
        result += "};\n\n"
        
        # Constructor implementation
        result += f"/**\n * Constructor implementation for {class_name}\n */\n"
        result += f"{class_name}::{class_name}("
        
        # Constructor parameters
        param_strs = []
        for attr in attributes:
            param_strs.append(f"{attr.get('type', 'auto')} {attr['name']}")
        
        result += ", ".join(param_strs)
        
        result += ") {\n"
        
        # Initialize attributes
        for attr in attributes:
            result += f"    this->{attr['name']} = {attr['name']};\n"
        
        result += "}\n\n"
        
        # Destructor implementation
        result += f"/**\n * Destructor implementation for {class_name}\n */\n"
        result += f"{class_name}::~{class_name}() {{\n"
        result += "    // Cleanup code here\n"
        result += "}\n\n"
        
        # Method implementations
        for method in methods:
            method_name = method["name"]
            params = method.get("parameters", [])
            return_type = method.get("return_type", "void")
            
            # Method implementation
            result += f"/**\n * Implementation of {method_name}\n */\n"
            result += f"{return_type} {class_name}::{method_name}("
            
            # Method parameters
            param_strs = []
            for param in params:
                param_strs.append(f"{param.get('type', 'auto')} {param['name']}")
            
            result += ", ".join(param_strs)
            
            result += ") {\n"
            
            # Method body
            if return_type != "void":
                result += "    // TODO: Implement method\n"
                
                if return_type == "int":
                    result += "    return 0;\n"
                elif return_type == "double" or return_type == "float":
                    result += "    return 0.0;\n"
                elif return_type == "bool":
                    result += "    return false;\n"
                elif return_type == "std::string":
                    result += "    return \"\";\n"
                else:
                    result += f"    return {return_type}();\n"
            else:
                result += "    // TODO: Implement method\n"
            
            result += "}\n\n"
        
        # Add main function
        result += "/**\n * Main function for demonstration\n */\n"
        result += "int main() {\n"
        result += "    // Example usage\n"
        result += "    return 0;\n"
        result += "}\n"
        
        return result
    
    def generate_function_definition(self,
                                    function_name: str,
                                    parameters: List[Dict[str, str]],
                                    return_type: str,
                                    description: str,
                                    code: str) -> str:
        """Generate C++ function definition."""
        # Function documentation
        result = f"/**\n"
        result += f" * {description}\n"
        
        # Add parameter descriptions
        for param in parameters:
            result += f" * @param {param['name']} {param.get('description', '')}\n"
        
        # Add return description
        if return_type != "void":
            result += " * @return Return value description\n"
        
        result += " */\n"
        
        # Function declaration
        result += f"{return_type} {function_name}("
        
        # Function parameters
        param_strs = []
        for param in parameters:
            param_strs.append(f"{param.get('type', 'auto')} {param['name']}")
        
        result += ", ".join(param_strs)
        
        result += ") {\n"
        
        # Function implementation
        indented_code = "\n".join(["    " + line for line in code.strip().split("\n")])
        result += indented_code + "\n"
        
        result += "}\n\n"
        
        # Add main function
        result += "/**\n * Main function for demonstration\n */\n"
        result += "int main() {\n"
        result += "    // Example usage\n"
        result += "    return 0;\n"
        result += "}\n"
        
        return result
    
    def add_documentation(self, code: str, description: str) -> str:
        """Add C++-style documentation to code."""
        # Convert description to doxygen-style comment
        doc = "/**\n"
        for line in description.strip().split('\n'):
            doc += f" * {line}\n"
        doc += " */\n"
        return doc + code
    
    def wrap_with_main(self, code: str) -> str:
        """Wrap C++ code with a main function."""
        main_code = code.strip()
        return f"{main_code}\n\n/**\n * Main function for demonstration\n */\nint main() {{\n    // Example usage\n    return 0;\n}}\n"


class RAdapter(LanguageAdapter):
    """
    R language adapter for code generation.
    """
    
    @property
    def language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.R
    
    def format_code(self, code: str) -> str:
        """Format R code."""
        # Simple formatting
        return code
    
    def generate_imports(self, packages: List[str]) -> str:
        """Generate R library imports."""
        imports = []
        
        for package in packages:
            imports.append(f"library({package})")
        
        return "\n".join(imports)
    
    def generate_class_definition(self, 
                                 class_name: str, 
                                 attributes: List[Dict[str, str]], 
                                 methods: List[Dict[str, Any]]) -> str:
        """
        Generate R class definition.
        
        Note: This uses R's S3 class system, which is less formal than other OOP systems.
        """
        # Start with creator function
        result = f"#' Create a new {class_name} object\n"
        
        # Add parameter roxygen comments
        for attr in attributes:
            result += f"#' @param {attr['name']} {attr.get('description', '')}\n"
        
        result += f"#' @return A new {class_name} object\n"
        result += f"#' @export\n"
        result += f"{class_name} <- function("
        
        # Add parameters
        param_strs = []
        for attr in attributes:
            if "default" in attr:
                param_strs.append(f"{attr['name']} = {attr['default']}")
            else:
                param_strs.append(attr['name'])
        
        result += ", ".join(param_strs)
        
        result += ") {\n"
        
        # Create object
        result += "  # Create object\n"
        result += "  obj <- list(\n"
        
        # Initialize attributes
        attr_strs = []
        for attr in attributes:
            attr_strs.append(f"    {attr['name']} = {attr['name']}")
        
        result += ",\n".join(attr_strs)
        
        result += "\n  )\n\n"
        
        # Set class
        result += f"  # Set class\n"
        result += f"  class(obj) <- \"{class_name}\"\n"
        result += f"  return(obj)\n"
        result += f"}}\n\n"
        
        # Add print method
        result += f"#' Print a {class_name} object\n"
        result += f"#' @param x A {class_name} object\n"
        result += f"#' @param ... Additional arguments (not used)\n"
        result += f"#' @export\n"
        result += f"print.{class_name} <- function(x, ...) {{\n"
        result += f"  cat(\"{class_name} object:\\n\")\n"
        
        # Print attributes
        for attr in attributes:
            result += f"  cat(\"  {attr['name']}: \", x${attr['name']}, \"\\n\")\n"
        
        result += f"  invisible(x)\n"
        result += f"}}\n\n"
        
        # Add methods
        for method in methods:
            method_name = method["name"]
            params = method.get("parameters", [])
            description = method.get("description", "Method description")
            
            # Create method function
            result += f"#' {description}\n"
            result += f"#' @param obj A {class_name} object\n"
            
            # Add parameter roxygen comments
            for param in params:
                result += f"#' @param {param['name']} {param.get('description', '')}\n"
            
            result += f"#' @return {method.get('return_description', 'Result of the operation')}\n"
            result += f"#' @export\n"
            
            # Function declaration
            result += f"{method_name}.{class_name} <- function(obj"
            
            # Add parameters
            for param in params:
                if "default" in param:
                    result += f", {param['name']} = {param['default']}"
                else:
                    result += f", {param['name']}"
            
            result += ") {\n"
            
            # Function implementation
            result += "  # TODO: Implement method\n"
            
            # Return statement
            return_desc = method.get("return_type", "")
            if return_desc.lower() == "logical" or return_desc.lower() == "boolean":
                result += "  return(FALSE)\n"
            elif return_desc.lower() == "numeric" or return_desc.lower() == "double":
                result += "  return(0)\n"
            elif return_desc.lower() == "character" or return_desc.lower() == "string":
                result += "  return(\"\")\n"
            elif return_desc.lower() == "list":
                result += "  return(list())\n"
            else:
                result += "  return(NULL)\n"
            
            result += "}\n\n"
        
        # Add example usage
        result += "# Example usage\n"
        
        # Create example object
        result += f"example <- {class_name}("
        
        # Add example values
        example_strs = []
        for attr in attributes:
            if attr.get("type", "").lower() == "character" or attr.get("type", "").lower() == "string":
                example_strs.append(f"{attr['name']} = \"example\"")
            elif attr.get("type", "").lower() == "numeric" or attr.get("type", "").lower() == "double":
                example_strs.append(f"{attr['name']} = 1.0")
            elif attr.get("type", "").lower() == "integer":
                example_strs.append(f"{attr['name']} = 1L")
            elif attr.get("type", "").lower() == "logical" or attr.get("type", "").lower() == "boolean":
                example_strs.append(f"{attr['name']} = TRUE")
            elif attr.get("type", "").lower() == "list":
                example_strs.append(f"{attr['name']} = list()")
            else:
                example_strs.append(f"{attr['name']} = NULL")
        
        result += ", ".join(example_strs)
        
        result += ")\n"
        result += "print(example)\n"
        
        return result
    
    def generate_function_definition(self,
                                    function_name: str,
                                    parameters: List[Dict[str, str]],
                                    return_type: str,
                                    description: str,
                                    code: str) -> str:
        """Generate R function definition."""
        # Function documentation
        result = f"#' {description}\n"
        
        # Add parameter roxygen comments
        for param in parameters:
            result += f"#' @param {param['name']} {param.get('description', '')}\n"
        
        # Add return description
        result += f"#' @return {return_type} description\n"
        result += f"#' @export\n"
        
        # Function declaration
        result += f"{function_name} <- function("
        
        # Function parameters
        param_strs = []
        for param in parameters:
            if "default" in param:
                param_strs.append(f"{param['name']} = {param['default']}")
            else:
                param_strs.append(param['name'])
        
        result += ", ".join(param_strs)
        
        result += ") {\n"
        
        # Function implementation
        indented_code = "\n".join(["  " + line for line in code.strip().split("\n")])
        result += indented_code + "\n"
        
        result += "}\n\n"
        
        # Add example usage
        result += "# Example usage\n"
        result += f"# result <- {function_name}("
        
        # Add example parameter values
        example_strs = []
        for param in parameters:
            if param.get("type", "").lower() == "character" or param.get("type", "").lower() == "string":
                example_strs.append(f"{param['name']} = \"example\"")
            elif param.get("type", "").lower() == "numeric" or param.get("type", "").lower() == "double":
                example_strs.append(f"{param['name']} = 1.0")
            elif param.get("type", "").lower() == "integer":
                example_strs.append(f"{param['name']} = 1L")
            elif param.get("type", "").lower() == "logical" or param.get("type", "").lower() == "boolean":
                example_strs.append(f"{param['name']} = TRUE")
            elif param.get("type", "").lower() == "list":
                example_strs.append(f"{param['name']} = list()")
            else:
                example_strs.append(f"{param['name']} = NULL")
        
        result += ", ".join(example_strs)
        
        result += ")\n"
        
        return result
    
    def add_documentation(self, code: str, description: str) -> str:
        """Add R-style documentation to code."""
        # Convert description to roxygen comments
        doc = ""
        for line in description.strip().split('\n'):
            doc += f"#' {line}\n"
        return doc + "\n" + code