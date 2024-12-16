from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import requests
from typing import Any, List, Tuple

def get_page_user_posts(page_url: str, user_id: str, page: int) -> List[str]:
    '''
    @param page_url: url of the page to fetch the content
    @param user_id: The id of the user whose posts to fetch
    @param page: Helping ignore the initial post of Po主 appears in all except the first page
    @return posts: A list of all posts of given user
    '''
    # 发送HTTP请求获取页面内容
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f"Failed to retrieve page {page}")
        return []

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts = []
    # 查找所有包含用户ID的帖子
    for uid_span in soup.find_all('span', class_='h-threads-info-uid'):
        if f'ID:{user_id}' in uid_span.text:
            # 找到共同的父级元素
            parent_div = uid_span.find_parent("div", class_="h-threads-info")
            if parent_div:
                # 在共同父级元素中查找发言内容
                # Observing the source code, the next sibling of <div> "h-threads-info" is <div> "h-threads-content"
                # See the example.html for some intuition
                content_div = parent_div.find_next_sibling("div", class_='h-threads-content')
                if content_div:
                    # 清除内部的HTML标签，保留纯文本
                    content_text = ''.join(content_div.stripped_strings)
                    posts.append(content_text)

    # Remove duplicate inital Po主 post
    return posts if (page == 1 or posts == None) else posts[1:]

def save_posts_to_txt(posts: List[str], page: int, user_id: str, filename: str = 'No0_0_posts.txt', save_path: Optional[str] = None) -> None:
    """
    将获取到的一页帖子内容保存到一个文本文件中。
    
    :param posts: 包含一页帖子内容的列表
    :param page: 当前页数
    :param user_id: 用户ID
    :param filename: 输出文件名，默认为 'No0_0_posts.txt'
    :param save_path: 保存文件的路径，默认为当前工作目录
    """
    # 构建完整的文件路径
    if save_path:
        full_path = os.path.join(save_path, filename)
    else:
        full_path = filename
    
    # 确保保存路径存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'a+', encoding='utf-8') as file:
        file.write(f"Page {page}    Poster {user_id}\n\n\n")
        if not posts:  # 检查posts是否为空或None
            file.write("No post")
        else:
            for idx, post_content in enumerate(posts, 1):
                file.write(f"Post {idx}:\n{post_content}\n{'-' * 80}\n")
    
    print(f"Save page {page} successfully to {full_path}")

def save_all_posts_given_base_url(base_url: str, page_range: Tuple[int, int], user_id: str) -> None:
    '''
    Get the posts the given user, for all pages of the entire thread, then save it to text file
    Because the feacture of x岛, each page will contains the initial post,
    so ignore it in the following pages
    @param base_url: the url of the thread, without the page part
    '''
    url = base_url + "?page={}"
    pages_to_check = range(page_range[0], page_range[1] + 1)
    thread_number = base_url.split('/')[-1]

    # Name file with current time to avoid duplication
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = 'No' + thread_number + '_' + user_id + "_posts_" + current_time + ".txt"

    print(f"Fetching posts of {user_id}...\n")
    for page in pages_to_check:
        page_url = url.format(page)
        posts = get_page_user_posts(page_url, user_id, page)
        
        print(f"Fetch page {page} posts successfully")
        save_posts_to_txt(posts=posts, page=page, user_id=user_id, filename=filename)

def save_all_posts_given_thread_number(thread_number: str, page_range: Tuple[int, int], user_id: str) -> None:
    '''
    @param thread_number: 串号，预期只有数字
    '''
    base_url = 'https://www.nmbxd1.com/t/' + thread_number
    save_all_posts_given_base_url(base_url, page_range, user_id) 

def save_all_posts_single_user(user_input: str, page_range: Tuple[int, int], user_id: str) -> None:
    '''
    @param user_input: 预期接受url(不包含page), No.串号, 纯数字串号三种格式
    ''' 
    url_pattern = r'^https://www\.nmbxd1\.com/t/\d+$'
    no_pattern = r'^No\.\d+$'
    num_pattern = r'^\d+$'

    if re.match(url_pattern, user_input):
        save_all_posts_given_base_url(user_input, page_range, user_id)
    elif re.match(no_pattern, user_input):
        thread_number = user_input.split('.')[1]
        save_all_posts_given_thread_number(thread_number, page_range, user_id)
    elif re.match(num_pattern, user_input):
        save_all_posts_given_thread_number(user_input, page_range, user_id)
    else:
        print(f"Error: Input '{user_input}' does not match any expected format.")
        return None

    print("Done\n")

def save_all_posts_multi_users(user_input: str, page_ranges: List[Tuple[int, int]], user_ids: List[str]) -> None:
    for (page_range, user_id) in zip(page_ranges, user_ids):
        save_all_posts_single_user(user_input, page_range, user_id)
         
if __name__ == "__main__":
    base_url = 'https://www.nmbxd1.com/t/60184882'
    page_ranges = [(1, 8), (8, 14)]
    user_ids = ['fyBPEP5', 'LhWkRsO']
    save_all_posts_multi_users(user_input=base_url, page_ranges=page_ranges, user_ids=user_ids)
