import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 生成slug
slugify = lambda s: re.sub(r'[^\w\u4e00-\u9fa5-]+', '-', s).strip('-').lower()

def get_post_url(post):
    filename = post['filename']
    name = os.path.splitext(filename)[0]
    return f"posts/{name}/"

def on_files(files, config):
    """在文件处理时自动生成博客页面"""
    print("=== 开始执行on_files钩子 ===")
    generate_blog_pages(config)
    print("=== on_files钩子执行完成 ===")
    return files

def generate_blog_pages(config):
    """生成博客相关页面"""
    docs_dir = Path(config['docs_dir'])
    posts_dir = docs_dir / 'blog' / 'posts'
    
    if not posts_dir.exists():
        return
    
    # 收集所有博客文章
    posts = []
    for post_file in posts_dir.glob('*.md'):
        if post_file.name.startswith('_'):
            continue
            
        post_info = extract_post_info(post_file)
        if post_info:
            posts.append(post_info)
    
    # 按日期排序
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    # 生成最新文章页面
    generate_latest_posts_page(docs_dir, posts, config)
    
    # 生成时间归档页面
    generate_archive_page(docs_dir, posts)
    
    # 生成分类页面
    generate_categories_page(docs_dir, posts)
    
    print("博客构建成功！文章列表和归档已自动生成。")

def extract_post_info(post_file):
    """提取文章信息"""
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取front matter
        front_matter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not front_matter_match:
            return None
        
        front_matter = yaml.safe_load(front_matter_match.group(1))
        
        # 提取标题
        title = front_matter.get('title', post_file.stem)
        
        # 提取日期
        date_str = front_matter.get('date', '2025-01-01')
        if isinstance(date_str, str):
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                date = datetime(2025, 1, 1)
        else:
            date = date_str
        
        # 提取分类和标签
        categories = front_matter.get('categories', [])
        if isinstance(categories, str):
            categories = [categories]
        
        tags = front_matter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        # 提取描述
        description = front_matter.get('description', '')
        
        # 提取作者
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
    """生成最新文章页面"""
    blog_dir = docs_dir / 'blog'
    blog_dir.mkdir(exist_ok=True)
    
    # 生成最新文章卡片
    latest_posts_html = ""
    for post in posts[:10]:  # 显示最新10篇文章
        date_str = post['date'].strftime('%Y年%m月%d日')
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
    
    site_url = config.get('site_url', '/')
    if site_url and not site_url.endswith('/'):
        site_url += '/'
    rss_url = f"{site_url}feed_rss_created.xml"
    
    # 生成完整的index.md内容
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
    
    with open(blog_dir / 'index.md', 'w', encoding='utf-8') as f:
        f.write(index_content)

def generate_archive_page(docs_dir, posts):
    """生成时间归档页面"""
    blog_dir = docs_dir / 'blog'
    
    # 按年份和月份分组
    archive_by_date = defaultdict(lambda: defaultdict(list))
    for post in posts:
        year = post['date'].year
        month = post['date'].month
        archive_by_date[year][month].append(post)
    
    # 生成归档内容
    archive_html = ""
    for year in sorted(archive_by_date.keys(), reverse=True):
        archive_html += f'<div class="archive-year" markdown>\n\n## {year}年\n\n'
        
        for month in sorted(archive_by_date[year].keys(), reverse=True):
            month_posts = archive_by_date[year][month]
            month_name = f"{month:02d}月"
            archive_html += f'<div class="archive-month" markdown>\n\n### {month_name}\n\n'
            
            for post in month_posts:
                date_str = post['date'].strftime('%m月%d日')
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
    
    # 生成完整的archive.md内容
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
    
    with open(blog_dir / 'archive.md', 'w', encoding='utf-8') as f:
        f.write(archive_content)

def generate_categories_page(docs_dir, posts):
    """生成分类页面"""
    blog_dir = docs_dir / 'blog'
    
    # 按分类分组
    categories_posts = defaultdict(list)
    for post in posts:
        for category in post['categories']:
            categories_posts[category].append(post)
    
    # 生成分类内容
    categories_html = ""
    for category in sorted(categories_posts.keys()):
        category_posts = categories_posts[category]
        categories_html += f'<div class="category-section" markdown>\n\n## {category}\n\n'
        categories_html += f'<div class="category-posts" markdown>\n\n'
        
        for post in category_posts:
            date_str = post['date'].strftime('%Y年%m月%d日')
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
    
    # 生成完整的categories.md内容
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
    
    for category in sorted(categories_posts.keys()):
        count = len(categories_posts[category])
        categories_content += f'- **{category}**: {count} 篇\n'
    
    categories_content += '''
</div>
'''
    
    with open(blog_dir / 'categories.md', 'w', encoding='utf-8') as f:
        f.write(categories_content)

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
    """在构建完成后生成博客页面"""
    print("=== 开始执行on_post_build钩子 ===")
    generate_blog_pages(config)
    print("=== on_post_build钩子执行完成 ===")