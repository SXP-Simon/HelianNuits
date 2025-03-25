import os
from datetime import datetime

def on_files(files, config):
    """
    在 MkDocs 收集文件时触发。
    动态生成博客文章列表页面。
    """
    # 获取博客文章目录
    blog_dir = os.path.join(config['docs_dir'], 'blog/posts')
    if not os.path.exists(blog_dir):
        os.makedirs(blog_dir)  # 如果 blog 目录不存在，则创建

    posts = [f for f in os.listdir(blog_dir) if f.endswith('.md') and f != 'index.md']

    # 生成博客文章列表内容
    blog_list_content = "# 博客文章列表\n\n"
    for post in posts:
        post_path = os.path.join(blog_dir, post)
        with open(post_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()  # 读取文章标题（假设标题是第一行）
            if first_line.startswith('# '):
                title = first_line[2:].strip()
            else:
                title = post.replace('.md', '')

        # 添加文章链接和标题
        blog_list_content += f"- [{title}]({post})\n"

    # 将生成的博客文章列表写入 index.md
    blog_index_path = os.path.join(blog_dir, 'index.md')
    with open(blog_index_path, 'w', encoding='utf-8') as f:
        f.write(blog_list_content)

    return files

def on_page_markdown(markdown, page, config, files):
    """
    在生成 Markdown 内容时触发。
    在每篇博客文章的顶部插入发布日期。
    """
    if page.file.src_path.replace('\\', '/').startswith('blog/') and page.file.src_path != 'blog/index.md':
        # 检查是否已经包含发布日期
        if not markdown.startswith('**发布日期：'):
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            # 在文章顶部插入发布日期
            markdown = f"**发布日期：{today}**\n\n" + markdown
    return markdown

def on_post_build(config):
    """
    在构建完成后触发。
    打印一条构建成功的通知。
    """
    print("博客构建成功！文章列表已更新，发布日期已添加。")