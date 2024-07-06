import os
import ast

# Constants
BASE_DIR = '.'  # Change to your base directory if needed
OUTPUT_FILE = 'DOCUMENTATION.md'

def extract_docstrings_and_code(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
        tree = ast.parse(content)
    
    docstrings = {}
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings[node.name] = docstring
    
    return docstrings, content

def generate_markdown(directory, files_info):
    directory_title = os.path.basename(directory).title()
    markdown_content = f"# Documentation for {directory_title}\n\n"
    
    for filename, (docstrings, code) in sorted(files_info.items()):
        filename_title = filename.title()
        markdown_content += f"## {filename_title}\n\n"
        markdown_content += "### Code\n\n"
        markdown_content += "```python\n"
        markdown_content += f"{code}\n"
        markdown_content += "```\n\n"
        
        for name, docstring in docstrings.items():
            markdown_content += f"### {name}\n\n"
            markdown_content += f"{docstring}\n\n"
    
    return markdown_content

def process_directory(directory, output_file):
    files_info = {}
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                docstrings, code = extract_docstrings_and_code(filepath)
                if docstrings:
                    relative_path = os.path.relpath(filepath, directory)
                    files_info[relative_path] = (docstrings, code)
    
    if files_info:
        markdown_content = generate_markdown(directory, files_info)
        with open(output_file, 'a') as md_file:
            md_file.write(markdown_content)
            md_file.write("\n\n")

def main():
    with open(OUTPUT_FILE, 'w') as md_file:
        md_file.write("# Project Documentation\n\n")
    
    for root, dirs, _ in os.walk(BASE_DIR):
        for dir in sorted(dirs):
            process_directory(os.path.join(root, dir), OUTPUT_FILE)

if __name__ == "__main__":
    main()
