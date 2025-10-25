"""Sphinx extension to automatically generate tables from dataclass definitions.

This extension provides a directive to dynamically create documentation tables
from Python dataclasses, extracting field information and metadata.
"""

from dataclasses import fields
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
import sys
import os


class DataclassTableDirective(Directive):
    """Directive to generate a table from a dataclass.
    
    Usage:
        .. dataclass-table:: module.path.ClassName
    """
    
    required_arguments = 1  # The fully qualified class name
    optional_arguments = 0
    has_content = False
    
    def run(self):
        """Generate the table from the dataclass."""
        # Get the class reference from the argument
        class_path = self.arguments[0]
        
        # Import the class dynamically
        module_path, class_name = class_path.rsplit('.', 1)
        
        # Add the Python package path to sys.path if needed
        # Get the source directory from the document settings
        source_dir = os.path.dirname(self.state.document.current_source)
        package_dir = os.path.abspath(os.path.join(source_dir, '../../python'))
        if package_dir not in sys.path:
            sys.path.insert(0, package_dir)
        
        try:
            # Import just the module file directly, not through the package __init__
            # This avoids loading dependencies we might not need
            import importlib.util
            
            # Construct the file path
            module_file = module_path.replace('.', '/') + '.py'
            module_full_path = os.path.join(package_dir, module_file)
            
            # Load the module directly from file
            spec = importlib.util.spec_from_file_location(module_path, module_full_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module spec from {module_full_path}")
            
            module = importlib.util.module_from_spec(spec)
            # Execute the module
            spec.loader.exec_module(module)
            # Add to sys.modules only after successful execution
            sys.modules[module_path] = module
            
            dataclass_obj = getattr(module, class_name)
        except (ImportError, AttributeError, FileNotFoundError) as e:
            error = self.state_machine.reporter.error(
                f'Cannot import class {class_path}: {e}',
                nodes.literal_block('', ''),
                line=self.lineno
            )
            return [error]
        
        # Generate RST table content
        rst_content = self._generate_table(dataclass_obj)
        
        # Parse the RST content into nodes
        result = ViewList()
        for line in rst_content.split('\n'):
            result.append(line, '<dataclass-table>')
        
        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        
        return node.children
    
    def _generate_table(self, dataclass_obj):
        """Generate RST table markup from dataclass fields."""
        # Get all fields from the dataclass
        field_list = fields(dataclass_obj)
        
        # Build the table header
        lines = [
            ".. list-table::",
            "   :header-rows: 1",
            "   :widths: 20 10 15 15 40",
            "",
            "   * - Field Name",
            "     - Type",
            "     - Default Value",
            "     - Units",
            "     - Description",
        ]
        
        # Add rows for each field
        for field_obj in field_list:
            # Get field information
            field_name = field_obj.name
            field_type = self._format_type(field_obj.type)
            default_value = self._format_default(field_obj.default)
            units = self._get_units(field_obj)
            description = self._get_description(field_obj)
            
            # Add table row
            lines.extend([
                f"   * - ``{field_name}``",
                f"     - {field_type}",
                f"     - ``{default_value}``",
                f"     - {units}",
                f"     - {description}",
            ])
        
        return '\n'.join(lines)
    
    def _format_type(self, type_obj):
        """Format the type annotation for display."""
        if hasattr(type_obj, '__name__'):
            return f"``{type_obj.__name__}``"
        else:
            return f"``{str(type_obj)}``"
    
    def _format_default(self, default_value):
        """Format the default value for display."""
        # Handle enum values - extract the underlying value
        if hasattr(default_value, 'value'):
            default_value = default_value.value
        
        # Add quotes around string values
        if isinstance(default_value, str):
            return f'"{default_value}"'
        
        return str(default_value)
    
    def _get_units(self, field_obj):
        """Extract units from field metadata."""
        metadata = field_obj.metadata
        
        # Check for 'units' in metadata
        if 'units' in metadata:
            return metadata['units']
        
        # No units available
        return ""
    
    def _get_description(self, field_obj):
        """Extract description from field metadata."""
        metadata = field_obj.metadata
        
        # Check for 'desc' in metadata
        if 'desc' in metadata:
            return metadata['desc']
        
        # No description available
        return ""


def setup(app):
    """Register the extension with Sphinx."""
    app.add_directive('dataclass-table', DataclassTableDirective)
    
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
