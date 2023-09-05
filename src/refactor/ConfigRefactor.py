from src.file_generator.FileGenerator import FileGenerator
from src.file_generator.FileParser import FileParser
from src.refactoring_related_files.RelatedFiles import RelatedFiles


class ConfigRefactor:
    dir_path: str
    related_files: RelatedFiles
    file_parser: FileParser
    file_generator: FileGenerator

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.related_files = self.search_for_files()
        self.file_parser = FileParser(self.related_files)
        self.file_generator = FileGenerator(self.related_files, self.file_parser.node_list)

    def refactor(self):
        if self.related_files.has_candidate_cpp_file():
            self.file_parser.parse_files()
            self.file_parser.parameter_judging()
            self.file_generator.generate_files()
            print(f"\nRefactoring complete!")

    def search_for_files(self):
        related_files = RelatedFiles(self.dir_path).get_related_files()
        return related_files
