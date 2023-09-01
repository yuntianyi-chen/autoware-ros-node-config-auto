from pathlib import Path


class RelatedFiles:
    def __init__(self, dir_path):
        self.dir_path = dir_path

        self.cpp_file_list = []
        self.launch_file_list = []
        self.param_file_list = []
        self.schema_file_list = []
        self.cmake_file_list = []
        self.readme_file_list = []

        self.candidate_cpp_file_list = []

    def get_related_files(self):
        all_files_list = self.get_all_files_from_dir(self.dir_path)
        for file_path in all_files_list:
            self.check_for_candidate(str(file_path))

        if self.has_cpp_file():
            for cpp_file in self.cpp_file_list:
                if self.check_for_candidate_cpp_file(cpp_file):
                    self.candidate_cpp_file_list.append(cpp_file)
            if self.has_candidate_cpp_file():
                print(f".cpp files below contain the 'declare_parameter' function:")
                for cpp_file in self.candidate_cpp_file_list:
                    file_name = cpp_file.split("/")[-1]
                    print(f"    {file_name}")
            else:
                print("No .cpp files contain the 'declare_parameter' function!")
        else:
            print("No .cpp files found!")

        return self

    def has_cpp_file(self):
        if self.cpp_file_list:
            return True
        else:
            return False

    def has_candidate_cpp_file(self):
        if self.candidate_cpp_file_list:
            return True
        else:
            return False

    def get_all_files_from_dir(self, dir_path):
        path = Path(dir_path)
        all_files_list = [file for file in path.rglob('*') if file.is_file()]
        return all_files_list

    def check_for_candidate(self, file_path):
        if ".cpp" in file_path:
            self.cpp_file_list.append(file_path)
        elif ".launch." in file_path:
            self.launch_file_list.append(file_path)
        elif ".param.yaml" in file_path:
            self.param_file_list.append(file_path)
        elif ".schema.json" in file_path:
            self.schema_file_list.append(file_path)
        elif "CMakeLists.txt" in file_path:
            self.cmake_file_list.append(file_path)
        elif ".md" in file_path:
            self.readme_file_list.append(file_path)

    def check_for_candidate_cpp_file(self, file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "declare_parameter" in line:
                    return True

    def get_cpp_file_list(self):
        return self.cpp_file_list

    def get_launch_file_list(self):
        return self.launch_file_list

    def get_param_file_list(self):
        return self.param_file_list

    def get_schema_file_list(self):
        return self.schema_file_list

    def get_cmake_file_list(self):
        return self.cmake_file_list

    def get_readme_file_list(self):
        return self.readme_file_list

    def get_candidate_cpp_file_list(self):
        return self.candidate_cpp_file_list