#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
import subprocess
import datetime
from threading import Thread
from queue import Queue, Empty


main_cmd = 'ghci'
# main_cmd = '/home/yamaguchi/bin/fc_client -h 192.168.16.5 -i 3000 -u db_admin -p db_admin'

interval_time = 0.1 # 
# success_keyword = '--QUERY RESULT--'
success_keyword = '0'

# プログラム終了まで標準出力を監視続け、
# なんか来たら出力キューに入れておくスレッド
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    #out.close()

# 出力キューの内容を全部吐き出させる関数
def out_allelements_queue(que):
    while True:
        try:
            line = que.get(timeout=0.001)
        except Empty:
            break
        else:
            print(line.decode().strip())

# fc_client にSQLを投げた後、fc_clientが何か出力するまで待って
# それを全部吐き出してから帰る関数
def run_sql(proc, que, sql):
    # コマンドを投げる前に出力キューの内容を全部吐き出しておく。
    out_allelements_queue(que)

    # コマンドを投げる
    print('---- run:{0} ----'.format(sql.strip()))
    start_time = time.time()
    proc.stdin.write(sql.encode())
    proc.stdin.flush()

    # 返事があるまで待つ
    while True:
        try:
            line = q.get_nowait()
        except Empty:
            time.sleep(0.001)
        else:
            line = line.decode().strip()
            #print(line)
            if success_keyword in line:
                break
    elapsed_time = time.time() - start_time

    # 返事を全部吐き出す
    out_allelements_queue(que)
    print('---- end:{0}  {1}(secs) ----'.format(sql.strip(), elapsed_time))

# 適当な値でINSERT文を作成して標準入力に書き込み、
# → 返事を待って出力
def task_insert(i):
    sql = 'INSERT INTO TBL80B VALUES ('
    for c in range(9):
        sql += str(i + c)
        sql += ','
    sql += str(i + 10)
    sql += ');'
    sql += '\n'
    run_sql(p, q, sql)

# コミット発行 → 返事を待って出力
def task_commit():
    sql = 'COMMIT;' + '\n'
    run_sql(p, q, sql)

# 対象テーブルの行数を取得して出力
def task_count():
    sql = 'SELECT count(*) FROM TBL80B;' + '\n'
    run_sql(p, q, sql)

# 時間がかかるSQLをお試し実行
def task_test():
    sql = 'select avg(p1), sum(p2) from TBL80B;' + '\n'
    run_sql(p, q, sql)

def task_ghci():
    cmd = '10000000 * 12345678901234567890' + '\n'
    run_sql(p, q, cmd)

    
# ここからメイン処理
p = subprocess.Popen(main_cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True
t.start()

#last_time = time.time()
#i = 1
#while i <= 1000:
#    if time.time() - last_time > interval_time:
#        last_time = time.time()
#        task_insert(i)
#        i += 1
#    else:
#        time.sleep(interval_time / 5)

#task_commit()
#time.sleep(0.1)

#task_count()
#time.sleep(0.1)

#task_test()
#time.sleep(0.1)

task_ghci()
time.sleep(0.1)

# fc_client にEXITを発行して終了
#sql = 'exit\n'
sql = ':quit\n'
p.stdin.write(sql.encode())
p.stdin.flush()
p.terminate()


# In[ ]:




