from playwright.sync_api import sync_playwright
import time
import os.path as osp

STATE_FILE = "state.json"

def get_user_info(page):
    """从localStorage中获取用户信息"""
    user_info = None
    try:
        user_info = page.evaluate("() => JSON.parse(localStorage.getItem('user'))")
        if user_info:
            print(f"获取用户信息成功: {user_info.get('userName', '未知用户')}")
        else:
            print("获取用户信息失败: 未找到用户数据")
    except Exception as e:
        print(f"获取用户信息时出错: {e}")
    return user_info

def exam_api_request(page, url, params):
    """发送考试相关的API请求"""
    try:
        # 构建请求体
        request_body = []
        for key, value in params.items():
            request_body.append(f"{key}={value}")
        request_body = "&".join(request_body)
        
        # 获取用户token
        user_info = get_user_info(page)
        if not user_info:
            return None
            
        # 发送请求
        response = page.request.post(
            url,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'X-Token': user_info['token'],
            },
            data=request_body
        )
        
        if response.status != 200:
            print(f"请求失败! Status: {response.status}, Message: {response.text}")
            return None
            
        data = response.json()
        if data.get('code') != '0':
            print(f"请求返回错误码: Code: {data.get('code')}, DetailCode: {data.get('detailCode')}, Msg: {data.get('msg')}")
        return data
        
    except Exception as e:
        print(f"请求出现未知错误:\n{e}")
        return None

def get_project_list(page):
    """获取用户学习项目"""
    url = "https://weiban.mycourse.cn/pharos/index/listMyProject.do"
    user_info = get_user_info(page)
    if not user_info:
        return None
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'ended': '2',
    }
    
    response = exam_api_request(page, url, params)
    return response.get('data') if response else None

def get_exams(page, user_project_id):
    """获取考试列表"""
    url = "https://weiban.mycourse.cn/pharos/exam/listPlan.do"
    user_info = get_user_info(page)
    if not user_info:
        return None
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'userProjectId': user_project_id,
    }
    
    response = exam_api_request(page, url, params)
    return response.get('data') if response else None

def get_exam_history(page, exam_plan_id, exam_type):
    """获取考试历史记录"""
    url = "https://weiban.mycourse.cn/pharos/exam/listHistory.do"
    user_info = get_user_info(page)
    if not user_info:
        return None
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'examPlanId': exam_plan_id,
        'examType': str(exam_type)
    }
    
    response = exam_api_request(page, url, params)
    return response.get('data') if response else None

def get_exam_answer(page, user_exam_id):
    """获取考试答题记录和正确答案"""
    url = "https://weiban.mycourse.cn/pharos/exam/reviewPaper.do"
    user_info = get_user_info(page)
    if not user_info:
        return None
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'userExamId': user_exam_id,
        'isRetake': '2',
    }
    
    response = exam_api_request(page, url, params)
    return response.get('data', {}).get('questions') if response else None

def start_exam(page, user_exam_plan_id):
    """开始考试"""
    url = "https://weiban.mycourse.cn/pharos/exam/startPaper.do"
    user_info = get_user_info(page)
    if not user_info:
        return None
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'userExamPlanId': user_exam_plan_id,
    }
    
    response = exam_api_request(page, url, params)
    return response.get('data', {}).get('questionList') if response else None

def submit_answer(page, exam_plan_id, user_exam_plan_id, question_id, answer_ids):
    """提交答案"""
    url = "https://weiban.mycourse.cn/pharos/exam/recordQuestion.do"
    user_info = get_user_info(page)
    if not user_info:
        return False
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'examPlanId': exam_plan_id,
        'userExamPlanId': user_exam_plan_id,
        'questionId': question_id,
        'answerIds': answer_ids,
        'useTime': '10',
    }
    
    response = exam_api_request(page, url, params)
    return response and response.get('code') == '0'

def submit_paper(page, user_exam_plan_id):
    """交卷"""
    url = "https://weiban.mycourse.cn/pharos/exam/submitPaper.do"
    user_info = get_user_info(page)
    if not user_info:
        return None
        
    params = {
        'tenantCode': user_info['tenantCode'],
        'userId': user_info['userId'],
        'userExamPlanId': user_exam_plan_id,
    }
    
    response = exam_api_request(page, url, params)
    return response.get('data') if response and response.get('code') == '0' else None

def print_exam(exam):
    """打印考试信息"""
    retake_text = "  (补考)" if (exam.get('isRetake') == 1 and exam.get('examType') == 1) else ""
    print(f"- {exam.get('examPlanName')}  最高成绩: {exam.get('examScore')} 分  已答 {exam.get('examFinishNum')} / {exam.get('answerNum')} 次{retake_text}")

def apply_exam_answer(question, answers, exam_answers):
    """应用考试答案"""
    # 查找当前问题的答案
    answer = next((a for a in exam_answers if a.get('title') == question.get('title')), None)
    
    if not answer:
        print("    找不到本题答案")
        return
        
    # 获取正确答案内容
    correct_answers = [opt.get('content') for opt in answer.get('optionList', []) if opt.get('isCorrect') == 1]
    
    # 匹配选项ID
    for option in question.get('optionList', []):
        if option.get('content') in correct_answers:
            print(f"    {option.get('content')}")
            answers.append(option.get('id'))

def start_exam_with_callback(page, exam, question_handler):
    """开始考试并处理问题"""
    print(f"    开始考试")
    
    exam_questions = start_exam(page, exam.get('id', ''))
    if not exam_questions:
        print(f"    失败\n    尝试调用页面验证码进入考试\n    请完成验证码后重试")
        return False
        
    for question in exam_questions:
        print(f"    {question.get('title', '')}")
        
        answers = []
        question_handler(question, answers)
        
        success = submit_answer(
            page, 
            exam.get('examPlanId', ''), 
            exam.get('id', ''), 
            question.get('id', ''), 
            ','.join(answers)
        )
        
        print(f"    {'成功' if success else '失败'}")
        
        # 等待一段时间
        time.sleep(1)
        
    # 等待5秒后交卷
    for i in range(5, 0, -1):
        print(f"    等待 {i} 秒后交卷")
        time.sleep(1)
        
    submit_result = submit_paper(page, exam.get('id', ''))
    if submit_result:
        score = submit_result.get('score', 0)
        print(f"    交卷成功, 分数: {score}")
        if score < 100:
            print("    没有满分的可以多刷几次, 因为考的次数越多, 能查到的题就越多")
    else:
        print("    交卷失败!")
        
    return True

def take_all_exams(page):
    """处理所有考试"""
    print("开始处理考试...")
    
    # 获取所有项目
    projects = get_project_list(page)
    if not projects:
        print("获取用户学习项目失败")
        return
    
    if not projects:
        print("没有学习项目")
        return
        
    for project in projects:
        project_name = project.get('projectName', '未知项目')
        user_project_id = project.get('userProjectId', '')
        print(f"\n获取项目 '{project_name}' 的考试:")
        
        # 获取考试列表
        exams = get_exams(page, user_project_id)
        if not exams:
            print("获取失败")
            continue
            
        if not exams:
            print("没有考试")
            continue
            
        for exam in exams:
            print_exam(exam)
            
        # 查找已完成考试
        print("查找做过的考试:")
        done_exams = [exam for exam in exams if exam.get('examFinishNum', 0) > 0]
        
        if not done_exams:
            print("找不到已完成考试\n我们需要先故意做错至少一个考试, 获取到答案再做补考")
            
            # 取第一个考试进行初次考试
            todo_exam = exams[0]
            print_exam(todo_exam)
            
            if not start_exam_with_callback(page, todo_exam, lambda question, answers: answers.append(question['optionList'][0]['id'])):
                continue
                
            print("    初次考试已完成\n    再次运行 '刷考试' 即可根据初次考试的答案刷补考")
            continue
            
        for exam in done_exams:
            print_exam(exam)
            
        # 收集答案
        exam_answers = []
        for done_exam in done_exams:
            print("获取答题记录")
            
            exam_plan_id = done_exam.get('examPlanId', '')
            exam_type = done_exam.get('examType', 2)
            
            exam_history = get_exam_history(page, exam_plan_id, exam_type)
            if not exam_history:
                print("获取失败")
                continue
                
            print(f"正在获取 {len(exam_history)} 个答题分析和答案")
            for history in exam_history:
                history_id = history.get('id', '')
                
                answers = get_exam_answer(page, history_id)
                if not answers:
                    print("获取失败")
                    continue
                    
                for answer in answers:
                    if not any(a.get('title') == answer.get('title') for a in exam_answers):
                        exam_answers.append(answer)
                        
                print("成功")
                
        print(f"成功获取 {len(exam_answers)} 条答案")
        
        # 查找未完成考试
        print("查找未完成考试:")
        todo_exam = next((exam for exam in exams if exam.get('examOddNum', 0) > 0 and exam.get('examScore', 0) < 100), None)
        
        if not todo_exam:
            print("所有考试都已完成!")
            continue
            
        print_exam(todo_exam)
        
        # 开始考试并应用答案
        start_exam_with_callback(page, todo_exam, lambda question, answers: apply_exam_answer(question, answers, exam_answers))

def navigate_to_exam_page(page):
    """导航到考试页面"""
    try:
        # 导航到项目页面
        page.goto("https://weiban.mycourse.cn/#/courseChoose")
        page.wait_for_load_state("networkidle")
        
        # 等待页面加载完成
        time.sleep(2)
        
        # 查找考试按钮或链接
        exam_tab = page.locator("text=考试")
        if exam_tab.count() > 0:
            exam_tab.first.click()
            print("成功导航到考试页面")
            return True
        else:
            print("未找到考试标签，尝试其他方法...")
            # 尝试直接访问考试URL
            page.goto("https://weiban.mycourse.cn/#/exam")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            print("已尝试直接访问考试页面")
            return True
            
    except Exception as e:
        print(f"导航到考试页面时出错: {e}")
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
    
    # 导航到考试页面
    if not navigate_to_exam_page(page):
        print("导航到考试页面失败")
        
    # 获取用户信息
    user_info = get_user_info(page)
    if not user_info:
        print("无法获取用户信息，请确保已登录")
        input("\n按任意键退出...")
        return
        
    # 处理考试
    take_all_exams(page)
    
    print("考试处理完成！")
    input("按任意键退出...")
    
if __name__ == "__main__":
    main()