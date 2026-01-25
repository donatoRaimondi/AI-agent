import os
import subprocess
import sys

def run_python_file(working_directory, file_path, args=None):
    try:
        #validate args
        args = args or []
        if isinstance(args, str):
            args = [args]

        # Resolve absolute paths
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # Security check: prevent directory traversal
        valid_target_dir =  os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(target_dir):
            return f'Error: "{file_path}" does not exist'

        # Check that it is a directory
        if not os.path.isfile(target_dir):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        if not os.path.splitext(target_dir)[1] == ".py":
            return f'Error: "{file_path}" is not a Python file'

        # subprocess to run the python script
        command = [sys.executable, target_dir, *args]

        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            timeout=30,
            text=True,
            capture_output=True
        )
        
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()

        if stdout or stderr:
            return (
                f"Process exited with code {result.returncode}\n"
                f"STDOUT: {stdout if stdout else '(empty)'}\n"
                f"STDERR: {stderr if stderr else '(empty)'}"
            )

        return f'Process exited with code {result.returncode} No output produced'
    except Exception as e:
        return f"Error: executing Python file: {e}"