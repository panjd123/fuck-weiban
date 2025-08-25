from playwright.sync_api import sync_playwright, TimeoutError
import time
from tqdm import tqdm
from itertools import count
import os.path as osp
import re

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

def find_uncompleted_modules(page):
    """查找未完成的课程模块"""
    print("查找未完成的课程模块...")
    
    # 查找所有课程模块
    modules = page.locator(".van-collapse-item")
    modules.first.wait_for()
    uncompleted_modules = []
    
    for i in range(modules.count()):
        module = modules.nth(i)
        try:
            title_element = module.locator(".van-cell__title")
            if not title_element.count():
                continue
                
            # text = title_element.inner_text().strip()
            text = title_element.inner_text().strip().replace('\n', ' ')
            print(f"检查模块: {text}")
            
            # 匹配进度格式 "x/y"
            numbers = re.findall(r'\d+', text)
            if len(numbers) >= 2:
                completed = int(numbers[0])
                total = int(numbers[1])
                
                if completed < total:
                    module_name = re.sub(r'\d+/\d+', '', text).strip()
                    uncompleted_modules.append({
                        'element': module.locator(".van-cell.van-cell--clickable"),
                        'module': module,
                        'name': module_name,
                        'progress': f"{completed}/{total}"
                    })
                    print(f"未完成模块: {module_name} ({completed}/{total})")
                else:
                    module_name = re.sub(r'\d+/\d+', '', text).strip()
                    print(f"已完成模块: {module_name} ({completed}/{total})")
        except Exception as e:
            print(f"检查模块时出错: {e}")
    
    print(f"找到 {len(uncompleted_modules)} 个未完成模块")
    return uncompleted_modules

def expand_module(page, module_data):
    """展开课程模块"""
    print(f"展开模块: {module_data['name']} {module_data['progress']}")
    
    try:
        module_data['element'].click()
        print("模块展开成功")
        return True
    except Exception as e:
        print(f"模块展开失败: {e}")
        return False

def find_course_cards(page, module_element):
    """查找模块中的课程卡片"""
    print("查找课程卡片...")
    
    try:
        content_area = module_element.locator(".van-collapse-item__content")
        if not content_area.count():
            print("未找到内容区域")
            return []
        
        # 查找课程卡片
        course_items = content_area.first.locator("li.img-texts-item")
        course_items.first.wait_for()
        cards = []
        for i in range(course_items.count()):
            item = course_items.nth(i)
            try:
                title_element = item.locator("h5.title")
                title = title_element.inner_text().strip() if title_element else item.inner_text().strip()
                
                if title and len(title) > 3:  # 避免空标题或太短的标题
                    cards.append({
                        'element': item,
                        'name': title
                    })
                    print(f"找到课程: {title}")
            except Exception as e:
                print(f"处理课程卡片时出错: {e}")
        
        print(f"找到 {len(cards)} 个课程卡片")
        return cards
        
    except Exception as e:
        print(f"查找课程卡片失败: {e}")
        return []

def click_first_course(page, card_data):
    """点击第一个课程卡片"""
    print(f"点击第一个课程: {card_data['name']}")
    
    try:
        card_data['element'].click()
        print("课程点击成功")
        return True
    except Exception as e:
        print(f"课程点击失败: {e}")
        return False

def find_and_enter_first_uncompleted_course(page):
    """查找并进入第一个未完成的课程"""
    print("开始查找第一个未完成的课程...")
    
    # 1. 查找未完成模块
    modules = find_uncompleted_modules(page)
    if not modules:
        print("所有模块都已完成！")
        return False
    
    # 2. 选择第一个未完成模块
    first_module = modules[0]
    print(f"\n选择第一个未完成模块: {first_module['name']} {first_module['progress']}")
    
    # 3. 展开模块
    if not expand_module(page, first_module):
        print("模块展开失败")
        return False
    
    # 4. 查找课程卡片
    cards = find_course_cards(page, first_module['module'])
    if not cards:
        print("未找到课程卡片")
        return False
    
    # 5. 点击第一个课程
    first_card = cards[0]
    print(f"\n准备进入第一个课程: {first_card['name']}")
    
    if click_first_course(page, first_card):
        print("成功进入第一个未完成的课程！")
        print("自动处理课程...")
        return True
    else:
        print("进入课程失败！")
        return False

def main():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    if osp.exists(STATE_FILE):
        context = browser.new_context(storage_state=STATE_FILE)
    else:
        context = browser.new_context()
    page = context.new_page()
    page.goto("https://weiban.mycourse.cn/")
    input("\n请手动完成登录，等待页面加载完成，完成后按任意键开始...")
    context.storage_state(path=STATE_FILE)
    
    # 自动查找并进入第一个未完成的课程      
    if not find_and_enter_first_uncompleted_course(page):
        input("未能找到或进入未完成的课程\n你可以手动进入第一节未完成的课程，完成后按任意键继续...")
    try:
        for i in count(start=1):
            millisecond_countdown(WAITING_SECS)
            title = page.title()
            print(f"第 {i} 课: {title} ", end="")
            frame = page.frame_locator("#app > div > div > iframe").locator("body")
            frame.evaluate("finishWxCourse();")
            page.get_by_text("下一课").click()
            print(f"完成")
    except TimeoutError:
        print(f"所有课程已完成")
        print("点个 star 谢谢喵：https://github.com/panjd123/fuck-weiban")
        input("按任意键退出...")

if __name__ == "__main__":
    main()