from os import popen
from datetime import datetime

def init(api):
    @api.skill("text", api.skill_prompt("输出文本", "text"))
    def do_text(arg):
        print(f"[AI] {arg.strip()}")
        return ""

    @api.skill("command", api.skill_prompt("执行命令", "command", "命令执行结果"))
    def do_command(arg):
        print(f"[AI] 执行命令：{arg}")
        do = input("确定要执行吗？(y/[n]) ").lower()
        if do == "y":
            with popen(arg) as f:
                return f.read()
        else:
            return "用户拒绝执行。"

    @api.skill("python", api.skill_prompt("执行python表达式", "python", "表达式的结果"))
    def do_python(arg):
        print(f"[AI] 计算python表达式：{arg}")
        do = input("确定要计算吗？(y/[n]) ").lower()
        if do == "y":
            return eval(arg)
        else:
            return "用户拒绝计算。"

    @api.skill("token", api.skill_prompt("获取一共使用了多少token", "token", "总共使用的token"))
    def do_token(arg):
        print(f"[AI] 获取总共使用的token")
        return api.tokens

    @api.skill("exit", api.skill_prompt("退出对话", "exit"))
    def do_exit(arg):
        print(f"[AI] 退出程序")
        do = input("确定要退出程序吗？(y/[n]) ").lower()
        if do == "y":
            exit()
        else:
            return "用户拒绝退出。"

    @api.skill("time", api.skill_prompt("获取时间", "time", "YYYY-mm-dd HH:MM:SS格式的时间"))
    def do_time(arg):
        print("[AI] 获取时间")
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
