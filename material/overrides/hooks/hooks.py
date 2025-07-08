"""
MkDocs 自定义钩子函数模块

本模块为 MkDocs 静态站点生成器提供自定义钩子函数，
用于自动生成博客文章列表、归档页面和分类页面。

主要功能：
1. 自动扫描博客文章目录
2. 提取文章元数据（标题、日期、分类、标签等）
3. 生成最新文章列表页面
4. 生成时间归档页面
5. 生成分类浏览页面
6. 自动更新 MkDocs 导航配置

作者: Helian Nuits
创建时间: 2025年
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from ruamel.yaml import YAML

# ==================== 全局配置常量 ====================

# 获取当前 hooks.py 文件的绝对路径
HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（hooks.py 在 material/overrides/hooks/ 下，向上三级）
PROJECT_ROOT = os.path.abspath(os.path.join(HOOKS_DIR, '..', '..', '..'))
# MkDocs 配置文件路径
MKDOCS_YML = os.path.join(PROJECT_ROOT, 'mkdocs.yml')
# 博客文章目录路径
POSTS_DIR = os.path.join(PROJECT_ROOT, 'docs', 'blog', 'posts')

# ==================== 工具函数 ====================

def slugify(s):
    """
    将字符串转换为 URL 友好的 slug
    
    Args:
        s (str): 输入字符串
        
    Returns:
        str: 转换后的 slug，只包含字母、数字、中文字符和连字符
    """
    return re.sub(r'[^\w\u4e00-\u9fa5-]+', '-', s).strip('-').lower()

def get_post_url(post):
    """
    根据文章信息生成文章链接
    
    Args:
        post (dict): 包含文章信息的字典
        
    Returns:
        str: 文章的 URL 路径
    """
    filename = post['filename']
    name = os.path.splitext(filename)[0]
    # 使用绝对路径，确保链接始终指向正确的地址
    return f"/HelianNuits/blog/posts/{name}/"

# ==================== 主要钩子函数 ====================

def on_files(files, config):
    """
    在文件处理时自动生成博客页面
    
    这是 MkDocs 的核心钩子函数，在文件处理阶段被调用。
    负责扫描博客文章并生成相关的索引页面。
    同时处理文章的增删，自动更新导航配置。
    
    Args:
        files: MkDocs 文件对象
        config: MkDocs 配置对象
        
    Returns:
        files: 处理后的文件对象
    """
    print("=== 开始执行on_files钩子 ===")
    generate_blog_pages(config)

    # 检查导航中的文章是否都存在，如果有文章被删除则更新导航
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(MKDOCS_YML, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
    
    nav = data.get('nav', [])
    need_update = False

    def check_posts_existence(items):
        nonlocal need_update
        for item in items:
            if isinstance(item, dict):
                if '博客' in item:
                    blog_nav = item['博客']
                    for sub in blog_nav:
                        if isinstance(sub, dict) and '文章列表' in sub:
                            post_list = sub['文章列表']
                            for post in post_list:
                                if isinstance(post, dict):
                                    for title, path in post.items():
                                        if path.startswith('blog/posts/'):
                                            full_path = os.path.join(PROJECT_ROOT, 'docs', path)
                                            if not os.path.exists(full_path):
                                                print(f"导航中存在不存在的文章: {path}，将自动更新导航配置。")
                                                need_update = True
                                                return
                elif any(isinstance(v, list) for v in item.values()):
                    for v in item.values():
                        if isinstance(v, list):
                            check_posts_existence(v)

    check_posts_existence(nav)
    
    # 检查是否有新文章被添加
    current_posts = set()
    if os.path.exists(POSTS_DIR):
        for fname in os.listdir(POSTS_DIR):
            if fname.endswith('.md'):
                current_posts.add(f'blog/posts/{fname}')

    def get_nav_posts(items):
        posts = set()
        for item in items:
            if isinstance(item, dict):
                if '博客' in item:
                    blog_nav = item['博客']
                    for sub in blog_nav:
                        if isinstance(sub, dict) and '文章列表' in sub:
                            post_list = sub['文章列表']
                            for post in post_list:
                                if isinstance(post, dict):
                                    for path in post.values():
                                        if path.startswith('blog/posts/'):
                                            posts.add(path)
                elif any(isinstance(v, list) for v in item.values()):
                    for v in item.values():
                        if isinstance(v, list):
                            posts.update(get_nav_posts(v))
        return posts

    nav_posts = get_nav_posts(nav)
    
    # 如果有新文章或文章被删除，更新导航
    if current_posts != nav_posts:
        need_update = True

    if need_update:
        update_mkdocs_nav()
        
    print("=== on_files钩子执行完成 ===")
    return files

def on_page_markdown(markdown, page, config, files):
    """
    在生成 Markdown 内容时触发
    
    为博客文章自动添加发布日期信息。
    
    Args:
        markdown (str): 页面的 Markdown 内容
        page: 页面对象
        config: MkDocs 配置对象
        files: 文件对象
        
    Returns:
        str: 处理后的 Markdown 内容
    """
    # 检查是否为博客文章页面（排除博客首页）
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
    在构建完成后生成博客页面
    
    作为备用钩子，确保在构建完成后也能生成博客页面。
    
    Args:
        config: MkDocs 配置对象
    """
    print("=== 开始执行on_post_build钩子 ===")
    generate_blog_pages(config)
    print("=== on_post_build钩子执行完成 ===")

# ==================== 博客页面生成函数 ====================

def generate_blog_pages(config):
    """
    生成博客相关页面的主函数
    
    负责协调生成所有博客相关的页面，包括：
    - 最新文章列表页面
    - 时间归档页面
    - 分类浏览页面
    
    Args:
        config: MkDocs 配置对象
    """
    docs_dir = Path(config['docs_dir'])
    posts_dir = docs_dir / 'blog' / 'posts'
    
    # 检查文章目录是否存在
    if not posts_dir.exists():
        return
    
    # 收集所有博客文章
    posts = []
    for post_file in posts_dir.glob('*.md'):
        # 跳过以下划线开头的文件（通常是草稿或模板）
        if post_file.name.startswith('_'):
            continue
            
        post_info = extract_post_info(post_file)
        if post_info:
            posts.append(post_info)
    
    # 按日期排序（最新的在前）
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    # 生成各种博客页面
    generate_latest_posts_page(docs_dir, posts, config)
    generate_archive_page(docs_dir, posts)
    generate_categories_page(docs_dir, posts)
    
    print("博客构建成功！文章列表和归档已自动生成。")

def extract_post_info(post_file):
    """
    从 Markdown 文件中提取文章信息
    
    解析文章的 front matter 部分，提取标题、日期、分类、标签等信息。
    
    Args:
        post_file (Path): 文章文件路径
        
    Returns:
        dict: 包含文章信息的字典，如果解析失败返回 None
    """
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 front matter（YAML 格式的元数据）
        front_matter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not front_matter_match:
            return None
        
        front_matter = yaml.safe_load(front_matter_match.group(1))
        
        # 提取标题（如果没有则使用文件名）
        title = front_matter.get('title', post_file.stem)
        
        # 提取并解析日期
        date_str = front_matter.get('date', '2025-01-01')
        if isinstance(date_str, str):
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # 如果日期格式错误，使用默认日期
                date = datetime(2025, 1, 1)
        else:
            date = date_str
        
        # 提取分类（确保是列表格式）
        categories = front_matter.get('categories', [])
        if isinstance(categories, str):
            categories = [categories]
        
        # 提取标签（确保是列表格式）
        tags = front_matter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        # 提取描述和作者信息
        description = front_matter.get('description', '')
        author = front_matter.get('author', 'Helian Nuits')
        
        return {
            'title': title,
            'date': date,
            'categories': categories,
            'tags': tags,
            'description': description,
            'author': author,
            'filename': post_file.name,
        }
    except Exception as e:
        print(f"处理文章 {post_file} 时出错: {e}")
        return None

def generate_latest_posts_page(docs_dir, posts, config):
    """
    生成最新文章列表页面
    
    创建一个展示最新博客文章的页面，包含文章卡片、元数据和链接。
    
    Args:
        docs_dir (Path): 文档目录路径
        posts (list): 文章信息列表
        config: MkDocs 配置对象
    """
    blog_dir = docs_dir / 'blog'
    blog_dir.mkdir(exist_ok=True)
    
    # 生成最新文章卡片 HTML
    latest_posts_html = ""
    for post in posts[:10]:  # 显示最新10篇文章
        date_str = post['date'].strftime('%Y年%m月%d日')
        
        # 生成分类标签 HTML
        categories_html = ""
        if post['categories']:
            categories_html = f'<span class="category-tag">{", ".join(post["categories"])}</span>'
        
        url = get_post_url(post)
        latest_posts_html += f'''
<div class="post-card" markdown>
<div class="post-header">
  <h3 class="post-title">
    <a href="{url}">{post['title']}</a>
  </h3>
  <div class="post-meta">
    <span class="post-date">📅 {date_str}</span>
    {categories_html}
  </div>
</div>
<div class="post-excerpt">
  {post['description'] or '暂无描述'}
</div>
<div class="post-footer">
  <span class="post-author">👤 {post['author']}</span>
  <a href="{url}" class="read-more">阅读全文 →</a>
</div>
</div>
'''
    
    # 生成 RSS 订阅链接
    site_url = config.get('site_url', '/')
    if site_url and not site_url.endswith('/'):
        site_url += '/'
    rss_url = f"{site_url}feed_rss_created.xml"
    
    # 生成完整的 index.md 内容
    index_content = f'''---
title: 博客文章
description: 最新博客文章列表
---

# 📝 最新文章

<div class="posts-grid" markdown>

{latest_posts_html}

</div>

---

<div class="more-posts" markdown>

## 📚 更多文章

- [:octicons-archive-24: 时间归档](archive.md) - 按时间浏览所有文章
- [:octicons-tag-24: 分类浏览](categories.md) - 按分类浏览文章
- [:octicons-rss-24: RSS订阅]({rss_url}) - 订阅最新文章

</div>
'''
    
    # 写入文件
    with open(blog_dir / 'index.md', 'w', encoding='utf-8') as f:
        f.write(index_content)

def generate_archive_page(docs_dir, posts):
    """
    生成时间归档页面
    
    按年份和月份组织文章，创建时间归档页面。
    
    Args:
        docs_dir (Path): 文档目录路径
        posts (list): 文章信息列表
    """
    blog_dir = docs_dir / 'blog'
    
    # 按年份和月份分组文章
    archive_by_date = defaultdict(lambda: defaultdict(list))
    for post in posts:
        year = post['date'].year
        month = post['date'].month
        archive_by_date[year][month].append(post)
    
    # 生成归档内容 HTML
    archive_html = ""
    for year in sorted(archive_by_date.keys(), reverse=True):
        archive_html += f'<div class="archive-year" markdown>\n\n## {year}年\n\n'
        
        for month in sorted(archive_by_date[year].keys(), reverse=True):
            month_posts = archive_by_date[year][month]
            month_name = f"{month:02d}月"
            archive_html += f'<div class="archive-month" markdown>\n\n### {month_name}\n\n'
            
            for post in month_posts:
                date_str = post['date'].strftime('%m月%d日')
                
                # 生成分类标签
                categories_html = ""
                if post['categories']:
                    categories_html = f'<span class="category-tag">{", ".join(post["categories"])}</span>'
                
                url = get_post_url(post)
                archive_html += f'''
<div class="archive-post" markdown>
- **{date_str}** - [{post['title']}]({url}) {categories_html}
</div>
'''
            
            archive_html += '\n</div>\n'
        
        archive_html += '\n</div>\n'
    
    # 生成完整的 archive.md 内容
    archive_content = f'''---
title: 时间归档
description: 按时间归档的博客文章
---

# 📅 时间归档

> 本页由系统自动生成，按时间顺序展示所有文章。

{archive_html}

---

<div class="archive-stats" markdown>

## 📊 统计信息

- **总文章数**: {len(posts)} 篇
- **最早文章**: {min(posts, key=lambda x: x['date'])['date'].strftime('%Y年%m月%d日') if posts else '无'}
- **最新文章**: {max(posts, key=lambda x: x['date'])['date'].strftime('%Y年%m月%d日') if posts else '无'}

</div>
'''
    
    # 写入文件
    with open(blog_dir / 'archive.md', 'w', encoding='utf-8') as f:
        f.write(archive_content)

def generate_categories_page(docs_dir, posts):
    """
    生成分类浏览页面
    
    按分类组织文章，创建分类浏览页面。
    
    Args:
        docs_dir (Path): 文档目录路径
        posts (list): 文章信息列表
    """
    blog_dir = docs_dir / 'blog'
    
    # 按分类分组文章
    categories_posts = defaultdict(list)
    for post in posts:
        for category in post['categories']:
            categories_posts[category].append(post)
    
    # 生成分类内容 HTML
    categories_html = ""
    for category in sorted(categories_posts.keys()):
        category_posts = categories_posts[category]
        categories_html += f'<div class="category-section" markdown>\n\n## {category}\n\n'
        categories_html += f'<div class="category-posts" markdown>\n\n'
        
        for post in category_posts:
            date_str = post['date'].strftime('%Y年%m月%d日')
            
            # 生成标签 HTML
            tags_html = ""
            if post['tags']:
                tags_html = f'<span class="tag-list">🏷️ {", ".join(post["tags"])}</span>'
            
            url = get_post_url(post)
            categories_html += f'''
<div class="category-post-card" markdown>
<div class="post-info">
  <h4 class="post-title">
    <a href="{url}">{post['title']}</a>
  </h4>
  <div class="post-meta">
    <span class="post-date">📅 {date_str}</span>
    {tags_html}
  </div>
  <div class="post-excerpt">
    {post['description'] or '暂无描述'}
  </div>
</div>
</div>
'''
        
        categories_html += '\n</div>\n</div>\n'
    
    # 生成完整的 categories.md 内容
    categories_content = f'''---
title: 文章分类
description: 按分类浏览的文章列表
---

# 🏷️ 文章分类

按分类浏览的所有文章。

{categories_html}

---

<div class="categories-stats" markdown>

## 📊 分类统计

'''
    
    # 添加分类统计信息
    for category in sorted(categories_posts.keys()):
        count = len(categories_posts[category])
        categories_content += f'- **{category}**: {count} 篇\n'
    
    categories_content += '''
</div>
'''
    
    # 写入文件
    with open(blog_dir / 'categories.md', 'w', encoding='utf-8') as f:
        f.write(categories_content)

# ==================== 导航配置更新函数 ====================

def get_post_nav():
    """
    获取博客文章的导航配置
    
    扫描文章目录，为每篇文章生成导航项。
    只返回实际存在的文章。
    
    Returns:
        list: 包含文章导航配置的列表
    """
    post_nav = []
    if os.path.exists(POSTS_DIR):
        for fname in sorted(os.listdir(POSTS_DIR)):
            if fname.endswith('.md'):
                file_path = os.path.join(POSTS_DIR, fname)
                # 只添加实际存在的文件
                if os.path.isfile(file_path):
                    name = os.path.splitext(fname)[0]
                    post_nav.append({name: f'blog/posts/{fname}'})
    return post_nav

def update_mkdocs_nav():
    """
    更新 MkDocs 导航配置
    
    只更新博客文章列表，保持其他导航结构不变。
    使用 ruamel.yaml 保持 YAML 格式和注释。
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    
    # 读取现有的 mkdocs.yml 文件
    with open(MKDOCS_YML, 'r', encoding='utf-8') as f:
        data = yaml.load(f)

    nav = data.get('nav', [])
    
    # 获取最新的文章列表
    post_nav = get_post_nav()
    
    # 遍历导航结构，只更新文章列表部分
    def update_posts_nav(items):
        for item in items:
            if isinstance(item, dict):
                # 找到博客导航项
                if '博客' in item:
                    blog_nav = item['博客']
                    # 遍历博客下的子项
                    for sub_item in blog_nav:
                        if isinstance(sub_item, dict) and '文章列表' in sub_item:
                            # 更新文章列表
                            sub_item['文章列表'] = post_nav
                            return True
                # 递归处理嵌套的导航项
                elif any(isinstance(v, list) for v in item.values()):
                    for v in item.values():
                        if isinstance(v, list) and update_posts_nav(v):
                            return True
        return False

    # 更新导航结构
    if not update_posts_nav(nav):
        # 如果没有找到文章列表，则在博客导航下添加
        for item in nav:
            if isinstance(item, dict) and '博客' in item:
                blog_nav = item['博客']
                if not any(isinstance(sub_item, dict) and '文章列表' in sub_item for sub_item in blog_nav):
                    blog_nav.append({'文章列表': post_nav})
                break
    
    data['nav'] = nav

    # 写回文件
    with open(MKDOCS_YML, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)