import sys
import shutil
import json
from openai import OpenAI
from sys import platform
from importlib import import_module
from pathlib import Path

class API:
    def __init__(self, agent):
        self.tokens = 0
        self.agent = agent
        
    def skill_prompt(self, skill, name, arguments="", answer=""):
        prompt = f'如果你需要{skill}，那么请输出"{name}'
        if arguments:
            prompt += f': {arguments}'
        prompt += '"。'
        if answer:
            prompt += f'执行命令后，用户会返回{answer}。'
        prompt += '\n'
        return prompt
    
    def register(self, name, func, prompt):
        self.agent.prompt += prompt
        self.agent.skills[name] = func

    def skill(self, name, prompt):
        def decorator(func):
            self.register(name, func, prompt)
            return func
        return decorator

class Agent:
    def __init__(self):
        self.main_path = Path("agent")
        self.skills_path = self.main_path / "skills"
        self.config_path = self.main_path / "config.json"
        self.history_path = self.main_path / "history.json"
        if not self.main_path.is_dir():
            shutil.copytree(self.get_resource(Path("default")), self.main_path)
            print("请修改配置文件 /agent/config.json 后继续")
            exit()
        with open(self.history_path, "r") as f:
            self.messages = json.load(f)
        self.skills = {}
        with open(self.config_path) as f:
            self.configs = json.load(f)
        self.client = OpenAI(api_key=self.configs["key"], base_url=self.configs["url"])
        self.model = self.configs["model"]
        self.api = API(self)

    def save_history(self):
        with open(self.history_path, "w") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)

    def get_resource(self, path):
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS) / path
        else:
            return path
            
    def import_skills(self):
        sys.path.append(str(self.skills_path))
        self.prompt = f"""【严格执行规则】
1. 一次只能输出一条指令，禁止换行、禁止多指令！
2. 格式只能是：指令名 或 指令名:参数。不能自己瞎编数值，能使用指令的一定要使用指令！
3. 如果你使用 text 回答了用户，并且你认为已经说完了全部内容，下一条指令必须直接输出 end！
4. 不许多问、不许多想、不许等待！
5. 任务完成 = 输出 end
        """
        for file in self.skills_path.glob("*.py"):
            module = import_module(file.stem)
            module.init(self.api)
        self.messages.append({"role": "system", "content": self.prompt})
        
    def request(self):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        self.api.tokens += response.usage.total_tokens
        self.save_history()
        return response.choices[0].message.content

    def agent_loop(self, answer):
        while True:
            while True:
                try:
                    self.messages.append({"role": "assistant", "content": answer})
                    mark = answer.find(":")
                    if mark == -1:
                        case = answer
                        argument = ""
                    else:
                        case = answer[:mark]
                        argument = answer[mark + 1:]
                    if case == "end":
                        return
                    skill = self.skills[case]
                    break
                except KeyError:
                    self.messages.append({"role": "system", "content": "格式错误，请重新回复。"})
                    answer = self.request()
            agent_answer = skill(argument)
            if agent_answer:
                self.messages.append({"role": "system", "content": agent_answer})
            answer = self.request()

def main():
    agent = Agent()
    agent.import_skills()
    while True:
        prompt = input("[你] ")
        agent.messages.append({"role": "user", "content": prompt})
        answer = agent.request()
        agent.agent_loop(answer)

if __name__ == '__main__':
    main()
