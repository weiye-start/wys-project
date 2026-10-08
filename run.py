import subprocess
import sys

print("正在编译…")
result = subprocess.run(["gcc","wy.c","-o","wy.exe"],capture_output=True,text=True)
if result.returncode == 0:
    print("\033[32m编译成功,正在运行\033[0m")
    subprocess.run([".\\wy.exe"])
else:
    print("\033[31m编译失败,请检查代码!错误信息如下:\033[0m")
    print(result.stderr)