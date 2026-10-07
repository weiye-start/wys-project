import subprocess
import sys

print("正在编译…")
result = subprocess.run(["gcc","wy.c","-o","wy.exe"],capture_output=True,text=True)
if result.returncode == 0:
    print("编译成功,正在运行")
    subprocess.run([".\\wy.exe"])
else:
    print("编译失败,请检查代码!错误信息如下:")
    print(result.stderr)