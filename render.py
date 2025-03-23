#!/usr/bin/env python3

import yaml
import jinja2
import os

def load_yaml(file_path):
    """Load YAML file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def render_template(template_path, output_path, data):
    """Render the template with the provided data and save to output file."""
    # Create a Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(template_path))
    )
    
    # Load the template
    template = env.get_template(os.path.basename(template_path))
    
    # Render the template with the data
    rendered = template.render(site={'pdfs': data})
    
    # Write the rendered content to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered)

def main():
    # Define paths
    template_path = 'index.template.html'
    yaml_path = 'pdfs.yml'
    output_path = 'index.html'
    
    # Load the PDF data
    pdfs_data = load_yaml(yaml_path)
    
    # Render the template
    render_template(template_path, output_path, pdfs_data)
    
    print(f"Successfully rendered {template_path} to {output_path}")

if __name__ == '__main__':
    main() 