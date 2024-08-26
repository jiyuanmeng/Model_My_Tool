import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import data

if __name__ == "__main__":
    data.load_all()
