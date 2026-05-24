# ============================================================
# 0. IMPORTS
# ============================================================

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import pickle
import os
import time
import pandas as pd
import random
import re

from datetime import date, timedelta, datetime


# ============================================================
# 1. CONFIG
# （仅集中配置，不改行为）
# ============================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
]

WINDOW_SIZES = [
    "1920,1080",
    "1366,768",
    "1536,864"
]

KEYWORDS = [
    '马德里攻略',
    '马德里旅行攻略',
    '马德里旅行',
    '马德里旅游'
]

COOKIE_FILE = "xhs_cookies.pkl"

NOTE_OUTPUT_FILE = "xhs正文数据集.xlsx"

COMMENT_OUTPUT_FILE = "xhs一级评论数据集.xlsx"

TARGET_COUNT = 200

MAX_CONSECUTIVE_ERRORS = 10

MAX_SINGLE_LOOP_ERROR = 5

WAIT_TIMEOUT = 8


# ============================================================
# 2. DRIVER
# （完全保留你的反爬逻辑）
# ============================================================

def create_stealth_driver():

    options = Options()

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        'useAutomationExtension',
        False
    )

    options.add_argument(
        f"--user-agent={random.choice(USER_AGENTS)}"
    )

    options.add_argument(
        f"--window-size={random.choice(WINDOW_SIZES)}"
    )

    options.add_argument("--disable-extensions")

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Edge(
        options=options
    )

    driver.execute_script(
        """
        Object.defineProperty(
            navigator,
            'webdriver',
            {get: () => undefined}
        )
        """
    )

    return driver


# ============================================================
# 3. COOKIE LOGIN
# （逻辑保持原样）
# ============================================================

def ensure_cookie():

    if os.path.exists(COOKIE_FILE):

        print("Cookie存在")

        return

    print("Cookie不存在，开始登录")

    login_driver = create_stealth_driver()

    login_driver.get(
        'https://www.xiaohongshu.com/explore'
    )

    input("登录完成后按回车，后续自动登录时可能需要手动选择页面cookie")

    cookies = login_driver.get_cookies()

    with open(
        COOKIE_FILE,
        "wb"
    ) as f:

        pickle.dump(cookies, f)

    login_driver.quit()


# ============================================================
# 4. HUMAN BEHAVIOR UTILS
# （你的反检测逻辑全部保留）
# ============================================================

def human_like_delay(
        min_sec=2,
        max_sec=5
):

    """随机延迟，模拟阅读行为"""

    time.sleep(
        random.uniform(
            min_sec,
            max_sec
        )
    )


def random_mouse_movements(driver):

    """随机鼠标移动"""

    try:

        actions = ActionChains(driver)

        window_size = driver.get_window_size()

        safe_max_x = window_size['width'] - 50

        safe_max_y = window_size['height'] - 50

        body = driver.find_element(
            By.TAG_NAME,
            'body'
        )

        start_x = random.randint(
            50,
            safe_max_x // 2
        )

        start_y = random.randint(
            50,
            safe_max_y // 2
        )

        actions.move_by_offset(
            start_x,
            start_y
        )

        for _ in range(
                random.randint(2, 4)
        ):

            move_x = random.randint(-80, 80)

            move_y = random.randint(-35, 35)

            actions.move_by_offset(
                move_x,
                move_y
            )

            actions.pause(
                random.uniform(
                    0.1,
                    0.3
                )
            )

        actions.perform()

        return True

    except Exception as e:

        print(
            f'鼠标位置出错了，报错为{e}'
        )

        try:

            actions.move_to_element_with_offset(
                body,
                100,
                100
            ).perform()

        except:
            pass

        return False


def human_like_typing(
        element,
        text
):

    """模拟人类输入"""

    for char in text:

        element.send_keys(char)

        time.sleep(
            random.uniform(
                0.1,
                0.3
            )
        )

    human_like_delay(
        0.5,
        1.5
    )


def human_like_scroll(
        driver,
        scroll_times=1
):

    """人类式滚动"""

    current_scroll = driver.execute_script(
        "return window.pageYOffset;"
    )

    window_height = driver.execute_script(
        "return window.innerHeight;"
    )

    for _ in range(scroll_times):

        scroll_amount = random.randint(
            int(window_height * 0.5),
            int(window_height * 0.8)
        )

        target_scroll = (
                current_scroll
                + scroll_amount
        )

        scroll_script = f"""
            window.scrollTo({{
                top:{target_scroll},
                behavior:'smooth'
            }});
        """

        driver.execute_script(
            scroll_script
        )

        human_like_delay(
            2,
            3
        )

        current_scroll = target_scroll

    if random.random() > 0.9:

        driver.execute_script(
            "window.scrollBy(0,-100);"
        )

        human_like_delay(
            0.5,
            1
        )

# ============================================================
# 5. SAVE FUNCTIONS
# （仅统一出口，不改行为）
# ============================================================

def save_note_to_excel(
        data_list,
        filename=NOTE_OUTPUT_FILE
):

    df = pd.DataFrame(data_list)

    df.to_excel(
        filename,
        index=False
    )

    print(
        f"数据已保存到: {filename}"
    )

    print(
        f"共保存了 {len(data_list)} 条笔记"
    )


def save_comment_to_excel(
        data_list,
        filename=COMMENT_OUTPUT_FILE
):

    df = pd.DataFrame(data_list)

    df.to_excel(
        filename,
        index=False
    )

    print(
        f"数据已保存到: {filename}"
    )

    print(
        f"共保存了 {len(data_list)} 条评论"
    )


# ============================================================
# 6. DATE PARSER
# （完全保留你的日期兼容逻辑）
# ============================================================

def convert_to_yyyymmdd(rq):

    """日期格式标准化"""

    today = date.today()

    if '编辑于' in rq:

        rq = re.sub(
            r'编辑于\s*',
            '',
            rq
        )

    pattern = r'^(\d{1,2})-(\d{1,2})(?:\s+|\s*)([^\d\s].*)?$'

    match = re.match(
        pattern,
        rq
    )

    if match:

        month = int(
            match.group(1)
        )

        day = int(
            match.group(2)
        )

        candidate_date = datetime(
            today.year,
            month,
            day
        )

        if candidate_date <= datetime(
                today.year,
                today.month,
                today.day
        ):

            return candidate_date.strftime(
                '%Y%m%d'
            )

        else:

            prev_year_date = datetime(
                today.year - 1,
                month,
                day
            )

            return prev_year_date.strftime(
                '%Y%m%d'
            )

    if re.match(
            r'^\d+分钟前\s*',
            rq
    ) or re.match(
            r'^\d+小时前\s*',
            rq
    ):

        return today.strftime(
            '%Y%m%d'
        )

    if '昨天' in rq:

        yesterday = today - timedelta(days=1)

        return yesterday.strftime(
            '%Y%m%d'
        )

    if re.match(
            r'^\d+天前\s*',
            rq
    ):

        days_ago = int(
            re.match(
                r'^(\d+)天前',
                rq
            ).group(1)
        )

        result_date = (
                today
                - timedelta(days=days_ago)
        )

        return result_date.strftime(
            '%Y%m%d'
        )

    if re.match(
            r'^\d{1,2}-\d{1,2}$',
            rq
    ):

        month, day = map(
            int,
            rq.split('-')
        )

        candidate_date = datetime(
            today.year,
            month,
            day
        )

        if candidate_date <= datetime(
                today.year,
                today.month,
                today.day
        ):

            return candidate_date.strftime(
                '%Y%m%d'
            )

        else:

            prev_year_date = datetime(
                today.year - 1,
                month,
                day
            )

            return prev_year_date.strftime(
                '%Y%m%d'
            )

    if re.match(
            r'^(\d{4})-(\d{1,2})-(\d{1,2})$',
            rq
    ):

        match_date = re.match(
            r'^(\d{4})-(\d{1,2})-(\d{1,2})$',
            rq
        )

        year, month, day = map(
            int,
            match_date.groups()
        )

        return datetime(
            year,
            month,
            day
        ).strftime('%Y%m%d')

    return rq


# ============================================================
# 7. SEARCH
# （保持原逻辑）
# ============================================================

def search_keyword(keyword):

    search_box = driver.find_element(
        By.CSS_SELECTOR,
        "[id='search-input']"
    )

    driver.execute_script(
        "arguments[0].click();",
        search_box
    )

    random_mouse_movements(driver)

    human_like_delay(
        1,
        2
    )

    search_box.clear()

    human_like_typing(
        search_box,
        keyword
    )

    search_box.send_keys(
        Keys.RETURN
    )

    time.sleep(5)


# ============================================================
# 8. COMMENT CRAWLER
# （完全保留防报错+评论逻辑）
# ============================================================

def find_first_comment(
        note_id,
        note_counts_real
):

    print(
        f"  💬 开始爬取笔记 {note_id} 的评论..."
    )

    target_count = (
        int(note_counts_real[2])
        if (
            note_counts_real[2]
            and note_counts_real[2].isdigit()
        )
        else 0
    )

    print(
        f"  📈 目标评论数: {target_count}"
    )

    if target_count == 0:

        return []

    element = driver.find_element(
        By.CLASS_NAME,
        "comments-container"
    )

    ActionChains(driver).move_to_element(
        element
    ).perform()

    ind_comment_list = []

    scroll_increment = random.randint(
        200,
        600
    )

    driver.execute_script(
        f"""
        arguments[0].scrollTop += {scroll_increment}
        """,
        element
    )

    first_level_comments = driver.find_elements(
        By.XPATH,
        "//div[@class='comment-item']"
    )

    for comment in first_level_comments:

        try:

            comment_1 = comment.find_element(
                By.XPATH,
                ".//div[@class='content']//span[@class='note-text']"
            ).text

            c_author = comment.find_element(
                By.XPATH,
                ".//div[@class='author']"
            ).text

            date_rough_text = comment.find_element(
                By.XPATH,
                ".//div[@class='date']"
            ).text

            date_text = convert_to_yyyymmdd(
                date_rough_text
            )

            location = comment.find_element(
                By.XPATH,
                ".//span[@class='location']"
            ).text

            like_count = comment.find_element(
                By.XPATH,
                ".//div[@class='like']//span[@class='count']"
            ).text

            if like_count == '赞':

                like_count = 0

            sub_comment_count = comment.find_element(
                By.XPATH,
                ".//div[@class='reply icon-container']//span[@class='count']"
            ).text

            if sub_comment_count == '回复':

                sub_comment_count = 0

            comment_info = {

                'note_id': note_id,

                'context': comment_1,

                'c_author': c_author,

                'date': date_text,

                'location': location,

                'like_count': like_count,

                'response_count': sub_comment_count
            }

            ind_comment_list.append(
                comment_info
            )

        except Exception as e:

            print(
                f"爬取评论信息时出错: {e}"
            )

            continue

    print(
        f'已经爬取{len(ind_comment_list)}条一级评论'
    )

    return ind_comment_list

# ============================================================
# 9. MAIN CRAWLER
# （极保守重构版，不改运行逻辑）
# ============================================================

def get_fluently():

    wait = WebDriverWait(
        driver,
        WAIT_TIMEOUT
    )

    note_list = []

    comment_list = []

    last_title = None

    current_count = 0

    empty_title_count = 0

    consecutive_errors = 0

    while current_count < TARGET_COUNT:

        print(
            f"\n=== 第 {current_count+1}/{TARGET_COUNT} 个笔记 ==="
        )

        # ====================================================
        # 连续错误保护
        # ====================================================

        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:

            print(
                "⚠️ 连续错误达到10次，可能Cookie失效，保存数据并退出..."
            )

            if note_list:

                save_note_to_excel(
                    note_list
                )

                save_comment_to_excel(
                    comment_list
                )

                print(
                    "💾 已保存数据到Excel"
                )

            driver.quit()

            return (
                note_list,
                comment_list
            )

        # ====================================================
        # 获取当前页卡片
        # ====================================================

        try:

            note_cards = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "[class = 'title']"
                    )
                )
            )

            print(
                f"📝 当前页面发现 {len(note_cards)} 个笔记卡片"
            )

            consecutive_errors = 0

        except Exception as e:

            consecutive_errors += 1

            print(
                f"❌ 查找笔记卡片失败 "
                f"(错误 {consecutive_errors}/10):{e}"
            )

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:

                continue

            time.sleep(2)

            continue

        # ====================================================
        # 过滤空标题
        # ====================================================

        valid_indices = []

        valid_cards = []

        valid_titles = []

        for i, card in enumerate(note_cards):

            try:

                title_element = driver.find_elements(
                    By.CLASS_NAME,
                    'title'
                )[i]

                title_text = (
                    title_element.text.strip()
                )

                if title_text:

                    valid_indices.append(i)

                    valid_cards.append(card)

                    valid_titles.append(
                        title_text
                    )

                else:

                    print(
                        f"⚠️ 跳过第 {i+1} 个空标题卡片"
                    )

            except:

                pass

        # ====================================================
        # 空列表保护
        # ====================================================

        if not valid_titles:

            empty_title_count += 1

            print(
                f"⚠️ 第 {empty_title_count} 次获取到空标题列表"
            )

            if empty_title_count >= 3:

                print(
                    "❌ 连续三次获取到空标题列表，"
                    "可能已到底部，退出爬取"
                )

                break

            consecutive_errors += 1

            human_like_scroll(
                driver
            )

            time.sleep(2)

            continue

        else:

            empty_title_count = 0

            consecutive_errors = 0

        print(
            f'✔ 提取到有效标题 {len(valid_titles)} 个'
        )

        # ====================================================
        # 找到断点位置
        # ====================================================

        try:

            start_index = (
                valid_titles.index(last_title)
                if last_title
                else -1
            )

        except ValueError:

            start_index = -1

        error_count = 0

        # ====================================================
        # 遍历笔记
        # ====================================================

        for idx_in_valid in range(
                start_index + 1,
                len(valid_cards)
        ):

            if current_count >= TARGET_COUNT:

                print(
                    f"✅ 已达到目标数量 "
                    f"{TARGET_COUNT}，停止爬取"
                )

                if note_list:

                    save_note_to_excel(
                        note_list
                    )

                    save_comment_to_excel(
                        comment_list
                    )

                return (
                    note_list,
                    comment_list
                )

            if error_count >= MAX_SINGLE_LOOP_ERROR:

                print(
                    '连续错误达到五次，退出循环'
                )

                if note_list:

                    save_note_to_excel(
                        note_list
                    )

                    save_comment_to_excel(
                        comment_list
                    )

                break

            card = valid_cards[
                idx_in_valid
            ]

            current_title = valid_titles[
                idx_in_valid
            ]

            try:

                # ============================================
                # 打开笔记
                # ============================================

                print(
                    f"📖 正在处理第 "
                    f"{current_count+1}/"
                    f"{TARGET_COUNT} 个笔记..."
                )

                print(
                    f"  标题: "
                    f"{current_title[:50]}..."
                )

                card.click()

                human_like_delay()

                # ============================================
                # 登录保护
                # ============================================

                if (
                        "login"
                        in driver.current_url
                        or
                        "signin"
                        in driver.current_url
                ):

                    print(
                        "⚠️ 检测到登录页面，"
                        "Cookie可能已失效"
                    )

                    consecutive_errors = 10

                    driver.back()

                    time.sleep(2)

                    break

                # ============================================
                # 提取正文信息
                # ============================================

                note_body = driver.find_element(
                    By.ID,
                    "detail-desc"
                )

                note_url = driver.current_url

                id_match = re.search(
                    '(6[a-zA-Z0-9]{23})',
                    note_url
                )

                if id_match:

                    note_id = (
                        id_match.group(1)
                    )

                else:

                    note_id = 'NotFound'

                note_username = driver.find_element(
                    By.XPATH,
                    "//span[@class='username']"
                )

                note_date_rough = driver.find_element(
                    By.CLASS_NAME,
                    "date"
                )

                note_date_fine = convert_to_yyyymmdd(
                    note_date_rough.text
                )

                date_text = (
                    note_date_rough.text
                )

                parts = date_text.split(
                    ' '
                )

                location = (
                    parts[-1]
                    if (
                            len(parts) > 1
                            and
                            not re.match(
                                r'\d',
                                parts[-1]
                            )
                    )
                    else ""
                )

                # ============================================
                # tag
                # ============================================

                note_tag_list = driver.find_elements(
                    By.ID,
                    "hash-tag"
                )

                note_tag = []

                for tag in note_tag_list:

                    note_tag.append(
                        tag.text
                    )

                # ============================================
                # counts
                # ============================================

                note_counts_list = driver.find_elements(
                    By.CLASS_NAME,
                    "count"
                )

                note_counts = []

                for counts in note_counts_list:

                    note_counts.append(
                        counts.text
                    )

                note_counts_real = (
                    note_counts[-3:]
                )

                if note_counts_real[0] == '点赞':

                    note_counts_real[0] = 0

                if note_counts_real[1] == '收藏':

                    note_counts_real[1] = 0

                if note_counts_real[2] == '评论':

                    note_counts_real[2] = 0

                # ============================================
                # note dict
                # ============================================

                note_info = {

                    'id': note_id,

                    'title': current_title,

                    'note_url':
                        note_url,

                    'body':
                        note_body.text,

                    'date':
                        note_date_fine,

                    'location':
                        location,

                    'tag':
                        note_tag,

                    'likes':
                        note_counts_real[0],

                    'collection':
                        note_counts_real[1],

                    'comment':
                        note_counts_real[2]
                }

                note_list.append(
                    note_info
                )

                print(
                    f"  📊 笔记统计 - "
                    f"点赞:{note_counts_real[0]}, "
                    f"收藏:{note_counts_real[1]}, "
                    f"评论:{note_counts_real[2]}"
                )

                # ============================================
                # 评论
                # ============================================

                ind_comment_list = (
                    find_first_comment(
                        note_id,
                        note_counts_real
                    )
                )

                comment_list.extend(
                    ind_comment_list
                )

                # ============================================
                # 返回上一页
                # ============================================

                driver.back()

                time.sleep(2)

                error_count = 0

                consecutive_errors = 0

                current_count += 1

                last_title = current_title

            except Exception as e:

                error_count += 1

                consecutive_errors += 1

                print(
                    f'错误次数{error_count}/5 '
                    f'(总连续错误 '
                    f'{consecutive_errors}/10)，'
                    f'在提取第'
                    f'{current_count+1}'
                    f'条时出错：{e}'
                )

                try:

                    driver.back()

                    time.sleep(2)

                except:

                    pass

                if (
                        error_count
                        >= MAX_SINGLE_LOOP_ERROR
                        or
                        consecutive_errors
                        >= MAX_CONSECUTIVE_ERRORS
                ):

                    break

        # ====================================================
        # 当前轮保存
        # ====================================================

        if note_list:

            save_note_to_excel(
                note_list
            )

            save_comment_to_excel(
                comment_list
            )

            print(
                "💾 当前轮次数据已保存到Excel"
            )

        if current_count >= TARGET_COUNT:

            print(
                f"✅ 已达到目标数量 "
                f"{TARGET_COUNT}，停止爬取"
            )

            break

        # ====================================================
        # 翻页滚动
        # ====================================================

        human_like_scroll(
            driver
        )

    # ========================================================
    # 最终保存
    # ========================================================

    if note_list:

        save_note_to_excel(
            note_list
        )

        save_comment_to_excel(
            comment_list
        )

        print(
            "💾 最终数据已保存到Excel"
        )

    return (
        note_list,
        comment_list
    )

# ============================================================
# 10. MAIN
# （启动流程整理版，不改运行行为）
# ============================================================

ensure_cookie()

driver = create_stealth_driver()

driver.get(
    'https://www.xiaohongshu.com/explore'
)

# ============================================================
# LOAD COOKIE
# ============================================================

with open(
        COOKIE_FILE,
        "rb"
) as f:

    saved_cookies = pickle.load(f)

for cookie in saved_cookies:

    driver.add_cookie(cookie)

driver.refresh()

time.sleep(15)

# ============================================================
# GLOBAL RESULT CONTAINER
# ============================================================

all_notes = []

all_comments = []

# ============================================================
# KEYWORD LOOP
# ============================================================

for keyword in KEYWORDS:

    print(
        f"\n开始搜索: {keyword}"
    )

    try:

        search_keyword(
            keyword
        )

        note_list, comment_list = (
            get_fluently()
        )

        all_notes.extend(
            note_list
        )

        all_comments.extend(
            comment_list
        )

        print(
            f"✔ 完成关键词: {keyword}"
        )

    except Exception as e:

        print(
            f"❌ 关键词 {keyword} "
            f"执行失败: {e}"
        )

        continue

# ============================================================
# FINAL SAVE
# ============================================================

save_note_to_excel(
    all_notes
)

save_comment_to_excel(
    all_comments
)

print(
    "\n===== 全部任务完成 ====="
)

print(
    f"正文总数: {len(all_notes)}"
)

print(
    f"评论总数: {len(all_comments)}"
)

driver.quit()