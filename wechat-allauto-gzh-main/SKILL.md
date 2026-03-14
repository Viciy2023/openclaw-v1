---
name: wechat-allauto-gzh
description: WeChat Official Account management and Markdown to HTML conversion for publishing articles
---

# WeChat Official Account Skill

Automate WeChat Official Account operations including Markdown formatting, article publishing, draft management, and full API capabilities.

## Core Workflow

When you receive end-to-end tasks like "write an article about XXX and publish to Official Account", follow this workflow:

1. **Content Creation**: Generate high-quality Markdown article based on user requirements
2. **Fact Checking** (if needed): Use `tavily_search` to verify key data and facts
3. **Format Conversion**: Call `convert_markdown_to_wechat_html` to convert Markdown to WeChat-compatible inline-style HTML
4. **Cover Image**: Generate or select appropriate cover image for the article
5. **Publish/Draft**: Call `wechat_manage_capability` to save to draft box or publish directly
6. **Scheduled Publishing**: Can integrate with `cron_job` for automated scheduled posts

## Available Tools

### 1. convert_markdown_to_wechat_html

Convert Markdown text to WeChat Official Account compatible HTML with inline CSS styles.

**Usage**:
```python
import sys
sys.path.append('/root/.openclaw/skills/wechat-allauto-gzh/src/skills')
from wechat_formatter_skill import convert_markdown_to_wechat_html

html_content = convert_markdown_to_wechat_html(
    markdown_content="# Title\n\nContent here...",
    theme_name="default",  # Options: default, macaron, wenyan, shuimo
    themes_dir="/root/.openclaw/skills/wechat-allauto-gzh/src/themes"
)
```

**Parameters**:
- `markdown_content` (str, required): Markdown text to convert
- `theme_name` (str, optional): Theme name (default, macaron, wenyan, shuimo). Default: "default"
- `themes_dir` (str, optional): Path to themes directory. Default: "./themes"

**Returns**: HTML string with inline CSS styles

**Use Cases**:
- User requests "format article" or "beautify article"
- User needs "preview Official Account effect"
- Preparing content for API push to draft box

### 2. wechat_manage_capability

Unified interface for all WeChat Official Account API operations with automatic Access Token management.

**Usage**:
```python
import sys
sys.path.append('/root/.openclaw/skills/wechat-allauto-gzh/src/skills')
from wechat_capability_skill import wechat_manage_capability

# Load credentials
import json
with open('/root/.openclaw/skills/wechat-allauto-gzh/credentials.json', 'r') as f:
    creds = json.load(f)

# Add draft
result = wechat_manage_capability(
    app_id=creds['AppID'],
    app_secret=creds['AppSecret'],
    capability="draft",
    action="add",
    articles=[{
        "title": "Article Title",
        "author": "Author Name",
        "digest": "Article summary",
        "content": "<html>...</html>",
        "content_source_url": "https://example.com",
        "thumb_media_id": "MEDIA_ID",
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }]
)
```

**Parameters**:
- `app_id` (str, required): WeChat Official Account AppID
- `app_secret` (str, required): WeChat Official Account AppSecret
- `capability` (str, required): API capability category
- `action` (str, required): Specific action within the capability
- `**kwargs`: Additional parameters specific to the action

**Supported Capabilities**:

#### menu (Custom Menu)
- Actions: `create`, `get`, `delete`
- Example: Create menu, get current menu, delete menu

#### draft (Draft Box)
- Actions: `add`, `get`, `delete`, `update`, `count`, `batchget`
- Example: Add draft, get draft by media_id, delete draft, update draft, count drafts, batch get drafts

#### publish (Publishing)
- Actions: `submit`, `get_status`, `delete`, `get_article`, `batchget`
- Example: Submit for publishing, check publish status, delete published article

#### material (Permanent Materials)
- Actions: `get`, `delete`, `count`, `batchget`
- Example: Get material, delete material, count materials, batch get materials

#### user (User Management)
- Actions: `get_list`, `get_info`, `update_remark`
- Example: Get user list, get user info, update user remark

#### comment (Comment Management)
- Actions: `open`, `close`, `list`, `markelect`, `unmarkelect`, `delete`, `reply`, `delete_reply`
- Example: Open comments, close comments, list comments, mark/unmark selected comments

#### message (Messaging & Mass Sending)
- Actions: `send_custom`, `send_mass`
- Example: Send custom message, send mass message

#### kf (Customer Service)
- Actions: `add`, `get_list`
- Example: Add customer service account, get customer service list

#### analysis (Data Analytics)
- Actions: `get_article_summary`, `get_user_summary`
- Example: Get article statistics, get user statistics

**Returns**: Dictionary with API response
- Success: `{"errcode": 0, "errmsg": "ok", ...}`
- Failure: `{"errcode": <non-zero>, "errmsg": "<error message>"}`

**Use Cases**:
- User requests "update bottom menu", "check draft box", "send mass message", "check fan data", "manage comments"

## Interaction Guidelines

1. **Credential Security**: Always load AppID and AppSecret from `/root/.openclaw/skills/wechat-allauto-gzh/credentials.json`. Never use placeholders or make up credentials.

2. **Error Handling**: If API returns error (`errcode != 0`), explain the error in human-readable language (e.g., "AppSecret incorrect", "IP not in whitelist", "API call frequency exceeded") and provide fix suggestions.

3. **Confirmation**: Before destructive operations (delete menu, delete published article) or formal publishing (`publish` -> `submit`), ask user for confirmation.

4. **Preview**: After Markdown to HTML conversion, show user a preview or confirm conversion success before pushing to draft box.

5. **Proactive Fixes**: If encountering bugs or exceptions, analyze the error and propose fixes (with user consent).

6. **Plug-and-Play**: This skill supports plug-and-play architecture. Functions can be added or removed as needed.

## Example: Complete Publishing Workflow

```python
import sys
import json
sys.path.append('/root/.openclaw/skills/wechat-allauto-gzh/src/skills')
from wechat_formatter_skill import convert_markdown_to_wechat_html
from wechat_capability_skill import wechat_manage_capability

# 1. Load credentials
with open('/root/.openclaw/skills/wechat-allauto-gzh/credentials.json', 'r') as f:
    creds = json.load(f)

# 2. Convert Markdown to HTML
markdown_text = """
# 月亮之歌

皎洁明月挂苍穹，
清辉普照大地中。
"""

html_content = convert_markdown_to_wechat_html(
    markdown_content=markdown_text,
    theme_name="macaron",
    themes_dir="/root/.openclaw/skills/wechat-allauto-gzh/src/themes"
)

# 3. Add to draft box
result = wechat_manage_capability(
    app_id=creds['AppID'],
    app_secret=creds['AppSecret'],
    capability="draft",
    action="add",
    articles=[{
        "title": "月亮之歌",
        "author": "林可菲",
        "digest": "一首关于月亮的七言诗",
        "content": html_content,
        "thumb_media_id": "COVER_IMAGE_MEDIA_ID"
    }]
)

print(f"Draft added: {result}")
```

## Notes

- All Python skill files are located in `/root/.openclaw/skills/wechat-allauto-gzh/src/skills/`
- Credentials file: `/root/.openclaw/skills/wechat-allauto-gzh/credentials.json`
- Themes directory: `/root/.openclaw/skills/wechat-allauto-gzh/src/themes/`
- Access Token is automatically managed with caching and expiry retry
