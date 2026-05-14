---
name: teacher-assistant
description:  |
    Teacher Office Assistant - Complete home-school communication and student grade management system. Triggers：(1) User mentions student grades, parent communication (2) Need to analyze student data (3) Send email to parent (auto-generates and sends Word grade report) (4) Upload new grade files (5) Generate student reports. Supports: Feishu/WeCom/DingTalk/Excel data reading, grade analysis comparison, Word report generation, email sending (with attachments), private message sending.
---

# Teacher Office Assistant Skill

A complete home-school communication and student grade management system for automating daily teaching tasks.

---

## ✅ Configuration

### Feishu App Credentials - Auto-detected

**No manual configuration needed!** Built-in scripts automatically read Feishu credentials from `~/.openclaw/openclaw.json`:

```
Config path: channels.feishu.accounts.<account_id>
Read fields: appId, appSecret
```

**Prerequisite**: OpenClaw has Feishu bot account configured (in `openclaw.json`)

**Verification**:
```bash
python skills/teacher-assistant/scripts/feishu_utils.py
# Output: ✅ Found Feishu credentials / ✅ Got access_token successfully
```

---

### 🔧 Group Chat Configuration (Important)

#### Step 1: Add Bot to Group Chat

**Method 1: Via Group Settings**
1. Open target group chat
2. Click group name → Enter "Group Settings"
3. Click "Add Robot"
4. Select your bot

**Method 2: Via Bot Homepage**
1. Search bot name in Feishu
2. Open bot homepage
3. Click "Add to Group Chat"
4. Select target group

#### Step 2: Enable Bot Group Chat Permissions

Enable the following permissions in Feishu Open Platform:

| Permission | Description | Required |
|------------|-------------|----------|
| `im:message` | Send messages | ✅ Required |
| `im:message.group_msg` | Receive group messages | ✅ Required |
| `im:chat.members:read` | Read group member list | ✅ Required |
| `im:message:send_as_bot` | Send as bot identity | ✅ Required |
| `im:message:update` | Update sent messages | Optional |
| `im:message:recall` | Recall messages | Optional |
| `im:message.reactions:read` | Read message reactions | Optional |

**How to Enable**:
1. Login to Feishu Open Platform → Your App
2. Left menu "Permission Management" → "Permission Config"
3. Search and check the above permissions
4. Click "Publish Version" to apply

#### Step 3: Configure Event Subscription

**Required Event**: `im.message.receive_v1`

**Configuration**:
1. Feishu Open Platform → Your App → "Event Subscription"
2. Add event: `im.message.receive_v1`
3. Save and publish

#### Step 4: Verify Configuration

**Verify bot works correctly**:
1. @mention bot in group and send message
2. Bot should receive and reply

**Verify group member reading**:
```
User: Show group member list
Assistant: ✅ Successfully got group member list (X members)
```

---

## ⚠️ Core Principles

### 1. Single Agent Architecture

**All tasks execute directly in current workspace**, no sub-agents, no additional workspaces.

### 2. Student Records and Exam Scores as Long-term Memory

**Must write to long-term memory**:
- Student records → `data/students.json` → Write to MEMORY.md
- Exam scores → `data/grades.json` → Write to MEMORY.md
- User config → `config.json` → Write to MEMORY.md

### 3. First-time Use Must Ask User

**All configurations must be provided by user**:
- ❌ No hardcoded tokens
- ❌ No preset email/auth codes
- ❌ No assumed student count
- ❌ No test data
- ❌ No assumed user info

### 4. Important Info to Long-term Memory

**Must write to MEMORY.md**:
- Email config (email, auth code)
- Data source tokens (student records, grade summary)
- Parent group ID, target folder token
- Class info (grade, class, year)

---

## 📜 Built-in Scripts

The skill includes Python scripts that auto-read Feishu credentials from `openclaw.json`:

### 1. `scripts/feishu_utils.py` - Feishu Utils Module

**Features**:
- Auto-read Feishu App credentials from OpenClaw config
- Get tenant_access_token
- Read spreadsheet sheet list
- Read sheet data range
- Parse table data to dict list

**Usage**:
```python
from feishu_utils import get_access_token, read_sheet_range, parse_table_data

token = get_access_token()
values = read_sheet_range(token, spreadsheet_token, sheet_id)
records = parse_table_data(values)
```

### 2. `scripts/read_sheet.py` - Read Spreadsheet

**CLI Usage**:
```bash
python scripts/read_sheet.py <spreadsheet_token> [sheet_id]
```

**Examples**:
```bash
# Read student archive
python scripts/read_sheet.py GSDVxxxxb

# Read specific sheet
python scripts/read_sheet.py SXlnsxxxxf CNxxxc
```

### 3. `scripts/analyze_exams.py` - Exam Score Comparison

**CLI Usage**:
```bash
python scripts/analyze_exams.py <spreadsheet_token> <sheet1_id> <sheet2_id> <exam1_name> <exam2_name>
```

**Example**:
```bash
python scripts/analyze_exams.py SXxxxxxUf CNxxVc iixxOO 2025-11-12 2025-10-25
```

**Output**:
- Improved/declined student list
- Subject average comparison
- Score range distribution changes

### 4. `scripts/student_report.py` - Generate Student Report

**CLI Usage**:
```bash
python scripts/student_report.py <student_name>
```

**Example**:
```bash
python scripts/student_report.py xxx
```

**Output**:
- Console display of complete grade report
- Save JSON format report to `data/reports/`

### 5. `scripts/send_word_report.py` - Send Word Grade Report (Recommended)

**CLI Usage**:
```bash
PYTHONPATH=lib python scripts/send_word_report.py <student_name> [parent_email]
```

**Example**:
```bash
PYTHONPATH=lib python scripts/send_word_report.py xxx parent@163.com
```

**Features**:
- Auto-fetch student's last 3 exam scores
- Generate Word format grade report (with tables)
- Send email to parent (with Word attachment)

**Word Report Content**:
- Basic info (name, class, student ID)
- Recent exam overview (table format)
- Subject score comparison (table format)
- Subject analysis (strengths/weaknesses)
- Teacher comments
- Home-school communication info

### 6. `scripts/send_email_report.py` - Send Plain Text Grade Report

**CLI Usage**:
```bash
python scripts/send_email_report.py <student_name> [parent_email]
```

**Example**:
```bash
python scripts/send_email_report.py xxx parent@163.com
```

**Features**:
- Send plain text format grade report
- No Word dependency required

---

## 📦 Dependencies

The skill uses the following Python libraries (pre-installed in `lib/` directory):

| Library | Version | Purpose |
|---------|---------|---------|
| python-docx | 1.2.0 | Generate Word documents |
| lxml | 6.1.0 | XML parsing (python-docx dependency) |
| typing-extensions | 4.15.0 | Type support |

**Usage**:
```bash
# When running scripts that need python-docx, specify PYTHONPATH
PYTHONPATH=lib python scripts/send_word_report.py xxx   parent@email.com
```

---

## 📊 Feishu Table Data Reading

### Method 1: Link Sharing Mode (Recommended)

**Setup Steps**:

1. Open Feishu spreadsheet
2. Click "Share" button (top right)
3. Select "Get Link"
4. Set permission to "Anyone can view" or "Organization can view"
5. Copy link and send to assistant

**Link Format Recognition**:

| Link Type | Format Example | Parse Method |
|-----------|----------------|--------------|
| Spreadsheet | `https://xxx.feishu.cn/sheets/XXX` | Extract spreadsheet_token |
| Bitable | `https://xxx.feishu.cn/base/XXX` | Extract app_token |
| With Sheet | `https://xxx.feishu.cn/sheets/XXX?sheet=YYY` | Extract token + sheet_id |

### Method 2: Feishu API Mode

**Prerequisite**: Feishu app has required permissions

**Required Permissions**:

| Permission | Purpose | Required |
|------------|---------|----------|
| `sheets:spreadsheet:readonly` | Read spreadsheet | ✅ |
| `bitable:record:readonly` | Read bitable | Optional |
| `contact:user.base:readonly` | Query user by phone | Optional |
| `im:message` | Send private message | Optional |

### Reading Flow

```
User provides link
    ↓
Parse link type (sheets/base)
    ↓
Extract token and sheet_id
    ↓
Call Feishu API to read data
    ↓
Convert to JSON format
    ↓
Save to data/ directory
    ↓
Update MEMORY.md
```

---

## Directory Structure

```
workspace/
├── MEMORY.md                   # Long-term memory (config + data summary)
├── config.json                 # User configuration (email, data sources, etc.)
├── lib/                        # Python dependencies
│   ├── docx/                   # python-docx
│   ├── lxml/                   # lxml
│   └── typing_extensions.py    # typing-extensions
├── data/
│   ├── students.json           # Student basic info
│   ├── grades.json             # Exam score data
│   └── reports/                # Generated reports
│       ├── xxx_成绩报告.docx
│       ├── xxx_成绩报告.txt
│       └── ...
├── cache/                      # Data cache
│   ├── Class1_Grade7_2025/
│   │   ├── students.json
│   │   └── grades.json
│   └── Class2_Grade7_2025/
│       ├── students.json
│       └── grades.json
└── skills/
    └── teacher-assistant/
        ├── SKILL.md            # English docs
        ├── SKILL_CN.md         # Chinese docs
        └── scripts/
            ├── feishu_utils.py     # Feishu utils module
            ├── read_sheet.py       # Read spreadsheet
            ├── analyze_exams.py    # Exam score analysis
            ├── student_report.py   # Generate student report
            ├── send_word_report.py # Send Word report (recommended)
            └── send_email_report.py # Send plain text report
```

---

## First-time Usage Flow

### Step 0: Skill Introduction

```
👋 Welcome to Teacher Office Assistant!

I'm your intelligent teaching assistant, I can help you:

📊 Student Grade Management
   - Auto-read Feishu table data (supports link sharing mode)
   - Auto-import uploaded Excel
   - Compare and analyze exam score changes

📈 Data Analysis & Statistics
   - Individual student grade analysis report
   - Class-wide grade statistics analysis
   - Track improved/declined students

📧 Home-School Communication
   - Auto-generate Word format grade reports
   - Send emails to parents (with report attachment)
   - Feishu private message notification to parents

---

⚠️ First-time use requires the following:

Required config:
1. 📊 Student data source (choose one)
   - Feishu table link (recommended: set link sharing to "can view")
   - Upload Excel file

2. 📧 Email config (for sending reports)
   - Sender email address
   - Email auth code (not password!)
   - Sender display name

Optional config:
3. 🔧 Other config
   - Grade summary table link
   - Parent group ID (for private messages)
   - Target folder token (for storage)

---

Please provide Feishu table link or upload Excel file to start.
```

### Step 1: Read Student Records

**When user provides Feishu table link**:

```
User provides link: https://xxx.feishu.cn/sheets/XXX
    ↓
Assistant parses link type
    ↓
Assistant calls Feishu API to read data
    ↓
Assistant saves to data/students.json
    ↓
Assistant updates MEMORY.md
    ↓
Assistant shows data summary:
    - Total students: XX
    - Class: Grade 7 Class 1
    - Fields: student_id, name, class, ...
```

### Step 2: Configure Email (Ask when sending reports)

```
User: Send report to XX's parent
Assistant: Email not configured, please provide:
      1. Sender email: ?
      2. Auth code: ?
      3. Sender name: ?
```

---

## Data Source Support

### Supported Platforms

| Platform | Recognition | Read Method | Link Sharing |
|----------|-------------|-------------|--------------|
| **Feishu Spreadsheet** | `feishu.cn/sheets` | Feishu API | ✅ Supported |
| **Feishu Bitable** | `feishu.cn/base` | Feishu API | ✅ Supported |
| **WeCom** | `work.weixin.qq.com` | Upload Excel | ❌ |
| **DingTalk** | `dingtalk.com` | DingTalk API | ⚠️ Partial |
| **Excel** | `.xlsx` / `.xls` | Direct read | N/A |

---

## Analysis Features

### Individual Student Analysis

Generate personal grade report including:
- Student basic info
- Last 3 exam score comparison
- Grade change analysis (rank, total, subjects)
- Teacher comments and suggestions
- Home-school communication info

### Class-wide Analysis

Generate class overall report including:

| Analysis Item | Description |
|---------------|-------------|
| Class Overview | Total count, average, max, min, pass rate |
| Rank Distribution | Top 10, middle, bottom 10 student list |
| Improvement Stats | Improved count, declined count, unchanged count |
| Improvement Stars | Top 5 students with biggest improvement |
| Focus Attention | Top 5 students with biggest decline |
| Subject Analysis | Each subject's average, max, min, trend |
| Score Range Distribution | 600+, 550-599, 500-549, 450-499, 400-449, below 400 counts |

---

## Home-School Communication Rules

### Send Method Detection

| User Instruction | send_method |
|------------------|-------------|
| Explicitly says "send email" | `"email"` - Generate Word report → Send email |
| Explicitly says "only private message" | `"chat"` - Only send private message |
| Not specified | `"both"` - Generate Word report → Send email + private message |

### Private Message Platform Selection

| Data Source | Platform |
|-------------|----------|
| Feishu | Feishu private message |
| WeCom | WeCom private message |
| DingTalk | DingTalk private message |

---

## Data Structure

### Student Records Table

| Field | Type | Description |
|-------|------|-------------|
| student_id | int | Unique identifier |
| name | string | Student name |
| class | string | e.g., Grade 7 Class 1 |
| gender | string | Male/Female |
| age | int | Student age |
| parent_name | string | |
| relationship | string | Father/Mother/Other |
| parent_phone | string | |
| parent_email | string | |
| parent_feishu_id | string | Parent's Feishu open_id (optional, starts with ou_) |
| boarding | string | Yes/No |
| weak_subjects | string | Multiple separated by comma |
| talents | string | |

### Grade Summary Table

Each sheet represents one exam, naming format: `YYYY-MM-DD`

| Field | Type | Description |
|-------|------|-------------|
| exam_date | date | YYYY-MM-DD |
| student_id | int | Link to student records |
| name | string | |
| class_rank | int | |
| grade_rank | int | |
| total_score | int | |
| average | float | |
| chinese | int | |
| math | int | |
| english | int | |
| politics | int | |
| history | int | |
| geography | int | |
| biology | int | |

---

## Error Handling

### Common Issues

| Issue | Solution |
|-------|----------|
| Link inaccessible | Check if link sharing permission is set to "can view" |
| Config not initialized | Prompt user to provide config |
| Student not found | Check if student_id is correct |
| Parent not in group | Prompt user to invite parent |
| Email send failed | Check SMTP config |
| API error | Check if token is valid |

---

## Usage Examples

### Read Feishu Table
```
User: Here's the student records: https://xxx.feishu.cn/sheets/XXX
Assistant: Reading Feishu table...
      ✅ Link parsed successfully
      ✅ Data read successfully
      ✅ Saved to data/students.json
      
      Data summary:
      - Total students: xx
      - Class: Grade 7 Class 1
      - Fields: student_id, name, class, gender, age, parent_name, ...
```

### Send Email to Parent
```
User: Send email to xxx's parent
Assistant: Email not configured, please provide:
      1. Sender email: ?
      2. Auth code: ?
      3. Sender name: ?

User: QQ email <email>, auth code: xxx

Assistant: Fetching xxx's grade data...
      ✅ Found 3 exam records
      Generating Word report...
      ✅ Word report generated: data/reports/xxx_成绩报告.docx
      Sending email to parent@163.com...
      ✅ Email sent successfully (with Word attachment)!
```

**⚠️ Send email = Auto-generate and send Word report**
- Email always includes Word format grade report as attachment
- No need to mention "send Word report" separately
- Parent receives complete report with attachment

### Send Private Message to Parent

**⚠️ IMPORTANT: Private messages must be sent privately, NEVER in group!**

**Flow**:
```
User: Send private message to xxx's parent
    ↓
Assistant executes:
    1. Find parent's Feishu ID in group (via @mention or phone lookup)
    2. Send private message to parent (one-on-one)
    ↓
✅ Private message sent to parent
```

**⚠️ Core Rules**:
- **Private message = Private send (one-on-one)**
- **NEVER send private content in group chat**
- Group messages only for announcements and public content

---

## Private Message Permissions

### Feishu Private Message

| Permission | Description |
|------------|-------------|
| `im:chat.members:read` | Get group member list |
| `im:message` | Send private message |

**Prerequisites**:
1. Parent must join Feishu organization
2. Bot must be able to private message the user

**On failure**: Auto-prompt user to enable required permissions

### WeCom (Enterprise WeChat) Private Message

| Condition | Description |
|-----------|-------------|
| **Prerequisite** | Parent must join enterprise organization |
| **Add method** | Invite parent via phone/email |
| **Message method** | Bot sends application message |

**Limitation**: Cannot private message users outside organization

### DingTalk Private Message

| Condition | Description |
|-----------|-------------|
| **Prerequisite** | Parent must join DingTalk organization |
| **Add method** | Invite parent via phone |
| **Message method** | Bot sends work notification |
| **Alternative** | Group @mention or DING message |

**Limitation**: Cannot private message users outside organization

---

## New Environment Deployment

Just copy the skill directory:

```bash
cp -r skills/teacher-assistant/ /path/to/new/server/skills/
```

**Configuration Steps**:
1. Configure Feishu credentials (`~/.openclaw/openclaw.json`)
2. Provide Feishu table link or upload Excel on first use
