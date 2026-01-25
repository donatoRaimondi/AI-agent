import os

def get_files_info(working_directory, directory="."):
    try:
        # Resolve absolute paths
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

        # Security check: prevent directory traversal
        valid_target_dir = (
            os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        )
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # # Check existence
        # if not os.path.exists(target_dir):
        #     return f'Error: "{directory}" does not exist'

        # Check that it is a directory
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        dir_content = ""
        for item in os.listdir(target_dir):
                dir_content = dir_content + f"- {item}: file_size:{os.path.getsize(os.path.join(target_dir, item))}, is_dir={os.path.isdir(os.path.join(target_dir, item))}\n"
        
        return dir_content
    except Exception as e:
        return f"Error: {e}"