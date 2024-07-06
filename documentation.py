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
    new_content_lines = content.splitlines()
    new_content_lines_copy = new_content_lines[:]

    # Extract file-level docstring if present
    file_docstring = ast.get_docstring(tree)
    if file_docstring:
        file_docstring_node = tree.body[0]
        start, end = file_docstring_node.lineno - 1, file_docstring_node.end_lineno
        for i in range(start, end):
            new_content_lines_copy[i] = ''

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings[node.name] = docstring
                start, end = node.body[0].lineno - 1, node.body[0].end_lineno
                for i in range(start, end):
                    new_content_lines_copy[i] = ''
    
    new_content = "\n".join(new_content_lines_copy)
    return file_docstring, docstrings, new_content

def generate_markdown(directory, files_info):
    """
    Generates Markdown documentation for the given directory and files information.

    Args:
    - directory (str): Directory path being processed.
    - files_info (dict): Dictionary mapping file names to their docstrings and code.

    Returns:
    - markdown_content (str): Generated Markdown content.
    """
    directory_title = os.path.basename(directory).replace('_', ' ').title()
    markdown_content = f"# Documentation for {directory_title}\n\n"

    for filename, (file_docstring, docstrings, code) in sorted(files_info.items()):
        filename_title = filename.replace('_', ' ').title()
        markdown_content += f"## {filename_title}\n\n"

        if file_docstring:
            markdown_content += "### Script Description\n\n"
            markdown_content += f"{file_docstring}\n\n"

        if docstrings:
            for name, docstring in docstrings.items():
                markdown_content += f"### {name}\n\n"
                markdown_content += "#### Description\n\n"
                markdown_content += f"{docstring}\n\n"

                function_code = get_function_code(code, name)
                markdown_content += "#### Code\n\n"
                markdown_content += "```python\n"
                markdown_content += f"{function_code}\n"
                markdown_content += "```\n\n"
        else:
            markdown_content += "### No Functions or Classes Found\n\n"

    markdown_content += "## Overall Script\n\n"
    overall_script_code = remove_docstrings_and_linebreaks(files_info)
    markdown_content += "```python\n"
    markdown_content += f"{overall_script_code}\n"
    markdown_content += "```\n"

    return markdown_content

def get_function_code(code, function_name):
    lines = code.splitlines()
    function_code = []
    in_function = False
    indentation = None
    
    for line in lines:
        if line.strip().startswith(f"def {function_name}") or line.strip().startswith(f"class {function_name}"):
            in_function = True
            indentation = len(line) - len(line.lstrip())
        
        if in_function:
            current_indentation = len(line) - len(line.lstrip())
            if current_indentation < indentation:
                break
            function_code.append(line)
    
    return "\n".join(function_code)

def remove_docstrings_and_linebreaks(files_info):
    overall_script = []
    for filename, (_, _, code) in sorted(files_info.items()):
        lines = code.splitlines()
        inside_docstring = False
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                inside_docstring = not inside_docstring
                continue
            if not inside_docstring and stripped_line:
                overall_script.append(line)
        overall_script.append("")  # Adding empty line after each file's content

    return "\n".join(overall_script)

def process_directory(directory, output_file):
    files_info = {}
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                file_docstring, docstrings, code = extract_docstrings_and_code(filepath)
                if docstrings or file_docstring:
                    relative_path = os.path.relpath(filepath, directory)
                    files_info[relative_path] = (file_docstring, docstrings, code)
    
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
