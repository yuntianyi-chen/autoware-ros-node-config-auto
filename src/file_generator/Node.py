from xml.etree.ElementTree import ElementTree
from src.parameter.Parameter import Parameter


class Node:
    node_name: str
    cpp_file: str
    launch_file: str
    cpp_file_name: str
    package_name: str
    package_path: str
    parameter_list: list[Parameter]
    launch_xml_tree: ElementTree

    def __init__(self, node_name, exec_name, package_path):
        self.node_name = node_name
        self.exec_name = exec_name
        self.package_path = package_path
        self.parameter_list = []
        self.package_name = package_path.split("/")[-2]

    def update_cpp_info(self, cpp_file):
        self.cpp_file = cpp_file
        self.cpp_file_name = cpp_file.split("/")[-1]

    def add_parameter(self, parameter):
        self.parameter_list.append(parameter)

    def has_parameter(self, param_name):
        for parameter in self.parameter_list:
            if parameter.param_name == param_name:
                return True

    def set_parameter_description(self, readme_param_name, readme_param_description):
        for parameter in self.parameter_list:
            if parameter.param_name == readme_param_name:
                parameter.set_param_description(readme_param_description)

    def update_parameter_value(self, readme_param_name, readme_param_value):
        for parameter in self.parameter_list:
            if parameter.param_name == readme_param_name and not parameter.param_value:
                parameter.set_param_value(readme_param_value)

    def update_parameter_type(self, readme_param_name, readme_param_type):
        for parameter in self.parameter_list:
            if parameter.param_name == readme_param_name and not parameter.cpp_type:
                parameter.set_cpp_type(readme_param_type)

    def update_launch_file_info(self, launch_file):
        self.launch_file = launch_file

    def update_launch_xml_tree(self, launch_xml_tree):
        self.launch_xml_tree = launch_xml_tree