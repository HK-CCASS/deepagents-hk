---
name: hkex-announcement-analysis
description: Structured approach to analyzing HKEX announcements (placements, rights offerings, results)
---

# HKEX Announcement Analysis Skill

## When to Use This Skill

Use this skill when you need to:
- Analyze placement (配售) announcements
- Evaluate rights offering (供股) announcements
- Review interim/annual results announcements
- Compare multiple HKEX announcements
- Extract key metrics from announcements

## Announcement Types and Key Metrics

### 1. Placement (配售)
**Key Information to Extract:**
- Number of shares placed (配售股份数量)
- Subscription price (认购价)
- Discount to market price (较市价折让)
- Use of proceeds (所得款项用途)
- Subscribers (认购人)
- Conditions precedent (先决条件)

### 2. Rights Offering (供股)
**Key Information to Extract:**
- Subscription ratio (供股比例) e.g., "1-for-1"
- Subscription price (认购价)
- Underwriting arrangement (包销安排)
- Irrevocable undertakings (不可撤回承诺)
- Expected timetable (预期时间表)
- Use of proceeds (所得款项用途)

### 3. Results Announcement (业绩公告)
**Key Information to Extract:**
- Revenue (收入)
- Profit/Loss (盈利/亏损)
- EPS (每股盈利)
- Dividend (股息)
- Year-on-year comparison (同比变化)
- Management discussion (管理层讨论)

## Analysis Process

### Step 1: Search and Download

1. **Search for announcements** using the search_hkex_announcements tool:
```
# First get current date
date +%Y%m%d

# Then search (use from_date/to_date, NOT start_date/end_date)
search_hkex_announcements(
    stock_code="00700",
    from_date="20251101",
    to_date="20251120"
)
# Note: Filter by keywords manually from results (title field)
```

2. **Download the PDF** using download_announcement_pdf:
```
download_announcement_pdf(
    news_id="[NEWS_ID from search results]",
    pdf_url="[PDF_URL from search results]",
    stock_code="00700",
    date_time="[DATE_TIME from search results]",
    title="[TITLE from search results]"
)
```

### Step 2: Extract Content

1. **Extract text and tables** using extract_pdf_content:
```
extract_pdf_content(pdf_path="[cached PDF path]")
```

2. **Analyze structure** using analyze_pdf_structure:
```
analyze_pdf_structure(pdf_path="[cached PDF path]")
```

### Step 3: Extract Key Metrics

**For Placements:**
- Search for "配售价" or "Subscription Price"
- Search for "配售股份" or "Placement Shares"
- Search for "折讓" or "Discount"
- Search for "認購人" or "Placee"
- Search for "所得款項用途" or "Use of Proceeds"

**For Rights Offerings:**
- Search for "供股比例" or "Subscription Ratio"
- Search for "供股價" or "Subscription Price"
- Search for "包銷" or "Underwriting"
- Search for "承諾" or "Undertaking"
- Search for "時間表" or "Timetable"

**For Results:**
- Search for "收入" or "Revenue"
- Search for "利潤" or "Profit"
- Search for "每股盈利" or "EPS"
- Search for "股息" or "Dividend"

### Step 4: Generate Structured Summary

**Write summary** using generate_summary_markdown or write_file:
```
# Use /md/ directory (project standard)
write_file(
    path="/md/[stock_code]-[event_type]-analysis.md",
    content="[Structured summary with all key metrics]"
)
```

**Summary Template for Placements:**
```markdown
# [Stock Code] 配售公告分析

## 基本信息
- **股票代码**: [code]
- **公司名称**: [name]
- **公告日期**: [date]

## 配售详情
- **配售股份数量**: [number] 股
- **配售价**: HK$ [price]
- **较市价折让**: [discount]%
- **认购人**: [placee names]

## 所得款项用途
1. [Use 1]: HK$ [amount]
2. [Use 2]: HK$ [amount]

## 市场影响
- **摊薄效应**: [dilution]%
- **集资额**: HK$ [total amount]

## 关键条款
- [Key terms and conditions]
```

### Step 5: Comparison (if requested)

Use the task tool to spawn a subagent for isolated analysis:
```
task(
    description="Compare this placement with similar ones from the past 6 months. Search for placements, download PDFs, extract key metrics, and return a comparison table.",
    subagent_type="general-purpose"
)
```
> Note: Subagent has same tools as main agent. Use for context isolation.

## Best Practices

**Do's:**
- ✅ Always download and cache PDFs first
- ✅ Extract both text and tables for complete information
- ✅ Cross-reference multiple sections for accuracy
- ✅ Use structured markdown for summaries
- ✅ Include source references (page numbers)

**Don'ts:**
- ❌ Don't guess metrics if not found in PDF
- ❌ Don't skip table data (often contains key metrics)
- ❌ Don't ignore footnotes and conditions
- ❌ Don't mix up traditional/simplified Chinese amounts

## Common Pitfalls

1. **Currency confusion**: Check if amounts are in HK$, RMB, or USD
2. **Share units**: Confirm if in shares, lots (手), or millions
3. **Date formats**: HKEX uses DD/MM/YYYY format
4. **Traditional Chinese**: HKEX announcements use traditional Chinese (繁體)

## Example Workflow

**User Request**: "分析00700最新的配售公告"

**Execution Steps:**
1. Get current date: `date +%Y%m%d` (e.g., "20251120")
2. Calculate date range: from_date = 1 year ago, to_date = today
3. Search announcements: `search_hkex_announcements(stock_code="00700", from_date="20241120", to_date="20251120")`
4. Filter results for "配售" in title
5. Download PDF: `download_announcement_pdf(news_id=..., pdf_url=..., stock_code="00700", date_time=..., title=...)`
6. Extract content: `extract_pdf_content([PDF path])`
7. Identify key metrics from extracted text/tables
8. Write summary: `write_file("/md/00700-配售分析.md", [content])`
9. Present summary to user

## Supporting Files

This skill can work with optional helper scripts:
- `parse_placement.py`: Extract placement-specific metrics
- `parse_rights_offering.py`: Extract rights offering metrics
- `parse_results.py`: Extract financial results

Place scripts in the same directory as this SKILL.md file.

