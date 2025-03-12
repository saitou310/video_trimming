import sys
import os
import shutil


def copyDirectory(sourceDir, destBaseDir, maxDirs, debug=False):
    # コピー元ディレクトリの存在確認
    if not os.path.exists(sourceDir) or not os.path.isdir(sourceDir):
        print(f"エラー: コピー元ディレクトリ '{sourceDir}' が存在しません。")
        return

    # コピー先ディレクトリの作成（存在しない場合）
    os.makedirs(destBaseDir, existOk=True)

    # コピー元ディレクトリ名を取得
    sourceName = os.path.basename(sourceDir)
    newDestDir = os.path.join(destBaseDir, sourceName)

    # コピー先に同名のディレクトリが既に存在する場合、コピーを行わない
    if os.path.exists(newDestDir):
        print(f"コピー先ディレクトリ '{newDestDir}' が既に存在するため、コピーを中止します。")
        return

    # 既存のディレクトリ数を確認
    existingDirs = [d for d in os.listdir(destBaseDir) if os.path.isdir(os.path.join(destBaseDir, d))]
    if debug:
        print(f"コピー先ディレクトリ内の既存ディレクトリ数: {len(existingDirs)} (上限: {maxDirs})")

    # 上限を超えていればコピーしない
    if len(existingDirs) >= maxDirs:
        print("コピー先ディレクトリが上限に達しているため、コピーを中止します。")
        return

    # ディレクトリをコピー
    try:
        shutil.copytree(sourceDir, newDestDir)
        print(f"ディレクトリ '{sourceDir}' を '{newDestDir}' にコピーしました。")
    except Exception as e:
        print(f"エラー: コピーに失敗しました。{e}")


if __name__ == "__main__":
    # 引数のチェック
    if len(sys.argv) < 4:
        print(
            "使用法: python copyDir.py (コピー元ディレクトリ) (コピー先ディレクトリ) (コピー先ディレクトリの上限数) [デバッグモード]")
        sys.exit(1)

    # 引数の取得
    sourceDir = sys.argv[1]
    destBaseDir = sys.argv[2]
    try:
        maxDirs = int(sys.argv[3])
    except ValueError:
        print("エラー: コピー先ディレクトリの上限数は整数で指定してください。")
        sys.exit(1)

    # デバッグモードの処理
    debug = False
    if len(sys.argv) > 4 and sys.argv[4].lower() in ("true", "1", "yes"):
        debug = True

    # 実行
    copyDirectory(sourceDir, destBaseDir, maxDirs, debug)
