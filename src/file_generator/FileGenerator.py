import os
import re
from xml.etree import ElementTree

# from xml.etree.ElementTree import ElementTree

from src.config import GENERATE_MODE, GENERATE_PATH, NODE_PATH
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
        self.generate_launch_file()

    def write_to_file(self, file_path, text):
        if GENERATE_MODE == "new":
            new_file_path = GENERATE_PATH + "/".join(NODE_PATH.split("/")[-2:]) + file_path.split(NODE_PATH)[-1]
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
                pattern = r"((this->)?declare_parameter(<(.+)>)?\((\s*\"(.+?)\"\s*(,\s*(.+)\s*)?)\);)"
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
                         f"          \"default\": \"{parameter.schema_value}\",\n"
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

    def generate_launch_file(self):
        for node in self.node_list:
            root = node.launch_xml_tree.getroot()
            old_arg_name = ""
            new_arg_name = node.node_name + "_param_file"
            new_arg_default = "$(find-pkg-share " + node.package_name + ")/config/" + node.node_name + ".param.yaml"
            for xml_arg in root.findall("arg"):
                arg_default = xml_arg.attrib.get("default")
                if f"$(find-pkg-share {node.package_name})/config" in arg_default:
                    old_arg_name = xml_arg.attrib.get("name")
                    root.remove(xml_arg)
                    break
            new_arg = ElementTree.Element("arg")
            new_arg.attrib["name"] = new_arg_name
            new_arg.attrib["default"] = new_arg_default
            root.insert(0, new_arg)

            xml_node = root.find("./node[@exec='" + node.exec_name + "']")
            for xml_param in xml_node.findall("param"):
                param_name = xml_param.attrib.get("name")
                if param_name in [parameter.param_name for parameter in node.parameter_list]:
                    xml_node.remove(xml_param)
                elif xml_param.attrib.get("from") == f"$(var {old_arg_name})":
                    xml_node.remove(xml_param)

            new_param = ElementTree.SubElement(xml_node, "param")
            new_param.attrib["from"] = f"$(var {new_arg_name})"

            launch_file_path = node.package_path + "launch/" + node.node_name + ".launch.xml"
            new_file_path = GENERATE_PATH + "/".join(NODE_PATH.split("/")[-2:]) + launch_file_path.split(NODE_PATH)[-1]
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
            ElementTree.indent(node.launch_xml_tree, space="\t", level=0)
            node.launch_xml_tree.write(new_file_path)

            # Insert one line "<?xml version="1.0" encoding="UTF-8"?>" at the beginning of the xml file
            with open(new_file_path, "r") as f:
                text = f.read()
                text = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + text
            self.write_to_file(launch_file_path, text)
