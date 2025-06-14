"""
ファイル操作の復習
"""

import csv
import os
import string
import tarfile
import zipfile
import glob
import datetime
import shutil
import subprocess


"""
ダミーログを作成する関数
"""
def create_dammy_logfile(filename):
    filepath = os.path.join('log_dir', filename)
    with open(filepath, 'w') as f:
        for i in range(10):
            f.write(f'Line{i}\n')

"""
ログファイルの一部読み込み
"""
def read_logfile(filepath):
    with open(filepath, 'r') as f:
        chunk = 3
        print(f.read(chunk))
        f.seek(11) # f.seek()に戻り値はない
        print(f.read(chunk*2))

"""
tar,zipの圧縮
"""
def archive(timestamp):
    archive_dir = os.path.join('archive', timestamp)
    os.makedirs(archive_dir, exist_ok=True)

    tar_name = os.path.join(archive_dir, f'logs_{timestamp}.tar.gz')
    zip_name = os.path.join(archive_dir, f'logs_{timestamp}.zip')

    log_dir = 'log_dir'

    with tarfile.open(tar_name, 'w:gz') as tar:
        tar.add(log_dir, arcname=os.path.basename(log_dir))

    with zipfile.ZipFile(zip_name, 'w') as z:
        for filepath in glob.glob(f'{log_dir}/*', recursive=True):
            if os.path.isfile(filepath):
                z.write(filepath, arcname=os.path.relpath(filepath, start=log_dir))

"""
bk作成
"""
def backup(timestamp):
    backup_dir = os.path.join('backup', timestamp)
    os.makedirs(backup_dir, exist_ok=True)

    for filepath in glob.glob('log_dir/*', recursive=True):
        filename = os.path.basename(filepath)
        shutil.copy(filepath,
                    os.path.join(backup_dir, filename))

"""
ログのファイル名・ファイルサイズのcsv出力
"""
def csv_writer():
    summary_list = []

    with open('log_summary.csv', 'w') as csvfile:
        fieldnames = ['filename', 'bytesize']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for filepath in glob.glob('log_dir/*', recursive=True):
            size = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            writer.writerow({'filename':filename, 'bytesize':size})

            summary_list.append(f'{filename}:{size}bytes')

        summary = '\n'.join(summary_list)

    return summary

"""
csvに出力した内容をテンプレートに従い出力
"""
def tmp_notify(summary):
    with open('email_template.txt') as f:
        t = string.Template(f.read())

    contents = t.substitute(name='Kaito', summary=summary)
    print(contents)

"""
実行後のディレクトリ構成のターミナル出力をsubprocessで実施
"""
def subprocess_run():
    subprocess.run(['ls', '-al'])


if __name__ == '__main__':
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('log_dir', exist_ok=True)

    create_dammy_logfile('access.log')
    create_dammy_logfile('error.log')
    create_dammy_logfile('system.log')
    # read_logfile('log_dir/access.log')

    backup(timestamp)
    archive(timestamp)
    summary = csv_writer()
    tmp_notify(summary)
    subprocess_run()

