import os
from multiprocessing import Pool

class FileProcessor:
    def __init__(self, folder_path, num_processes=4):
        self.folder_path = folder_path
        self.num_processes = num_processes

    def process_file(self, file_path):
        # Add your file processing logic here
        # For example, print the file name
        print(f"Processing file: {file_path}")

    def process_folder(self):
        files = [os.path.join(self.folder_path, file) for file in os.listdir(self.folder_path)]

        # Create a Pool with the specified number of processes
        with Pool(self.num_processes) as pool:
            # Use the pool to process files in parallel
            pool.map(self.process_file, files)

if __name__ == "__main__":
    # Example usage
    folder_path = "C:\\Users\\schatzm\\Documents\\GitHub\\CZI_processing\\libczi_notebook"
    num_processes = 4

    file_processor = FileProcessor(folder_path, num_processes)
    file_processor.process_folder()