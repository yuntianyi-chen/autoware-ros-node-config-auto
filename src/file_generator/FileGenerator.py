import os
import re
from src.config import GENERATE_MODE
from src.file_generator.Node import Node
from src.refactoring_related_files.RelatedFiles import RelatedFiles


class FileGenerator:
    related_files: RelatedFiles
    node_list: list[Node]

    def __init__(self, related_files, node_list):
        self.related_files = related_files
        self.node_list = node_list

    def generate_files(self):
        self.generate_cmake_file(self.related_files.get_cmake_file_list())
        self.generate_cpp_file()
        self.generate_param_file()
        self.generate_schema_file()
        # self.generate_launch_file(self.related_files.get_launch_file_list())

    def write_to_file(self, file_path, text):
        if GENERATE_MODE == "new":
            new_file_path = file_path.replace("demo_nodes", "generated_nodes")
        elif GENERATE_MODE == "overwrite":
            new_file_path = file_path
        else:
            raise ValueError(f"Invalid GENERATE_MODE: {GENERATE_MODE}")
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        with open(new_file_path, "w") as f:
            f.write(text)

    def generate_cmake_file(self, cmake_file_list):
        for cmake_file in cmake_file_list:
            # Use regex to match the line containing "ament_auto_package" in the CMakeLists.txt file
            with open(cmake_file, "r") as f:
                text = f.read()
                pattern = r"ament_auto_package\(([\w\s]*)\)"
                match = re.search(pattern, text)
                if match:
                    replaced_str = match.group(1)
                    new_text = text.replace(replaced_str, "\n  INSTALL_TO_SHARE\n  launch\n  config\n", 1)
                else:
                    new_text = text.join("\nament_auto_package(\n  INSTALL_TO_SHARE\n  launch\n  config\n)")
            self.write_to_file(cmake_file, new_text)

    def generate_cpp_file(self):
        for node in self.node_list:
            with open(node.cpp_file, "r") as f:
                text = f.read()
                pattern = r"((this->)?declare_parameter(<(.+)>)?\((\s*\"(.+)\"\s*(,\s*(.+)\s*)?)\);)"
                match_list = re.findall(pattern, text)
                for match in match_list:
                    statement = match[0]
                    param_name = match[5]
                    for parameter in node.parameter_list:
                        if parameter.param_name == param_name:
                            new_statement = f"declare_parameter<{parameter.param_type}>(\"{param_name}\");"
                            text = text.replace(statement, new_statement)
            self.write_to_file(node.cpp_file, text)

    def generate_param_file(self):
        for node in self.node_list:
            text = "/**:\n  ros__parameters:\n"
            for parameter in node.parameter_list:
                text += f"    {parameter.param_name}: {parameter.param_value}\n"
            config_file_path = node.package_path + "config/" + node.node_name + ".param.yaml"
            self.write_to_file(config_file_path, text)

    def generate_schema_file(self):
        for node in self.node_list:
            node_name_split_list = [i.capitalize() for i in node.node_name.split("_")]
            json_title = " ".join(node_name_split_list)
            text = (f"{{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n" +
                    f"  \"title\": \"Parameters for {json_title}\",\n" +
                    f"  \"type\": \"object\",\n  \"definitions\": {{\n" +
                    f"    \"{node.node_name}\":" + " {\n" +
                    f"      \"type\": \"object\",\n      \"properties\": {{\n")
            for parameter in node.parameter_list:
                text += (f"        \"{parameter.param_name}\": {{\n"
                         f"          \"type\": \"{parameter.schema_type}\",\n"
                         f"          \"default\": \"{parameter.param_value}\",\n"
                         f"          \"description\": \"{parameter.param_description}\"\n        }},\n")
                if parameter == node.parameter_list[-1]:
                    text = text[:-2] + "\n"

            text += (f"      }},\n      \"required\": [\n")
            for parameter in node.parameter_list:
                text += f"        \"{parameter.param_name}\",\n"
                if parameter == node.parameter_list[-1]:
                    text = text[:-2] + "\n"
            text += (f"      ],\n      \"additionalProperties\": false\n    }}\n  }},\n" +
                     f"  \"properties\": {{\n    \"/**\": {{\n" +
                     f"      \"type\": \"object\",\n      \"properties\": {{\n" +
                     f"        \"ros__parameters\": {{\n" +
                     f"          \"$ref\": \"#/definitions/{node.node_name}\"\n" +
                     f"        }}\n      }},\n      \"required\": [\"ros__parameters\"],\n" +
                     f"      \"additionalProperties\": false\n    }}\n  }},\n" +
                     f"  \"required\": [\"/**\"],\n  \"additionalProperties\": false\n}}")
            schema_file_path = node.package_path + "schema/" + node.node_name + ".schema.json"
            self.write_to_file(schema_file_path, text)

    def generate_launch_file(self, launch_file_list):
        pass
