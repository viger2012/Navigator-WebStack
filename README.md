# WebStack 项目说明文档

## 项目概述

本项目是一个基于 Flask 的网址导航网站，灵感来源于 [WebStack.cc](https://webstack.cc)。它提供了一个简单的内容管理系统（CMS），允许用户通过网页界面编辑和管理导航链接。项目支持中文和英文两种语言的首页展示，并可以将动态生成的页面导出为静态 HTML 文件。

## 文件结构

以下是项目的文件和文件夹列表：

```
.
├── cms_app/
│   ├── app.py
│   ├── data.csv
│   └── templates/
│       ├── cn_index.html
│       ├── edit.html
│       └── en_index.html
├── page/
├── plan.md
└── static/
    ├── 404.html
    ├── CNAME
    ├── index.html
    ├── LICENSE
    ├── README.md
    ├── tssss.html
    ├── assets/
    ├── cn/
    │   ├── about.html
    │   └── index.html
    └── en/
        ├── about.html
        └── index.html
```

## 项目组件说明

*   **`cms_app/`**: 包含 Flask 应用的核心文件。
    *   `app.py`: Flask 主应用文件，定义了路由、数据读取/写入逻辑以及页面渲染。它从 `data.csv` 读取导航数据，并使用 `templates` 目录下的 HTML 文件进行渲染。
    *   `data.csv`: 存储导航链接数据的 CSV 文件。包含 `category`, `name`, `description`, `url`, `icon` 等字段。
    *   `templates/`: 存放 Flask 应用的 HTML 模板文件。
        *   `cn_index.html`: 中文首页模板。
        *   `en_index.html`: 英文首页模板。
        *   `edit.html`: 用于编辑导航数据的管理界面模板。
*   **`page/`**: 用于存放导出后的静态 HTML 文件。
*   **`plan.md`**: 项目的计划文档（当前文件）。
*   **`static/`**: 存放静态资源文件，如 CSS、JavaScript、图片等。
    *   `404.html`: 404 错误页面。
    *   `CNAME`: CNAME 文件，用于自定义域名。
    *   `index.html`: 静态首页文件（可能是原始项目的）。
    *   `LICENSE`: 项目许可证文件。
    *   `README.md`: 原始 WebStack 项目的说明文档。
    *   `tssss.html`: 未知用途的 HTML 文件。
    *   `assets/`: 静态资源目录，包含 CSS, JS, 图片等。
    *   `cn/`: 中文静态页面目录，包含 `about.html` 和 `index.html`。
    *   `en/`: 英文静态页面目录，包含 `about.html` 和 `index.html`。

## 如何运行

1.  确保您已安装 Python 和 Flask。
2.  在项目根目录下，运行 `python cms_app/app.py` 命令启动 Flask 应用。
3.  应用通常会在 `http://127.0.0.1:5000/` 运行。

## 如何编辑数据

本项目提供两种编辑导航数据的方式：

1.  **通过 CMS 界面**:
    *   运行 Flask 应用后，访问 `/edit` 路由（例如 `http://127.0.0.1:5000/edit`）。
    *   在编辑页面，您可以修改现有分类和链接的信息，添加新的链接到现有分类，添加新的分类及其链接，以及删除分类和链接。
    *   完成修改后，点击页面底部的“Save Changes (保存更改)”按钮。数据将保存到 `cms_app/data.csv` 文件中。
2.  **直接修改 `data.csv` 文件**:
    *   您也可以直接使用文本编辑器或电子表格软件打开 `cms_app/data.csv` 文件进行编辑。
    *   请确保遵循 CSV 格式，并包含 `category`, `name`, `description`, `url`, `icon` 这几列。
    *   直接修改 CSV 文件后，重新运行 Flask 应用即可加载最新的数据。

## 如何导出静态页面

如果您需要生成静态 HTML 文件用于部署（例如在静态托管服务上），可以按照以下步骤操作：

1.  运行 Flask 应用并访问 `http://127.0.0.1:5000/edit` 页面。
2.  点击页面顶部的“Export Static Page (导出静态页面)”按钮。
3.  应用将根据 `data.csv` 中的数据和模板文件生成静态 HTML 文件，并保存到项目根目录下的 `page/` 文件夹中。目前主要导出中文首页 (`cn_index.html`) 到 `page/index.html`。导出的index.html文件替换掉`static/` 文件夹中的`index.html`，将`static` 文件夹部署到服务器即可。

## 许可证

本项目基于原始 WebStack 项目，并遵循 **MIT License**。

Copyright © 2017-2023 **[webstack.cc](https://webstack.cc)** Released under the **MIT License**.
