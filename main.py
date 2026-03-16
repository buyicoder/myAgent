"""
主入口：在终端与 Agent 对话（可改为 API、机器人等）。
"""
from agent import run_agent


def main():
    print("Agent 已启动。输入问题后回车，输入 quit 或 exit 退出。\n")
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("再见。")
            break
        print("Agent: ", end="", flush=True)
        reply = run_agent(user_input)
        print(reply)
        print()


if __name__ == "__main__":
    main()
