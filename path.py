import os

# Get the path of the current file (e.g., backend.py or front.py)
current_file_path = os.path.abspath(__file__)

# Get the directory of the current file
current_dir_path = os.path.dirname(current_file_path)

# Get the path of the 'results' directory by navigating up to the project root
# and then down into the 'results' directory
project_root = os.path.dirname(current_dir_path)
results_dir_path = os.path.join(project_root, 'results')

print("The absolute path to the 'results' directory is:", results_dir_path)
