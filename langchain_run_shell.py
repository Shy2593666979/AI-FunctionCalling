import subprocess

def run_Shell(shell):
    result = subprocess.run(shell, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 输出命令的标准输出
    print(result.stdout)

    # 输出命令的标准错误
    print(result.stderr)

    return result.stdout
