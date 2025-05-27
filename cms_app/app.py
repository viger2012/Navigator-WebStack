
# 导入 Flask 框架及相关模块
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, jsonify, render_template_string
import csv
import os
from collections import defaultdict
import json # 导入 json 模块用于处理 deleted_categories
import re # 导入 re 模块用于正则表达式替换

# 创建 Flask 应用实例，并指定静态文件目录
app = Flask(__name__, static_folder='../static')

# 定义 CSV 数据文件的路径
# os.path.dirname(__file__) 获取当前文件（app.py）所在的目录
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.csv')

# 从 CSV 文件读取数据
def read_data_from_csv():
    """
    从 CSV 文件读取数据并将其作为字典返回。
    字典的键是分类名称，值是该分类下的链接列表。
    """
    data = {}
    try:
        # 以 UTF-8 编码读取文件
        with open(DATA_FILE, mode='r', encoding='utf-8') as infile:
            # 使用 DictReader 读取 CSV，将每行作为字典
            reader = csv.DictReader(infile)
            for row in reader:
                # 安全地获取 'category' 字段
                category = row.get('category')
                # 只处理有分类的行
                if category:
                    # 如果分类不存在，则创建一个新的列表
                    if category not in data:
                        data[category] = []
                    # 将链接条目添加到对应分类的列表中
                    data[category].append(row)
    except FileNotFoundError:
        # 如果文件不存在，则返回空字典
        pass
    return data

# 将数据写入 CSV 文件
# 将数据写入 CSV 文件
def write_data_to_csv(data):
    """
    将数据（字典格式）写入 CSV 文件。
    """
    # 将字典数据转换为 DictWriter 需要的行列表
    rows = []
    fieldnames = ['category', 'name', 'description', 'url', 'icon'] # 定义列名

    for category, links in data.items():
        if links: # 如果分类有链接
            for link in links:
                # 确保每个链接字典都有 category 字段
                link['category'] = category
                rows.append(link)
        else: # 如果分类没有链接，添加一个只有分类名称的行
            rows.append({'category': category, 'name': '', 'description': '', 'url': '', 'icon': ''})

    # 以写入模式打开文件，指定 UTF-8 编码和 newline='' 防止空行
    with open(DATA_FILE, mode='w', encoding='utf-8', newline='') as outfile:
        # 创建 DictWriter 对象
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()
        # 写入所有数据行
        writer.writerows(rows)

# 首页路由，渲染中文首页
@app.route('/')
def index():
    """
    渲染中文首页，并从 CSV 文件加载数据。
    """
    # 从 CSV 读取数据
    data = read_data_from_csv()
    # 渲染 cn_index.html 模板，并将数据传递给模板
    return render_template('cn_index.html', data=data) # 默认使用中文模板

# 英文首页路由，渲染英文首页
@app.route('/en/')
def index_en():
    """
    渲染英文首页，并从 CSV 文件加载数据。
    """
    # 从 CSV 读取数据
    data = read_data_from_csv()
    # 渲染 en_index.html 模板，并将数据传递给模板
    return render_template('en_index.html', data=data)

# 生成静态 HTML 文件的路由
@app.route('/generate-html')
def generate_html():
    """
    从模板和数据生成静态 HTML 文件。
    """
    # 从 CSV 读取数据
    data = read_data_from_csv()

    # 生成中文 index.html
    cn_html_content = render_template('cn_index.html', data=data)
    # 将生成的中文 HTML 内容写入到 static 目录下的文件
    with open('../static/cn/index.html', 'w', encoding='utf-8') as f:
        f.write(cn_html_content)

    # 生成英文 index.html
    en_html_content = render_template('en_index.html', data=data)
    # 将生成的英文 HTML 内容写入到 static 目录下的文件
    with open('../static/en/index.html', 'w', encoding='utf-8') as f:
        f.write(en_html_content)

    # 返回生成成功的消息
    return "HTML files generated successfully!"

# 编辑页面路由，渲染编辑数据的表单
@app.route('/edit')
def edit():
    """
    渲染编辑页面，并从 CSV 文件加载数据。
    """
    # 从 CSV 读取数据
    data = read_data_from_csv()
    # 渲染 edit.html 模板，并将数据传递给模板
    return render_template('edit.html', data=data)

# 保存数据路由，处理编辑表单的提交
@app.route('/save', methods=['POST'])
def save():
    """
    处理编辑表单的提交。
    """
    if request.method == 'POST':
        print("Received form data:", request.form) # 添加这行来打印接收到的表单数据
        # 从 CSV 读取当前数据
        data = read_data_from_csv()
        updated_data = {}
        # 获取要删除的分类列表
        deleted_categories = request.form.getlist('deleted_categories')
        # 获取要删除的链接字符串，并按逗号分割成列表
        deleted_links_str = request.form.get('deleted_links', '')
        deleted_links = deleted_links_str.split(',') if deleted_links_str else []

        # 处理现有分类和链接
        for category_name, links in data.items():
            # 如果分类被标记为删除，则跳过
            if category_name in deleted_categories:
                continue

            # 获取更新后的分类名称，如果未更改则使用原名称
            updated_category_name = request.form.get(f'category_name_{category_name}', category_name)
            updated_links = []

            # 处理该分类下的现有链接
            # 遍历原始链接列表，根据原始分类名和原始链接在原始列表中的索引来获取更新后的数据
            for original_index, link in enumerate(links):
                # 生成链接的唯一标识符（使用原始分类名和原始URL）
                link_id = f"{category_name}:{link['url']}" # 注意这里使用冒号分隔，与前端JavaScript一致
                # 如果链接被标记为删除，则跳过
                if link_id in deleted_links:
                    continue

                # 获取更新后的链接信息，如果未更改则使用原信息
                updated_link = {
                    'name': request.form.get(f'name_{category_name}_{original_index}', link['name']),
                    'description': request.form.get(f'description_{category_name}_{original_index}', link['description']),
                    'url': request.form.get(f'url_{category_name}_{original_index}', link['url']),
                    'icon': request.form.get(f'icon_{category_name}_{original_index}', link['icon'])
                }
                updated_links.append(updated_link)

            # 处理添加到现有分类的新链接
            new_link_index = 1 # 前端索引从 1 开始
            while True:
                # 根据前端命名格式构建新链接字段名
                new_link_name_field = f'new_link_name_{category_name}_{new_link_index}'
                new_link_url_field = f'new_link_url_{category_name}_{new_link_index}'

                # 尝试从表单获取新链接的名称和URL
                new_link_name = request.form.get(new_link_name_field)
                new_link_url = request.form.get(new_link_url_field)

                # 如果名称和URL都为空，表示没有更多新链接了
                if new_link_name is None and new_link_url is None:
                    break

                # 确保新链接的必填字段（名称和URL）已填写
                if new_link_name and new_link_url:
                    # 构建新链接字典
                    new_link = {
                        'name': new_link_name,
                        'description': request.form.get(f'new_link_description_{category_name}_{new_link_index}', ''),
                        'url': new_link_url,
                        'icon': request.form.get(f'new_link_icon_{category_name}_{new_link_index}', '')
                    }
                    # 将新链接添加到该分类的链接列表中
                    updated_links.append(new_link)

                # 索引递增，检查下一个可能的新链接
                new_link_index += 1

            # 将更新后的链接列表添加到 updated_data 中，使用更新后的分类名称作为键
            updated_data[updated_category_name] = updated_links

        # 处理新分类及其链接
        # 前端新分类名称字段没有索引，直接获取
        new_category_name = request.form.get('new_category_name')

        # 如果新分类名称存在且不为空
        if new_category_name:
            new_links_in_new_category = []
            # 遍历前端可能发送的新分类下的新链接，前端使用了 new_category_index 和 new_link_index_in_new_category
            # 这里的 new_category_index 需要根据前端实际发送的字段名来确定，假设前端只发送一个新分类，其索引为 0
            # 如果前端可能发送多个新分类，这里的逻辑需要调整以遍历不同的 new_category_index
            # 根据您提供的终端数据，新分类下的新链接字段名格式是 new_link_name_new_category_0_1, new_link_url_new_category_0_1 等
            # 所以我们假设新分类的索引是 0
            new_category_form_index = 0 # 假设前端新分类的索引从 0 开始
            new_link_index_in_new_category = 1 # 新分类下的新链接索引从 1 开始
            while True:
                # 根据前端命名格式构建新分类下新链接的字段名
                new_link_name_field = f'new_link_name_new_category_{new_category_form_index}_{new_link_index_in_new_category}'
                new_link_url_field = f'new_link_url_new_category_{new_category_form_index}_{new_link_index_in_new_category}'

                # 尝试从表单获取新分类下新链接的名称和URL
                new_link_name = request.form.get(new_link_name_field)
                new_link_url = request.form.get(new_link_url_field)

                # 如果名称和URL都为空，表示该新分类下没有更多新链接了
                if new_link_name is None and new_link_url is None:
                    break

                # 确保新链接的必填字段（名称和URL）已填写
                if new_link_name and new_link_url:
                     # 构建新链接字典
                     new_link = {
                        'name': new_link_name,
                        'description': request.form.get(f'new_link_description_new_category_{new_category_form_index}_{new_link_index_in_new_category}', ''),
                        'url': new_link_url,
                        'icon': request.form.get(f'new_link_icon_new_category_{new_category_form_index}_{new_link_index_in_new_category}', '')
                    }
                     # 将新链接添加到该新分类的链接列表中
                     new_links_in_new_category.append(new_link)

                # 索引递增，检查该新分类下的下一个可能的新链接
                new_link_index_in_new_category += 1

            # 将新分类及其链接添加到 updated_data 中
            updated_data[new_category_name] = new_links_in_new_category

        # 将更新后的数据写入 CSV 文件
        write_data_to_csv(updated_data)

        # 重定向回编辑页面
        return redirect(url_for('edit'))


# 添加导出静态页面的路由
@app.route('/export_static', methods=['POST'])
def export_static():
    """
    导出静态页面到 page 文件夹。
    """
    try:
        # 从 CSV 读取数据
        data = read_data_from_csv()

        # 直接使用 render_template 渲染 templates/cn_index.html 模板
        # 注意：这里直接渲染 templates 目录下的模板
        rendered_html = render_template('cn_index.html', data=data)

        # 调整静态资源路径
        # 将 ../assets/ 替换为 ../static/assets/
        # 使用正则表达式进行替换，确保只替换相对路径
        # 查找 src="..." 或 href="..." 中以 ../assets/ 开头的路径
        def replace_path(match):
            # match.group(1) 是属性名 (src or href)
            # match.group(2) 是引号 (' or ")
            # match.group(3) 是原始路径 (../assets/...)
            original_path = match.group(3)
            # 检查是否是网络链接，如果是则不替换
            if original_path.startswith('http://') or original_path.startswith('https://') or original_path.startswith('//'):
                return match.group(0) # 返回原始匹配的字符串
            # 替换 ../assets/ 为 ../static/assets/
            # 确保只替换 ../assets/ 开头的路径
            if original_path.startswith('/static'):
                 print(original_path)
                 # 修改替换逻辑，将 /static 替换为 ../static/assets/
                 new_path = original_path.replace('/static/', './')
                 return f'{match.group(1)}={match.group(2)}{new_path}{match.group(2)}'
            return match.group(0) # 如果不是 ../assets/ 开头，返回原始匹配的字符串


        # 匹配 src="..." 或 href="..." 中的路径
        # 考虑单引号和双引号
        pattern = r'(src|href)=([\'"])(?P<path>.*?)\2'
        adjusted_html = re.sub(pattern, replace_path, rendered_html)


        # 创建 page 目录如果不存在
        page_dir = os.path.join(os.path.dirname(__file__), '..', 'page')
        os.makedirs(page_dir, exist_ok=True)

        # 保存到 page/index.html
        output_path = os.path.join(page_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(adjusted_html)

        return jsonify({'success': True, 'message': 'Static page exported successfully!'})

    except Exception as e:
        # 捕获所有异常并返回错误信息
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
