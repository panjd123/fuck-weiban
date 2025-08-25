import os
import os.path as osp
import re
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv
from zai import ZhipuAiClient

load_dotenv()
STATE_FILE = "state.json"
client = ZhipuAiClient()

system_prompt = """你是一个校园安全问题专家，你会收到用户提出的选择题，你需要直接回答选项的字母，例如A，如果是多选题，你需要回答所有你认为正确的答案的字母"""

user_prompt = """{quest_category}：
{question}
选项：
{choices}
答案："""


def get_answer(quest_category, question, choices):
    user_content = user_prompt.format(
        quest_category=quest_category, question=question, choices=choices
    )
    print(user_content)
    response = client.chat.completions.create(
        model="glm-4.5-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        thinking={
            "type": os.getenv("thinking", "disabled").lower()
        },
        temperature=0  # 避免随机性
    )
    answer = response.choices[0].message.content.strip()
    print(answer)
    letters = re.findall(r"[A-D]", answer.upper())
    mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
    return [mapping[ch] for ch in letters if ch in mapping]

def main():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    if osp.exists(STATE_FILE):
        context = browser.new_context(storage_state=STATE_FILE)
    else:
        context = browser.new_context()
    page = context.new_page()
    page.goto("https://weiban.mycourse.cn/")
    input("\n请手动完成登录，并进入考试界面，即第一道题的界面，完成后按任意键开始...")
    context.storage_state(path=STATE_FILE)

    last_question = ""
    while True:
        try:
            expect(page.locator(".quest-stem")).not_to_have_text(last_question, timeout=1000)
        except AssertionError:
            page.locator("#app > div > div.mint-popup.confirm-sheet.mint-popup-right > div.bottom-ctrls > button.mint-button.mint-button--danger.mint-button--normal").click()
            print("交卷")
            break
        question = page.locator(".quest-stem").inner_text()
        quest_category = page.locator(
            "#app > div > div.main-content > div > div.exam-info > div.quest-info > div.quest-category"
        ).inner_text()
        choices_locator = page.locator(".quest-option-top")
        choices = []
        for i in range(choices_locator.count()):
            choice = choices_locator.nth(i).inner_text()
            choice = choice.replace("\n", ".")
            choices.append(choice)
        choices = "\n".join(choices)
        answer = get_answer(quest_category, question, choices)
        for i in answer:
            choices_locator.nth(i).click()
        page.get_by_text("下一题").click()
        last_question = question

    print("点个 star 谢谢喵：https://github.com/panjd123/fuck-weiban")
    input("按任意键退出...")

if __name__ == "__main__":
    main()