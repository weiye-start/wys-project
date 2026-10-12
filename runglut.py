import subprocess
result = subprocess.run(["gcc","-std=c99","glutsnake.c","-o","glutsnake.exe"],capture_output=True,text=True)
if result.returncode == 0:
    print("编译成功，正在运行")
    subprocess.run([".\\glutsnake.exe"])
else:
    print("编译失败，问题如下:")
    print(result.stderr)