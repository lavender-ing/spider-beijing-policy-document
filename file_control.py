import os
import shutil
def solve(year):
    os.chdir('当前路径/file')
    des_path = '当前路径/file/'+year # ！！！运行之前确定年份到底对不对，无法撤销
    if os.path.exists(des_path) == False:
        os.mkdir(des_path)

    list = os.listdir(os.getcwd())
    for i in list:
        if 'DS' in i:
            print(i)
        elif os.path.isfile(i):
            shutil.move(i, des_path)
            # print(os.path.abspath(i))


