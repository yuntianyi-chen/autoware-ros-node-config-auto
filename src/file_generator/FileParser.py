import re
from src.file_generator.FileGroup import FileGroup
from src.parameter.Parameter import Parameter
from src.refactoring_related_files.RelatedFiles import RelatedFiles


class FileParser:
    related_files: RelatedFiles
    file_group_list: list[FileGroup]

    def __init__(self, related_files):
        self.related_files = related_files
        self.file_group_list = []

    def parameter_judging(self):
        for file_group in self.file_group_list:
            for parameter in file_group.parameter_list:
                parameter.judge_parameter()


    def parse_files(self):
        self.parse_cpp_file(self.related_files.get_candidate_cpp_file_list())
        self.parse_readme_file(self.related_files.get_readme_file_list())
        # self.parse_param_file(self.related_files.get_param_file_list()
        # self.parse_launch_file(self.related_files.get_launch_file_list())

    def parse_cpp_file(self, cpp_file_list):
        for cpp_file in cpp_file_list:
            file_group = FileGroup(cpp_file)
            self.file_group_list.append(file_group)
            with open(cpp_file, "r") as f:
                text = f.read()
                pattern = r"(this->)?declare_parameter(<(.+)>)?\((\s*\"(.+)\"\s*(,\s*(.+)\s*)?)\);"
                match_list = re.findall(pattern, text)
                if match_list:
                    print(f"\nMatch in {cpp_file}")
                    for match in match_list:
                        # print(f"\nMatch: {match}")
                        # for i in range(len(match)):
                        #     print(f"Group {i}: {match[i]}")
                        cpp_type = match[2]
                        param_name = match[4]
                        param_value = match[6]

                        parameter = Parameter(param_name)
                        parameter.set_cpp_type(cpp_type)
                        parameter.set_param_value(param_value)

                        parameter.print_parameter()

                        file_group.add_parameter(parameter)
                else:
                    print(f"\nNo match in {cpp_file}")

    def parse_readme_file(self, readme_file_list):
        for readme_file in readme_file_list:
            with open(readme_file, "r") as f:
                lines = f.readlines()
                until_parameters = False
                pattern = r"\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.*\S)?\s*\|(\s*(.*)\s*\|)?"
                for line in lines:
                    if until_parameters:
                        match = re.search(pattern, line)
                        if match:
                            groups = match.groups()
                            readme_param_name = groups[0]
                            readme_param_type = groups[1]
                            readme_param_description = groups[2]
                            readme_param_value = groups[4]
                            if readme_param_name and "`" in readme_param_name:
                                readme_param_name = readme_param_name.replace("`", "")
                            if readme_param_type and "`" in readme_param_type:
                                readme_param_type = readme_param_type.replace("`", "")
                            if readme_param_value:
                                if "`" in readme_param_value:
                                    readme_param_value = readme_param_value.replace("`", "")
                                if " " in readme_param_value:
                                    readme_param_value = readme_param_value.replace(" ", "")
                            for file_group in self.file_group_list:
                                if file_group.has_parameter(readme_param_name):
                                    file_group.set_parameter_description(readme_param_name, readme_param_description)
                                    file_group.update_parameter_value(readme_param_name, readme_param_value)
                                    file_group.update_parameter_type(readme_param_name, readme_param_type)
                    elif "## Parameters" in line:
                        until_parameters = True

    def parse_param_file(self):
        pass

    def parse_launch_file(self, launch_file_list):
        pass
