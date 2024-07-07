import os
import zipfile
import argparse
from datetime import datetime, timedelta

def print_delta_time(delta: timedelta)->str:
    """Formats a timedelta object to a string in the format HH:MM:SS.
    
    Args:
        delta (timedelta): The time delta object to format.

    Returns:
        str: The formatted time string in HH:MM:SS format.
    """
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def check_source_dir_permission(path:str) -> None:
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Read permission denied for the source path: {path}")

def do_archive(src_path:str, output_dir:str, depth:int = 10)->None:
    """Archives the specified folder up to a given depth.

    Args:
        path (str): Path to the folder to archive.
        depth (int): Maximum depth of subfolders to include.

    Raises:
        ValueError: If the depth is not a positive integer.
    """

    # Normalize the path and validate depth
    src_path = os.path.normpath(src_path)
    output_dir = os.path.normpath(output_dir)

    # Create a directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set up archive name
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    archive_name = os.path.basename(src_path.rstrip(os.sep)) + "_{}".format(timestamp) + '.zip'
    archive_path = os.path.join(output_dir, archive_name)

    start_time = datetime.now()

    try:
        if depth < 1:
            raise ValueError("Depth must be at least 1")

        check_source_dir_permission(src_path)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for root, dirs, files in os.walk(src_path):
                # Considering the depth of the curretn directory
                current_depth = root[len(src_path):].count(os.sep)

                if current_depth < depth:
                    for file in files:
                        # Get a full path
                        file_path = os.path.join(root, file)
                        print(f"Archiving: {os.path.normpath(file_path)}")
                        archive.write(file_path, os.path.relpath(file_path, src_path))
                else:
                    # Limit depth by modifying dirs in-place
                    dirs[:] = []
        
        end_time = datetime.now()
        elapsed_time = end_time - start_time

        print('-' * 50)
        print(f"Archive create: {archive_name}")
        print(f"Archivation time: {print_delta_time(elapsed_time)}")

    except Exception as ex:
        # Clean up archive file.
        if os.path.exists(archive_path):
            os.remove(archive_path)
        print(f'Error occured: {ex}')

def main():
    parser = argparse.ArgumentParser(description="Archivation utility with specified depth.")
    parser.add_argument('-p', '--path', type=str, default=os.getcwd(), help='Path to the folder to archive.')
    parser.add_argument('-o', '--output_dir', type=str, default=os.getcwd(), help='Path to the output folder where archive will be created.')
    parser.add_argument('-d', '--depth', type=int, default=10, help='Depth of subfolders to include.')

    args = parser.parse_args()
    do_archive(args.path, args.output_dir, args.depth)

if __name__ == "__main__":
    main()