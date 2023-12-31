import re
from typing import Any


class Parameter:
    param_name: str
    param_type: str
    param_value: str
    param_description: str
    cpp_type: str
    schema_type: str
    schema_value: str
    python_type: str
    python_value: Any

    def __init__(self, param_name):
        self.param_name = param_name
        self.param_type = ""
        self.param_value = ""
        self.param_description = ""
        self.cpp_type = ""
        self.schema_type = ""
        self.schema_value = ""
        self.python_type = ""
        self.python_value = None

    def judge_parameter(self):
        if self.python_type or self.cpp_type:
            self.set_param_schema_type_value(self.python_type, self.cpp_type)

    def set_cpp_type(self, cpp_type):
        if cpp_type:
            self.cpp_type = cpp_type
            # self.set_type(cpp_type)

    def set_param_value(self, param_value):
        if param_value:
            pattern = r".*\((.+)\)"
            match = re.search(pattern, param_value)
            if match:
                param_value = match.group(1)
            self.param_value = param_value
            self.set_python_value_type(param_value)

    def set_param_description(self, param_description):
        self.param_description = param_description

    def set_python_value_type(self, param_value):
        self.python_value = eval(self.proprocess_value(param_value))
        self.python_type = type(self.python_value).__name__

    def proprocess_value(self, param_value):
        if param_value == "true":
            return "True"
        elif param_value == "false":
            return "False"
        else:
            return param_value

    def print_parameter(self):
        print(f"Parameter: {self.param_name}")
        print(f"    cpp type: {self.cpp_type}")
        print(f"    python type: {self.python_type}")
        print(f"    param value: {self.param_value}")
        print(f"    Description: {self.param_description}")

    def set_param_schema_type_value(self, python_type, cpp_type):
        self.schema_value = self.param_value

        if python_type:
            if python_type == "str":
                self.param_type = "std::string"
                self.schema_type = "string"
                if self.schema_value[0] == "\"" and self.schema_value[-1] == "\"":
                    self.schema_value = self.schema_value[1:-1]
            elif python_type == "int":
                self.param_type = "int64_t"
                self.schema_type = "integer"
            elif python_type == "float":
                self.param_type = "float"
                self.schema_type = "number"
            elif python_type == "bool":
                self.param_type = "bool"
                self.schema_type = "boolean"
        else:
            if cpp_type == "string" or cpp_type == "std::string":
                self.param_type = "std::string"
                self.schema_type = "string"
                if self.schema_value[0] == "\"" and self.schema_value[-1] == "\"":
                    self.schema_value = self.schema_value[1:-1]
            elif cpp_type == "int" or cpp_type == "int32_t" or cpp_type == "int64_t":
                self.param_type = "int64_t"
                self.schema_type = "integer"
            elif cpp_type == "double":
                self.param_type = "double"
                self.schema_type = "number"
            elif cpp_type == "float":
                self.param_type = "float"
                self.schema_type = "number"
            elif cpp_type == "bool":
                self.param_type = "bool"
                self.schema_type = "boolean"

    def __str__(self):
        return f"{self.param_name}: {self.param_type} {self.param_value} ({self.param_description})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.param_name == other.param_name and self.param_type == other.param_type and
                self.param_value == other.param_value and self.param_description == other.param_description)

    def __hash__(self):
        return hash((self.param_name, self.param_type, self.param_value, self.param_description))
