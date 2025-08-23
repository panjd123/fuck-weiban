from playwright.sync_api import sync_playwright, TimeoutError
import time
from tqdm import tqdm
from itertools import count
import os.path as osp

WAITING_SECS = 15 # s
STATE_FILE = "state.json"

def millisecond_countdown(total_seconds: float, update_interval: float = 0.02):
    total_steps = int(total_seconds / update_interval)
    start_time = time.monotonic()

    with tqdm(total=total_steps, desc="等待中", bar_format="{desc}|{bar}| {postfix}", leave=False) as pbar:
        for i in range(total_steps):
            elapsed_time = min(time.monotonic() - start_time, total_seconds)
            remaining_time = max(0, total_seconds - elapsed_time)
            
            time_str = f"已过: {elapsed_time:.1f}s | 剩余: {remaining_time:.1f}s"
            
            pbar.set_postfix_str(time_str)
            pbar.update(1)
            time.sleep(update_interval)
        pbar.n = pbar.total

def main():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    if osp.exists(STATE_FILE):
        context = browser.new_context(storage_state=STATE_FILE)
    else:
        context = browser.new_context()
    page = context.new_page()
    page.goto("https://weiban.mycourse.cn/")

    input("请手动完成登录，并进入第一个未学习的课程，等待页面加载完成，完成后按任意键开始...")
    context.storage_state(path=STATE_FILE)

    try:
        for i in count(start=1):
            millisecond_countdown(WAITING_SECS - 5 if i == 1 else WAITING_SECS)
            title = page.title()
            print(f"第 {i} 课: {title} ", end="")
            frame = page.frame_locator("#app > div > div > iframe").locator("body")
            frame.evaluate("finishWxCourse();")
            page.get_by_text("下一课").click()
            print(f"完成")
    except TimeoutError:
        print("所有课程已完成")
        input("按任意键退出")
        print("点个 star 谢谢喵：")

if __name__ == "__main__":
    main()