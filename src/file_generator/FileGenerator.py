import os
import re
from src.config import GENERATE_MODE
from src.file_generator.FileGroup import FileGroup
from src.refactoring_related_files.RelatedFiles import RelatedFiles


class FileGenerator:
    related_files: RelatedFiles
    file_group_list: list[FileGroup]

    def __init__(self, related_files):
        self.related_files = related_files
        self.file_group_list = []


    def generate_files(self):
        # self.generate_cmake_file(self.related_files.get_cmake_file_list())
        self.generate_cpp_file(self.related_files.get_candidate_cpp_file_list())
        # self.generate_param_file()
        # self.generate_schema_file()
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

    def generate_cpp_file(self, cpp_file_list):
        for cpp_file in cpp_file_list:
            file_group = FileGroup(cpp_file)
            with open(cpp_file, "r") as f:
                text = f.read()
                pattern = r"(this->)?declare_parameter(<(.*)>)?\((\s*\"(\w+)\"\s*(,\s*(.*)\s*)?)\);"
                match_list = re.findall(pattern, text)
                for match in match_list:
                    for i in range(len(match)):
                        print(f"Group {i}: {match[i]}")


                    file_group.add_parameter(match)
                    # replaced_str = match.group(1)
                    # new_text = text.replace(replaced_str, "\n  .automatically_declare_parameters_from_overrides(true)\n", 1)
                else:
                    print(f"No match in {cpp_file}")
                    # new_text = text.join("\nament_auto_package(\n  INSTALL_TO_SHARE\n  launch\n  config\n)")
                # self.write_to_file(cpp_file, new_text)
                print()

    def generate_param_file(self):
        pass

    def generate_schema_file(self):
        pass

    def generate_launch_file(self, launch_file_list):
        pass