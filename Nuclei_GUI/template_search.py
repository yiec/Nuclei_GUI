# template_search.py
import os
import yaml
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter

TEMPLATE_FOLDER = "/home/user/nuclei-templates/"  # 设置nuclei模板默认路径

def search_templates(search_term, template_folder):
    results = []
    for root, _, files in os.walk(template_folder):
        for file in files:
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if search_term.lower() in content.lower():
                            results.append(file_path)
                except UnicodeDecodeError:
                    print(f"Warning: Could not decode file {file_path} with UTF-8. Skipping this file.")
    return results

def display_results(results):
    return results

def write_results_to_file(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for file_path in results:
            f.write(file_path + "\n")

def read_template_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        template_content = f.read()
        yaml_content = yaml.safe_load(template_content)
        formatted_yaml = highlight(
            yaml.dump(yaml_content, default_flow_style=False),
            YamlLexer(),
            TerminalFormatter(),
        )
        return formatted_yaml