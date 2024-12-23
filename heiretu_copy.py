from concurrent.futures import ProcessPoolExecutor
import shutil

def copy_file(src_dst):
    src, dst = src_dst
    shutil.copy2(src, dst)

files_to_copy = [
    (r"\\shared\dir\file1.txt", r"C:\local\dir\file1.txt"),
    (r"\\shared\dir\file2.txt", r"C:\local\dir\file2.txt"),
    (r"\\shared\dir\file3.txt", r"C:\local\dir\file3.txt"),
]

# ProcessPoolExecutorで並列化
with ProcessPoolExecutor() as executor:
    executor.map(copy_file, files_to_copy)
