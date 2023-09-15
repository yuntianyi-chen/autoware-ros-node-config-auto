import re
from src.file_generator.Node import Node
from src.parameter.Parameter import Parameter
from src.refactoring_related_files.RelatedFiles import RelatedFiles
import xml.etree.ElementTree as ET


class FileParser:
    related_files: RelatedFiles
    node_list: list[Node]

    def __init__(self, related_files):
        self.related_files = related_files
        self.node_list = []

    def parameter_judging(self):
        for node in self.node_list:
            for parameter in node.parameter_list:
                parameter.judge_parameter()

    def parse_files(self):
        self.parse_cmake_file(self.related_files.get_cmake_file_list())
        self.parse_cpp_file(self.related_files.get_candidate_cpp_file_list())
        self.parse_readme_file(self.related_files.get_readme_file_list())
        # self.parse_param_file(self.related_files.get_param_file_list())
        self.parse_launch_file(self.related_files.get_launch_file_list())

    def parse_cmake_file(self, cmake_file_list):
        for cmake_file in cmake_file_list:
            with open(cmake_file, "r") as f:
                text = f.read()
                pattern = r"rclcpp_components_register_node\(\s*(\w+)\s*PLUGIN\s*\"(.+)\"\s*.*EXECUTABLE\s*(\w+)"
                match_list = re.findall(pattern, text)
                if match_list:
                    for match in match_list:
                        node_or_package_name = match[0]
                        plugin_name = match[1]
                        exec_name = match[2]
                        package_path = cmake_file.replace("CMakeLists.txt", "")
                        node = Node(node_or_package_name, plugin_name, exec_name, package_path)
                        self.node_list.append(node)
                else:
                    print(f"\nNo Separate Nodes in this package")

    def find_node_register(self, plugin_name, text):
        pattern = r"RCLCPP_COMPONENTS_REGISTER_NODE\(\s*" + plugin_name + "\s*\)"
        match = re.search(pattern, text)
        if match:
            return True
        else:
            return False

    def parse_cpp_file(self, cpp_file_list):
        for cpp_file in cpp_file_list:
            for node in self.node_list:
                with open(cpp_file, "r") as f:
                    text = f.read()
                    if self.find_node_register(node.plugin_name, text):
                        node.update_cpp_info(cpp_file)
                        pattern = r"((this->)?declare_parameter(<(.+)>)?\((\s*\"(.+?)\"\s*(,\s*(.+)\s*)?)\);)"
                        match_list = re.findall(pattern, text)
                        for match in match_list:
                            cpp_type = match[3]
                            param_name = match[5]
                            param_value = match[7]

                            parameter = Parameter(param_name)
                            parameter.set_cpp_type(cpp_type)
                            parameter.set_param_value(param_value)

                            node.add_parameter(parameter)
                        break

    def header_filter(self, header):
        header = [h.lower() for h in header]
        new_header = []
        for h in header:
            if "default" in h or "value" in h:
                h = "default"
            new_header.append(h)
        return new_header

    def parse_readme_file(self, readme_file_list):
        for readme_file in readme_file_list:
            param_data_list = []
            with open(readme_file, "r") as f:
                lines = f.readlines()
                pattern = r"\|.*\|\s*\n\s*"
                line_count = 0
                for line in lines:
                    param_data = {}
                    match = re.search(pattern, line)
                    if match:
                        if line_count == 0:
                            header = [t.strip() for t in line.split('|')[1:-1]]
                            new_header = self.header_filter(header)
                        elif line_count > 1:
                            values = [t.strip() for t in line.split('|')[1:-1]]
                            for col, value in zip(new_header, values):
                                filtered_value = value.replace("`", "")
                                param_data[col] = filtered_value
                            if "default" not in param_data:
                                param_data["default"] = ""
                            if "type" not in param_data:
                                param_data["type"] = ""
                            if "description" not in param_data:
                                param_data["description"] = ""
                            param_data_list.append(param_data)
                        line_count += 1
                    else:
                        line_count = 0

            for param_data in param_data_list:
                for node in self.node_list:
                    if node.has_parameter(param_data["name"]):
                        node.set_parameter_description(param_data["name"], param_data["description"])
                        node.update_parameter_value(param_data["name"], param_data["default"])
                        node.update_parameter_type(param_data["name"], param_data["type"])

    # def parse_param_file(self, param_file_list):
    #     # parse the param.yaml file as the example shows above
    #     for param_file in param_file_list:
    #         with open(param_file, "r") as f:
    #             lines = f.readlines()
    #             param_data_list =[]
    #             prefix = ""
    #             for line in lines[2:]:
    #                 if ":" in line:
    #                     param_name = line.split(":")[0].strip()
    #                     param_value = line.split(":")[1].strip()
    #                     if not param_value:
    #                         if prefix:
    #                             prefix += "." + param_name
    #                         else:
    #                             prefix = param_name
    #                     for node in self.node_list:
    #                         if node.has_parameter(param_name):
    #                             node.update_parameter_value(param_name, param_value)
    #                             break

    def parse_launch_file(self, launch_file_list):
        # parse launch.xml file
        for launch_file in launch_file_list:
            # Load and parse the XML file
            tree = ET.parse(launch_file)
            root = tree.getroot()
            for element in root.iter('node'):
                found = False
                for node in self.node_list:
                    if element.attrib.get('exec') == node.exec_name:
                        node.update_launch_file_info(launch_file)
                        node.update_launch_xml_tree(tree)
                        found = True
                        break
                if found:
                    break
