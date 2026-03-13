#!/usr/bin/env python3
"""
微信公众号 Markdown 转 HTML 工具
支持多种主题样式，严格按照微信规范生成 HTML
主题从 YAML 文件动态加载
"""

import re
import html as html_module
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ThemeLoader:
    """从 YAML 文件加载主题"""
    
    _cache: Dict[str, dict] = {}
    _themes_dir: Optional[Path] = None
    
    @classmethod
    def _get_themes_dir(cls) -> Path:
        """获取主题目录路径"""
        if cls._themes_dir is None:
            cls._themes_dir = Path(__file__).parent.parent / 'themes'
        return cls._themes_dir
    
    @classmethod
    def load_theme(cls, theme_name: str) -> dict:
        """
        加载指定主题
        
        Args:
            theme_name: 主题名称，格式为 "category/name" 或 "name"
                       例如: "wenyan/default" 或 "macaron/pink"
                       如果不指定分类，默认使用 wenyan
        
        Returns:
            主题配置字典
        
        Raises:
            FileNotFoundError: 主题文件不存在
            yaml.YAMLError: YAML 解析错误
        """
        # 检查缓存
        if theme_name in cls._cache:
            return cls._cache[theme_name]
        
        # 解析主题路径
        parts = theme_name.split('/')
        if len(parts) == 2:
            category, name = parts
        else:
            category = 'wenyan'  # 默认使用文颜主题
            name = theme_name
        
        # 构建文件路径
        theme_file = cls._get_themes_dir() / category / f'{name}.yaml'
        
        if not theme_file.exists():
            raise FileNotFoundError(f"主题文件不存在: {theme_file}")
        
        # 加载 YAML
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme_data = yaml.safe_load(f)
        
        # 转换 YAML 格式到内部格式
        converted = cls._convert_theme_format(theme_data)
        
        # 缓存结果
        cls._cache[theme_name] = converted
        
        return converted
    
    @classmethod
    def _convert_theme_format(cls, yaml_data: dict) -> dict:
        """
        将 YAML 格式转换为主题配置格式
        
        YAML 格式:
          styles:
            body: {font_size, line_height, ...}
            h1: {...}
        
        内部格式:
          body: {font_size, line_height, ...}
          h1: {...}
        """
        result = {
            'name': yaml_data.get('name', '未命名主题'),
            'description': yaml_data.get('description', ''),
            'keywords': yaml_data.get('keywords', []),
        }
        
        # 直接使用 styles 下的配置
        styles = yaml_data.get('styles', {})
        result.update(styles)
        
        # 添加颜色信息（用于推荐等场景）
        if 'colors' in yaml_data:
            result['colors'] = yaml_data['colors']
        
        return result
    
    @classmethod
    def list_themes(cls) -> Dict[str, Dict[str, List[str]]]:
        """
        列出所有可用主题
        
        Returns:
            {category: [theme_name1, theme_name2, ...]}
        """
        themes_dir = cls._get_themes_dir()
        themes: Dict[str, List[str]] = {}
        
        for category in ['wenyan', 'macaron']:
            category_dir = themes_dir / category
            if category_dir.exists() and category_dir.is_dir():
                themes[category] = []
                for yaml_file in category_dir.glob('*.yaml'):
                    if yaml_file.name != '_template.yaml':
                        themes[category].append(yaml_file.stem)
                themes[category].sort()
        
        return themes
    
    @classmethod
    def get_all_themes(cls) -> Dict[str, dict]:
        """
        获取所有主题配置
        
        Returns:
            {theme_id: theme_config}
        """
        all_themes = {}
        theme_list = cls.list_themes()
        
        for category, names in theme_list.items():
            for name in names:
                theme_id = f"{category}/{name}"
                try:
                    theme_config = cls.load_theme(theme_id)
                    all_themes[theme_id] = theme_config
                except Exception as e:
                    print(f"警告: 加载主题 {theme_id} 失败: {e}")
        
        return all_themes
    
    @classmethod
    def get_theme_info(cls, theme_name: str) -> dict:
        """
        获取主题基本信息（不加载完整配置）
        
        Returns:
            {name, description, keywords}
        """
        try:
            theme = cls.load_theme(theme_name)
            return {
                'name': theme.get('name', theme_name),
                'description': theme.get('description', ''),
                'keywords': theme.get('keywords', [])
            }
        except Exception:
            return {
                'name': theme_name,
                'description': '主题加载失败',
                'keywords': []
            }
    
    @classmethod
    def clear_cache(cls):
        """清除主题缓存"""
        cls._cache.clear()


class ThemeKeywords:
    """主题关键词映射 - 用于自动推荐"""
    
    # 关键词映射：主题ID -> 关键词列表
    KEYWORDS = {
        # 文颜主题
        "wenyan/default": [
            "默认", "经典", "简洁", "专业", "长文", "博客", "技术", "公众号"
        ],
        "wenyan/mint": [
            "清新", "薄荷", "自然", "绿色", "健康", "环保"
        ],
        "wenyan/purple": [
            "紫色", "优雅", "神秘", "高端"
        ],
        "wenyan/maize": [
            "玉米", "温暖", "黄色", "阳光"
        ],
        "wenyan/pie": [
            "派", "甜美", "可爱"
        ],
        "wenyan/lapis": [
            "青金石", "蓝色", "沉稳", "专业"
        ],
        "wenyan/rainbow": [
            "彩虹", "多彩", "活泼", "童趣"
        ],
        "wenyan/orange_heart": [
            "橙心", "橙色", "温暖", "热情"
        ],
        # 马卡龙主题
        "macaron/pink": [
            "女性", "少女", "甜美", "温柔", "粉色", "浪漫", "恋爱", "情感",
            "闺蜜", "美妆", "护肤", "穿搭", "约会", "心情", "日记"
        ],
        "macaron/blue": [
            "清新", "宁静", "放松", "旅行", "自然", "海洋", "天空", "平静",
            "治愈", "海边", "度假", "慢生活"
        ],
        "macaron/mint": [
            "健康", "环保", "清新", "自然", "植物", "绿茶", "瑜伽", "养生",
            "有机", "绿色", "生态"
        ],
        "macaron/lavender": [
            "浪漫", "优雅", "文艺", "梦幻", "紫色", "薰衣草", "法式", "田园",
            "诗意"
        ],
        "macaron/peach": [
            "美食", "甜品", "下午茶", "温暖", "甜美", "柔和", "温馨", "家庭",
            "烘焙", "甜点", "治愈系"
        ],
        "macaron/lemon": [
            "活力", "正能量", "励志", "阳光", "明亮", "清新", "能量", "积极",
            "奋斗", "希望", "快乐", "青春"
        ],
        "macaron/coral": [
            "热情", "活力", "夏日", "海滩", "热带", "激情", "运动", "活泼"
        ],
        "macaron/sage": [
            "自然", "环保", "户外", "植物", "森林", "田园", "质朴", "简约",
            "鼠尾草", "森系"
        ],
        "macaron/lilac": [
            "优雅", "浪漫", "文艺", "精致", "女性", "轻奢", "品味", "丁香"
        ],
        "macaron/cream": [
            "温馨", "治愈", "柔和", "家庭", "生活", "简单", "舒适", "日常",
            "奶油", "暖调"
        ],
        "macaron/sky": [
            "旅行", "自由", "梦想", "天空", "飞行", "希望", "开阔", "蓝天",
            "云朵"
        ],
        "macaron/rose": [
            "浪漫", "爱情", "精致", "女性", "优雅", "玫瑰", "约会", "纪念日",
            "情侣", "表白"
        ],
        # 兼容旧格式的关键词映射
        "macaron/rose_alt": [
            "浪漫", "精致", "马卡龙玫瑰"
        ],
    }
    
    @classmethod
    def get_keywords(cls, theme_id: str) -> List[str]:
        """获取指定主题的关键词"""
        return cls.KEYWORDS.get(theme_id, [])
    
    @classmethod
    def get_all_keywords(cls) -> Dict[str, List[str]]:
        """获取所有主题关键词映射"""
        return cls.KEYWORDS.copy()


class WeChatHTMLConverter:
    """微信公众号 HTML 转换器 - 支持多主题"""
    
    # 微信安全标签白名单
    SAFE_TAGS = {
        'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'b', 'em', 'i', 'span', 'a', 'img',
        'ul', 'ol', 'li', 'section', 'blockquote',
        'pre', 'code'
    }
    
    # 支持的 CSS 属性
    SAFE_CSS = {
        'color', 'font-size', 'font-weight', 'font-family',
        'text-align', 'line-height', 'background-color',
        'padding', 'margin', 'border', 'border-radius',
        'border-left', 'border-right', 'border-top', 'border-bottom',
        'display', 'max-width', 'height', 'overflow-x', 'white-space', 
        'word-wrap', 'text-decoration', 'letter-spacing', 'text-shadow',
        'text-transform', 'font-style', 'padding-left', 'padding-right',
        'padding-top', 'padding-bottom', 'position', 'box-shadow'
    }
    
    # 默认主题
    DEFAULT_THEME = "wenyan/default"
    
    def __init__(self, theme: str = None):
        """
        初始化转换器
        
        Args:
            theme: 主题名称，格式为 "category/name" 或 "name"
        """
        self.toc = []  # 目录
        self.heading_counter = 0
        self.theme_name = theme or self.DEFAULT_THEME
        self.theme = self._load_theme(self.theme_name)
    
    def _load_theme(self, theme_name: str) -> dict:
        """
        加载主题配置
        
        Args:
            theme_name: 主题名称
        
        Returns:
            主题配置字典
        """
        try:
            return ThemeLoader.load_theme(theme_name)
        except FileNotFoundError:
            print(f"警告: 主题 '{theme_name}' 不存在，使用默认主题 '{self.DEFAULT_THEME}'")
            return ThemeLoader.load_theme(self.DEFAULT_THEME)
        except yaml.YAMLError as e:
            print(f"警告: 主题 '{theme_name}' 解析失败: {e}，使用默认主题")
            return ThemeLoader.load_theme(self.DEFAULT_THEME)
        except Exception as e:
            print(f"警告: 加载主题 '{theme_name}' 失败: {e}，使用默认主题")
            return ThemeLoader.load_theme(self.DEFAULT_THEME)
    
    def set_theme(self, theme_name: str):
        """
        切换主题
        
        Args:
            theme_name: 主题名称
        """
        self.theme_name = theme_name
        self.theme = self._load_theme(theme_name)
    
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self.theme_name
    
    def _style_to_str(self, style_dict: dict) -> str:
        """
        将样式字典转换为 CSS 字符串
        
        Args:
            style_dict: 样式字典，如 {'font_size': '16px', 'color': '#333'}
        
        Returns:
            CSS 字符串，如 "font-size: 16px; color: #333"
        """
        if not style_dict:
            return ""
        return "; ".join([f"{k.replace('_', '-')}: {v}" for k, v in style_dict.items() if v])
    
    def escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        return html_module.escape(text, quote=False)
    
    def convert(self, markdown_text: str) -> str:
        """
        将 Markdown 转换为微信安全的 HTML
        
        Args:
            markdown_text: Markdown 文本
        
        Returns:
            转换后的 HTML 字符串
        """
        html_content = markdown_text
        
        # 1. 处理代码块（优先处理，避免内部内容被转换）
        html_content = self._process_code_blocks(html_content)
        
        # 2. 处理标题
        html_content = self._process_headings(html_content)
        
        # 3. 处理粗体和斜体
        html_content = self._process_emphasis(html_content)
        
        # 4. 处理行内代码
        html_content = self._process_inline_code(html_content)
        
        # 5. 处理链接
        html_content = self._process_links(html_content)
        
        # 6. 处理图片
        html_content = self._process_images(html_content)
        
        # 7. 处理列表
        html_content = self._process_lists(html_content)
        
        # 8. 处理表格（在引用块之前处理）
        html_content = self._process_tables(html_content)
        
        # 9. 处理引用块
        html_content = self._process_blockquotes(html_content)
        
        # 10. 处理分隔线
        html_content = self._process_hr(html_content)
        
        # 11. 处理段落
        html_content = self._process_paragraphs(html_content)
        
        # 12. 清理空标签和多余换行
        html_content = self._cleanup(html_content)
        
        return html_content
    
    def _process_code_blocks(self, text: str) -> str:
        """处理代码块 - 使用主题样式"""
        pattern = r'```(\w+)?\n(.*?)```'
        style = self._style_to_str(self.theme.get("code_block", {}))
        
        def replace_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            code_escaped = self.escape_html(code)
            
            return f'''<pre style="{style}; overflow-x: auto; font-family: 'Courier New', monospace;">
<code style="display: block;">{code_escaped}</code>
</pre>'''
        
        return re.sub(pattern, replace_code_block, text, flags=re.DOTALL)
    
    def _process_headings(self, text: str) -> str:
        """处理标题 - 使用主题样式"""
        h1_style = self._style_to_str(self.theme.get("h1", {}))
        h2_style = self._style_to_str(self.theme.get("h2", {}))
        h3_style = self._style_to_str(self.theme.get("h3", {}))
        
        # H1
        text = re.sub(
            r'^# (.+)$',
            lambda m: f'<h1 style="{h1_style}">{self.escape_html(m.group(1))}</h1>',
            text,
            flags=re.MULTILINE
        )
        
        # H2
        text = re.sub(
            r'^## (.+)$',
            lambda m: f'<h2 style="{h2_style}">{self.escape_html(m.group(1))}</h2>',
            text,
            flags=re.MULTILINE
        )
        
        # H3
        text = re.sub(
            r'^### (.+)$',
            lambda m: f'<h3 style="{h3_style}">{self.escape_html(m.group(1))}</h3>',
            text,
            flags=re.MULTILINE
        )
        
        # H4-H6 使用 H3 样式
        text = re.sub(
            r'^#### (.+)$',
            lambda m: f'<h4 style="{h3_style}">{self.escape_html(m.group(1))}</h4>',
            text,
            flags=re.MULTILINE
        )
        
        return text
    
    def _process_emphasis(self, text: str) -> str:
        """处理粗体和斜体 - 使用主题样式"""
        strong_style = self._style_to_str(self.theme.get("strong", {}))
        
        # 粗体 **text**
        text = re.sub(
            r'\*\*(.+?)\*\*',
            lambda m: f'<strong style="{strong_style}">{self.escape_html(m.group(1))}</strong>',
            text
        )
        
        # 斜体 *text* - 使用主题文字颜色
        text_color = self.theme.get("body", {}).get("color", "#4a4a4a")
        text = re.sub(
            r'\*(.+?)\*',
            lambda m: f'<em style="font-style: italic; color: {text_color};">{self.escape_html(m.group(1))}</em>',
            text
        )
        
        return text
    
    def _process_inline_code(self, text: str) -> str:
        """处理行内代码 - 使用主题样式"""
        style = self._style_to_str(self.theme.get("code_inline", {}))
        return re.sub(
            r'`(.+?)`',
            lambda m: f'<code style="{style}">{self.escape_html(m.group(1))}</code>',
            text
        )
    
    def _process_links(self, text: str) -> str:
        """处理链接 - 使用主题样式"""
        style = self._style_to_str(self.theme.get("link", {}))
        return re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            lambda m: f'<a href="{m.group(2)}" style="{style}">{self.escape_html(m.group(1))}</a>',
            text
        )
    
    def _process_images(self, text: str) -> str:
        """处理图片 - 优化移动端显示"""
        # 根据主题获取图片样式
        img_style = self.theme.get("image", {})
        img_border_radius = img_style.get("border_radius", "8px")
        img_shadow = img_style.get("box_shadow", "none")
        
        shadow_style = f"box-shadow: {img_shadow};" if img_shadow and img_shadow != "none" else ""
        
        return re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            lambda m: f'<p style="text-align: center; margin: 20px 0; padding: 0 16px;"><img src="{m.group(2)}" alt="{self.escape_html(m.group(1))}" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: {img_border_radius}; {shadow_style}"></p>',
            text
        )
    
    def _process_lists(self, text: str) -> str:
        """处理列表 - 使用主题样式"""
        lines = text.split('\n')
        result = []
        in_ul = False
        in_ol = False
        
        list_style = self.theme.get("list", {})
        list_style_str = self._style_to_str(list_style)
        bullet_color = list_style.get("bullet_color", "#4a90d9")
        font_size = list_style.get("font_size", "15px")
        line_height = list_style.get("line_height", "1.75")
        text_color = self.theme.get("body", {}).get("color", "#333")
        
        for line in lines:
            ul_match = re.match(r'^[\s]*[-\*] (.+)$', line)
            ol_match = re.match(r'^[\s]*(\d+)\. (.+)$', line)
            
            if ul_match:
                if not in_ul:
                    if in_ol:
                        result.append('</ol>')
                        in_ol = False
                    result.append(f'<ul style="{list_style_str}; list-style: none;">')
                    in_ul = True
                content = ul_match.group(1)
                result.append(f'<li style="margin: 6px 0; line-height: {line_height}; color: {text_color}; padding-left: 20px; position: relative;"><span style="position: absolute; left: 0; color: {bullet_color}; font-size: {font_size};">·</span>{content}</li>')
            
            elif ol_match:
                if not in_ol:
                    if in_ul:
                        result.append('</ul>')
                        in_ul = False
                    result.append(f'<ol style="{list_style_str}; list-style: none; counter-reset: item;">')
                    in_ol = True
                content = ol_match.group(2)
                num = ol_match.group(1)
                result.append(f'<li style="margin: 6px 0; line-height: {line_height}; color: {text_color}; padding-left: 30px; position: relative;"><span style="position: absolute; left: 0; color: {bullet_color}; font-weight: bold; font-size: {font_size};">{num}.</span>{content}</li>')
            
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)
        
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')
        
        return '\n'.join(result)
    
    def _process_blockquotes(self, text: str) -> str:
        """处理引用块 - 使用主题样式"""
        lines = text.split('\n')
        result = []
        in_quote = False
        quote_content = []
        
        style = self._style_to_str(self.theme.get("blockquote", {}))
        
        for line in lines:
            quote_match = re.match(r'^[\s]*> (.+)$', line)
            
            if quote_match:
                if not in_quote:
                    in_quote = True
                    quote_content = []
                quote_content.append(quote_match.group(1))
            else:
                if in_quote:
                    content = '<br>'.join(quote_content)
                    result.append(f'<blockquote style="{style}">{content}</blockquote>')
                    in_quote = False
                    quote_content = []
                result.append(line)
        
        if in_quote:
            content = '<br>'.join(quote_content)
            result.append(f'<blockquote style="{style}">{content}</blockquote>')
        
        return '\n'.join(result)
    
    def _process_hr(self, text: str) -> str:
        """处理分隔线 - 使用主题样式"""
        style = self._style_to_str(self.theme.get("separator", {}))
        return re.sub(
            r'^[\s]*[-\*_]{3,}[\s]*$',
            f'<section style="{style}"></section>',
            text,
            flags=re.MULTILINE
        )
    
    def _process_tables(self, text: str) -> str:
        """处理 Markdown 表格 - 微信不支持table，转换为更美观的列表形式"""
        lines = text.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 检测表格开始（包含 | 的行，且不是引用块）
            if '|' in line and not line.startswith('>'):
                # 收集表格所有行
                table_lines = []
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i].strip())
                    i += 1
                
                # 解析表格
                if len(table_lines) >= 2:  # 至少需要表头和分隔行
                    # 过滤掉分隔行（包含 --- 的行）
                    content_rows = [row for row in table_lines if not re.match(r'^\|?[\s\-:|]+\|?$', row)]
                    
                    if content_rows and len(content_rows) >= 2:
                        # 获取表头
                        # header_cells = [cell.strip() for cell in content_rows[0].split('|') if cell.strip()]
                        
                        # 将表格转换为更美观的列表形式展示
                        html_list = []
                        
                        # 添加一个小标题说明
                        html_list.append('<p style="font-size: 15px; margin: 16px 0; line-height: 1.75; color: #333; text-align: justify; letter-spacing: 1px; padding: 0 16px;"><strong style="font-weight: bold; color: #1a1a1a;">排版参数：</strong></p>')
                        
                        html_list.append('<ul style="font-size: 15px; margin: 16px 0; padding-left: 0; list-style: none; line-height: 1.75; letter-spacing: 1px; padding: 0 16px;">')
                        
                        # 数据行（跳过表头，从第二行开始）
                        for row in content_rows[1:]:
                            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                            if cells:
                                # 将每行数据格式化为 参数 → 数值 的形式
                                if len(cells) >= 2:
                                    param = cells[0]
                                    value = cells[1]
                                    formatted = f"<strong style='color: #4a90d9;'>{self.escape_html(param)}</strong>：{self.escape_html(value)}"
                                else:
                                    formatted = self.escape_html(" | ".join(cells))
                                html_list.append(f'<li style="margin: 6px 0; line-height: 1.75; color: #333; padding-left: 20px; position: relative; letter-spacing: 1px;"><span style="position: absolute; left: 0; color: #4a90d9; font-size: 15px;">·</span>{formatted}</li>')
                        
                        html_list.append('</ul>')
                        result.append('\n'.join(html_list))
                    elif content_rows and len(content_rows) == 1:
                        # 只有一行，作为普通文本
                        result.append(content_rows[0])
                continue
            
            result.append(lines[i])
            i += 1
        
        return '\n'.join(result)
    
    def _process_paragraphs(self, text: str) -> str:
        """处理段落 - 使用主题样式"""
        lines = text.split('\n')
        result = []
        paragraph = []
        
        style = self._style_to_str(self.theme.get("body", {}))
        
        for line in lines:
            stripped = line.strip()
            
            # 如果已经是 HTML 标签，直接添加
            if stripped.startswith('<') and stripped.endswith('>'):
                if paragraph:
                    content = ' '.join(paragraph)
                    if content:
                        result.append(f'<p style="{style}">{content}</p>')
                    paragraph = []
                result.append(line)
            elif stripped:
                paragraph.append(stripped)
            else:
                # 空行，结束段落
                if paragraph:
                    content = ' '.join(paragraph)
                    result.append(f'<p style="{style}">{content}</p>')
                    paragraph = []
        
        # 处理最后一个段落
        if paragraph:
            content = ' '.join(paragraph)
            result.append(f'<p style="{style}">{content}</p>')
        
        return '\n'.join(result)
    
    def _cleanup(self, text: str) -> str:
        """清理空标签和多余内容"""
        # 移除空的 p 标签
        text = re.sub(r'<p[^>]*>[\s]*</p>', '', text)
        
        # 合并多个换行为一个
        text = re.sub(r'\n{2,}', '\n', text)
        
        # 移除行首行尾空白
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        return text.strip()
    
    @classmethod
    def get_all_themes(cls) -> Dict[str, Dict[str, List[str]]]:
        """
        获取所有可用主题列表
        
        Returns:
            {category: [theme_name1, theme_name2, ...]}
        """
        return ThemeLoader.list_themes()
    
    @classmethod
    def recommend_theme(cls, content: str, title: str = "") -> Tuple[str, float, str]:
        """
        根据内容自动推荐主题
        
        Args:
            content: 文章内容
            title: 文章标题
        
        Returns:
            (theme_id, confidence, reason)
        """
        text = (title + " " + content).lower()
        scores: Dict[str, Dict] = {}
        
        # 获取所有主题
        all_themes = ThemeLoader.list_themes()
        theme_ids = []
        for category, names in all_themes.items():
            for name in names:
                theme_ids.append(f"{category}/{name}")
        
        # 计算每个主题的匹配分数
        for theme_id in theme_ids:
            keywords = ThemeKeywords.get_keywords(theme_id)
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                count = text.count(keyword.lower())
                if count > 0:
                    score += count
                    matched_keywords.append(keyword)
            
            scores[theme_id] = {
                "score": score,
                "keywords": matched_keywords
            }
        
        # 排序找最高分
        sorted_themes = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        if sorted_themes[0][1]["score"] == 0:
            # 没有匹配到关键词，默认用文颜默认主题
            return cls.DEFAULT_THEME, 0.3, "未检测到明确主题特征，默认使用文颜默认风格"
        
        best_theme = sorted_themes[0]
        theme_id = best_theme[0]
        score = best_theme[1]["score"]
        keywords = best_theme[1]["keywords"][:3]  # 最多显示3个匹配词
        
        # 计算置信度
        total_score = sum(s["score"] for s in scores.values())
        confidence = score / total_score if total_score > 0 else 0
        
        try:
            theme_info = ThemeLoader.get_theme_info(theme_id)
            theme_name = theme_info.get("name", theme_id)
        except Exception:
            theme_name = theme_id
        
        reason = f"检测到关键词：{', '.join(keywords)}，适合{theme_name}风格"
        
        return theme_id, confidence, reason


def convert_markdown_to_wechat_html(markdown_text: str, theme: str = None) -> str:
    """
    便捷函数：将 Markdown 转换为微信 HTML
    
    Args:
        markdown_text: Markdown 文本
        theme: 主题名称，格式为 "category/name" 或 "name"
               例如: "wenyan/default", "macaron/pink", "default"
    
    Returns:
        转换后的 HTML 字符串
    """
    converter = WeChatHTMLConverter(theme=theme)
    return converter.convert(markdown_text)


def list_available_themes() -> Dict[str, Dict[str, List[str]]]:
    """
    列出所有可用主题
    
    Returns:
        {category: [theme_name1, theme_name2, ...]}
    """
    return ThemeLoader.list_themes()


def get_theme_list_detailed() -> Dict[str, Dict[str, str]]:
    """
    获取所有主题的详细信息
    
    Returns:
        {theme_id: {name, description}}
    """
    result = {}
    all_themes = ThemeLoader.list_themes()
    
    for category, names in all_themes.items():
        for name in names:
            theme_id = f"{category}/{name}"
            try:
                info = ThemeLoader.get_theme_info(theme_id)
                result[theme_id] = {
                    "name": info.get("name", name),
                    "description": info.get("description", ""),
                    "category": category
                }
            except Exception:
                result[theme_id] = {
                    "name": name,
                    "description": "加载失败",
                    "category": category
                }
    
    return result


# 测试
if __name__ == "__main__":
    test_md = """
# 测试文章

这是一段普通文字，**加粗**，*斜体*。

## 代码示例

```python
print("Hello, World!")
```

### 列表

- 项目1
- 项目2
- 项目3

> 这是一段引用

[链接](https://example.com)

---

分隔线测试
"""
    
    print("=" * 60)
    print("可用主题列表：")
    print("=" * 60)
    
    themes = list_available_themes()
    for category, names in themes.items():
        print(f"\n📁 {category}/")
        for name in names:
            theme_id = f"{category}/{name}"
            info = ThemeLoader.get_theme_info(theme_id)
            print(f"   🎨 {name}: {info.get('name', name)}")
            print(f"      {info.get('description', '')}")
    
    print("\n" + "=" * 60)
    print("主题推荐测试：")
    print("=" * 60)
    
    test_content = "这是一篇关于Python编程和AI人工智能的技术文章"
    theme_id, confidence, reason = WeChatHTMLConverter.recommend_theme(test_content)
    print(f"推荐主题: {theme_id}")
    print(f"置信度: {confidence:.2f}")
    print(f"原因: {reason}")
    
    print("\n" + "=" * 60)
    print("转换测试 (使用推荐主题)：")
    print("=" * 60)
    
    converter = WeChatHTMLConverter(theme=theme_id)
    html = converter.convert("# 主题预览\n\n这是一段测试文字**加粗显示**")
    print(html[:500] + "...")