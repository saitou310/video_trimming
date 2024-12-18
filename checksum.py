def calculate_file_sum(filepath):
    with open(filepath, 'rb') as f:
        return sum(f.read())

def compare_file_sums(file1, file2):
    sum1 = calculate_file_sum(file1)
    sum2 = calculate_file_sum(file2)
    return sum1 == sum2

# 使用例
file1 = 'file1.txt'
file2 = 'file2.txt'

if compare_file_sums(file1, file2):
    print("2つのファイルの合計値は一致します。")
else:
    print("2つのファイルの合計値は一致しません。")
