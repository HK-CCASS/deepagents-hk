# 港交所（HKEX）原始API接口文档

**基础URL**: `https://www1.hkexnews.hk`  
**文档版本**: v1.0.0  
**最后更新**: 2025-11-07

---

## 目录

1. [股票ID查询接口](#1-股票id查询接口)
2. [公告搜索接口](#2-公告搜索接口)
3. [最新公告接口](#3-最新公告接口)
4. [分类数据接口](#4-分类数据接口)
5. [请求头要求](#5-请求头要求)
6. [响应格式说明](#6-响应格式说明)
7. [注意事项](#7-注意事项)

---

## 1. 股票ID查询接口

### 1.1 接口信息

**端点**: `/search/prefix.do`

**方法**: `GET`

**描述**: 根据股票代码查询港交所内部股票ID

**完整URL示例**:
```
https://www1.hkexnews.hk/search/prefix.do?callback=callback&lang=ZH&type=A&name=00673&market=SEHK&_=1653821865437
```

### 1.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| callback | string | 是 | JSONP回调函数名 | "callback" |
| lang | string | 是 | 语言代码：ZH（中文）/EN（英文） | "ZH" |
| type | string | 是 | 类型：A（股票） | "A" |
| name | string | 是 | 5位股票代码 | "00673" |
| market | string | 是 | 市场：SEHK（主板） | "SEHK" |
| _ | string | 否 | 时间戳（防缓存） | "1653821865437" |

### 1.3 响应格式

**响应类型**: JSONP（JSON with Padding）

**响应示例**:
```javascript
callback({
  "stockInfo": [
    {
      "stockId": "12345",
      "stockCode": "00673",
      "stockName": "中國衛生集團",
      "market": "SEHK"
    }
  ]
})
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| stockInfo | array | 股票信息列表 |
| stockInfo[].stockId | string | 内部股票ID（用于后续搜索） |
| stockInfo[].stockCode | string | 股票代码 |
| stockInfo[].stockName | string | 股票名称 |
| stockInfo[].market | string | 市场代码 |

### 1.4 错误情况

**股票不存在**:
```javascript
callback({
  "stockInfo": []
})
```

### 1.5 实现位置

**项目中使用位置**: `app/services/hkex_service.py:70-115`

**关键代码**:
```python
url = (
    f"{self.base_url}/search/prefix.do?"
    f"callback=callback&lang=ZH&type=A&name={stock_code}"
    f"&market=SEHK&_=1653821865437"
)
```

---

## 2. 公告搜索接口

### 2.1 接口信息

**端点**: `/search/titleSearchServlet.do`

**方法**: `GET`

**描述**: 根据股票ID、日期范围、关键词等条件搜索公告

**完整URL示例**:
```
https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId=12345&documentType=-1&fromDate=20250101&toDate=20251008&title=年報&searchType=0&t1code=-2&t2Gcode=-2&t2code=-2&rowRange=100&lang=zh
```

### 2.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| sortDir | integer | 否 | 排序方向：0（降序）/1（升序） | 0 |
| sortByOptions | string | 否 | 排序字段：DateTime（日期时间） | "DateTime" |
| category | integer | 否 | 分类：0（全部） | 0 |
| market | string | 是 | 市场：SEHK（主板） | "SEHK" |
| stockId | string | 是 | 内部股票ID（通过prefix.do获取） | "12345" |
| documentType | integer | 否 | 文档类型：-1（全部） | -1 |
| fromDate | string | 是 | 开始日期（YYYYMMDD格式） | "20250101" |
| toDate | string | 是 | 结束日期（YYYYMMDD格式） | "20251008" |
| title | string | 否 | 搜索关键词 | "年報" |
| searchType | integer | 否 | 搜索类型：0（标题搜索） | 0 |
| t1code | string | 否 | 一级分类代码：-2（全部） | "-2" |
| t2Gcode | string | 否 | 二级分组代码：-2（全部） | "-2" |
| t2code | string | 否 | 二级分类代码：-2（全部） | "-2" |
| rowRange | integer | 否 | 返回数量：1-500 | 100 |
| lang | string | 否 | 语言：zh（中文）/en（英文） | "zh" |

### 2.3 响应格式

**响应类型**: JSON（但可能包含转义字符）

**响应示例**:
```json
{
  "result": "[{\"TITLE\":\"公告标题\",\"DATE_TIME\":\"08/10/2025 16:46\",\"FILE_LINK\":\"/listedco/listconews/sehk/2025/1008/file.pdf\",\"NEWS_ID\":\"11871132\",\"STOCK_CODE\":\"00673\",\"STOCK_NAME\":\"中國衛生集團\",\"FILE_TYPE\":\"PDF\",\"FILE_INFO\":\"127KB\",\"SHORT_TEXT\":\"翌日披露報表 - [其他]\",\"LONG_TEXT\":\"翌日披露報表 - [其他]\"}]"
}
```

**注意**: `result`字段可能是JSON字符串，需要二次解析

**解析后的result示例**:
```json
[
  {
    "TITLE": "公告标题",
    "DATE_TIME": "08/10/2025 16:46",
    "FILE_LINK": "/listedco/listconews/sehk/2025/1008/file.pdf",
    "NEWS_ID": "11871132",
    "STOCK_CODE": "00673",
    "STOCK_NAME": "中國衛生集團",
    "FILE_TYPE": "PDF",
    "FILE_INFO": "127KB",
    "SHORT_TEXT": "翌日披露報表 - [其他]",
    "LONG_TEXT": "翌日披露報表 - [其他]"
  }
]
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| result | string/array | 结果列表（可能是JSON字符串） |
| result[].TITLE | string | 公告标题 |
| result[].DATE_TIME | string | 日期时间（格式：dd/mm/yyyy HH:MM） |
| result[].FILE_LINK | string | PDF文件相对路径 |
| result[].NEWS_ID | string | 新闻ID |
| result[].STOCK_CODE | string | 股票代码（可能包含HTML编码） |
| result[].STOCK_NAME | string | 股票名称（可能包含HTML编码） |
| result[].FILE_TYPE | string | 文件类型（通常为PDF） |
| result[].FILE_INFO | string | 文件信息（大小等） |
| result[].SHORT_TEXT | string | 简短描述文本 |
| result[].LONG_TEXT | string | 详细描述文本 |

### 2.4 响应数据清理

**问题**: 响应数据包含转义字符和特殊编码

**需要清理的内容**:
1. JSON字符串转义：`"[{` → `[{`，`}]"` → `}]`
2. 反斜杠转义：`\\` → 空
3. Unicode编码：`u2013` → `-`，`u0026` → `-`
4. HTML编码：`&lt;` → `<`，`&gt;` → `>`
5. 字面字符串编码：`u003c` → `<`，`u003e` → `>`

**实现位置**: `app/services/hkex_service.py:181-187`

### 2.5 日期格式处理

**输入格式**: `YYYYMMDD`（如：`20250101`）  
**响应格式**: `dd/mm/yyyy HH:MM`（如：`08/10/2025 16:46`）

**实现位置**: `app/services/hkex_service.py:220-228`

### 2.6 PDF链接构建

**相对路径**: `/listedco/listconews/sehk/2025/1008/file.pdf`  
**完整URL**: `https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1008/file.pdf`

**实现位置**: `app/services/hkex_service.py:217`

### 2.7 实现位置

**项目中使用位置**: `app/services/hkex_service.py:117-275`

---

## 3. 最新公告接口

### 3.1 接口信息

**端点**: `/ncms/json/eds/lcisehk1relsdc_1.json`

**方法**: `GET`

**描述**: 获取港交所最新公告（无需股票代码，最多500条）

**完整URL示例**:
```
https://www1.hkexnews.hk/ncms/json/eds/lcisehk1relsdc_1.json
```

### 3.2 请求参数

**无查询参数**（所有过滤在客户端完成）

### 3.3 响应格式

**响应类型**: JSON

**响应示例**:
```json
{
  "newsInfoLst": [
    {
      "newsId": "11871132",
      "title": "截至2025年9月30日止六個月之中期業績公告",
      "relTime": "08/10/2025 16:46",
      "webPath": "/listedco/listconews/sehk/2025/1008/file.pdf",
      "ext": "PDF",
      "size": "127KB",
      "sTxt": "翌日披露報表 - [其他]",
      "lTxt": "翌日披露報表 - [其他]",
      "t1Code": "10000",
      "t2Code": "19850",
      "market": "SEHK",
      "stock": [
        {
          "sc": "00673",
          "sn": "中國衛生集團"
        }
      ]
    }
  ]
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| newsInfoLst | array | 新闻信息列表 |
| newsInfoLst[].newsId | string | 新闻ID |
| newsInfoLst[].title | string | 公告标题 |
| newsInfoLst[].relTime | string | 发布时间（格式：dd/mm/yyyy HH:MM） |
| newsInfoLst[].webPath | string | PDF文件相对路径 |
| newsInfoLst[].ext | string | 文件扩展名（PDF） |
| newsInfoLst[].size | string | 文件大小 |
| newsInfoLst[].sTxt | string | 简短描述文本 |
| newsInfoLst[].lTxt | string | 详细描述文本 |
| newsInfoLst[].t1Code | string | 一级分类代码（可能为"NaN"） |
| newsInfoLst[].t2Code | string | 二级分类代码（可能为"NaN"） |
| newsInfoLst[].market | string | 市场代码：SEHK/GEM |
| newsInfoLst[].stock | array | 股票信息列表 |
| newsInfoLst[].stock[].sc | string | 股票代码（可能包含HTML编码） |
| newsInfoLst[].stock[].sn | string | 股票名称（可能包含HTML编码） |

### 3.4 特点

- ✅ **无需股票代码**: 直接获取所有最新公告
- ✅ **包含分类代码**: `t1Code`和`t2Code`字段直接提供，无需文本解析
- ✅ **多股票支持**: 一个公告可能关联多个股票（`stock`数组）
- ✅ **实时更新**: 返回最新的公告列表

### 3.5 过滤逻辑

**客户端过滤**（非API参数）:
- `market`: 市场过滤（SEHK/GEM）
- `stock_code`: 股票代码过滤（从`stock[].sc`字段匹配）
- `t1_code`: 一级分类代码过滤
- `t2_code`: 二级分类代码过滤

**实现位置**: `app/services/hkex_service.py:374-391`

### 3.6 实现位置

**项目中使用位置**: `app/services/hkex_service.py:329-434`

---

## 4. 分类数据接口

### 4.1 接口信息

**端点**: `/ncms/script/eds/{category_file}.json`

**方法**: `GET`

**描述**: 获取港交所分类数据（文档类型、一级分类、二级分类等）

**完整URL示例**:
```
https://www1.hkexnews.hk/ncms/script/eds/doc_c.json
https://www1.hkexnews.hk/ncms/script/eds/tierone_c.json
https://www1.hkexnews.hk/ncms/script/eds/tiertwo_c.json
https://www1.hkexnews.hk/ncms/script/eds/tiertwogrp_c.json
```

### 4.2 分类文件列表

| 文件名 | 说明 | 用途 |
|--------|------|------|
| doc_c.json | 文档类型分类 | 文档类型代码映射 |
| tierone_c.json | 一级分类 | 一级分类代码映射 |
| tiertwo_c.json | 二级分类 | 二级分类代码映射 |
| tiertwogrp_c.json | 二级分组分类 | 二级分组代码映射 |

### 4.3 响应格式

**响应类型**: JSON数组

**响应示例**（tierone_c.json）:
```json
[
  {
    "code": "10000",
    "name": "公告及通告",
    "nameEn": "Announcements and Notices"
  },
  {
    "code": "50000",
    "name": "財務報表",
    "nameEn": "Financial Statements"
  }
]
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 分类代码 |
| name | string | 分类名称（中文） |
| nameEn | string | 分类名称（英文，可选） |

### 4.4 实现位置

**项目中使用位置**: `app/services/category_service.py:22-56`

---

## 5. 请求头要求

### 5.1 User-Agent

**要求**: 必须设置User-Agent，否则可能被拒绝

**默认值**:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**实现位置**: `app/services/hkex_service.py:23-30`

### 5.2 其他请求头

**无特殊要求**（Content-Type等由HTTP客户端自动处理）

---

## 6. 响应格式说明

### 6.1 JSONP格式

**使用场景**: 股票ID查询接口（`/search/prefix.do`）

**格式**: `callback({...})`

**解析方法**:
```python
match = re.search(r'callback\((.*)\)', response.text)
data = json.loads(match.group(1))
```

**实现位置**: `app/services/hkex_service.py:104-109`

### 6.2 JSON格式

**使用场景**: 公告搜索、最新公告、分类数据接口

**格式**: 标准JSON

**注意事项**:
- 公告搜索接口的`result`字段可能是JSON字符串，需要二次解析
- 某些字段值可能包含HTML编码，需要清理

### 6.3 数据清理

**HTML编码清理**:
- `&lt;` → `<`
- `&gt;` → `>`
- `u003c` → `<`（字面字符串）
- `u003e` → `>`（字面字符串）

**实现位置**: `app/services/hkex_service.py:32-68`

---

## 7. 注意事项

### 7.1 SSL/TLS配置

**问题**: 港交所API使用自签名证书

**解决方案**: 禁用SSL验证（仅用于开发/测试环境）

**实现代码**:
```python
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
```

**实现位置**: 
- `app/services/hkex_service.py:90-94`
- `app/services/hkex_service.py:165-169`
- `app/services/hkex_service.py:355-359`

### 7.2 日期格式

**输入格式**:
- 搜索接口：`YYYYMMDD`（如：`20250101`）

**响应格式**:
- 搜索接口：`dd/mm/yyyy HH:MM`（如：`08/10/2025 16:46`）
- 最新公告：`dd/mm/yyyy HH:MM`（如：`08/10/2025 16:46`）

**转换方法**:
```python
# 解析响应日期
date_object = datetime.strptime("08/10/2025", "%d/%m/%Y")
formatted_date = date_object.strftime("%Y-%m-%d")  # 2025-10-08
```

### 7.3 文件路径处理

**相对路径**: `/listedco/listconews/sehk/2025/1008/file.pdf`  
**完整URL**: `https://www1.hkexnews.hk/listedco/listconews/sehk/2025/1008/file.pdf`

**构建方法**:
```python
pdf_link = base_url + file_link
```

### 7.4 编码问题

**问题**: 响应数据可能包含多种编码格式

**处理策略**:
1. HTML实体编码（`&lt;`, `&gt;`）
2. Unicode字面字符串（`u003c`, `u003e`）
3. Unicode转义（`u2013`, `u0026`）
4. JSON字符串转义（`"[{`, `}]"`）

**实现位置**: `app/services/hkex_service.py:32-68, 181-187`

### 7.5 空结果处理

**搜索接口**: 返回`{"result": []}`或`{"result": "[]"}`  
**最新公告**: 返回`{"newsInfoLst": []}`

**处理逻辑**:
```python
if not result_data or 'result' not in result_data or not result_data['result']:
    return stock_id, []
```

### 7.6 分类代码处理

**问题**: 最新公告接口的`t1Code`和`t2Code`可能为`"NaN"`

**处理逻辑**:
```python
t1_code = item.get("t1Code") if item.get("t1Code") != "NaN" else None
t2_code = item.get("t2Code") if item.get("t2Code") != "NaN" else None
```

**实现位置**: `app/services/hkex_service.py:428-429`

### 7.7 多股票公告

**问题**: 最新公告接口中，一个公告可能关联多个股票

**处理逻辑**: 取第一个股票信息
```python
stock_info = item.get("stock", [{}])[0]
stock_code = stock_info.get("sc", "")
```

**实现位置**: `app/services/hkex_service.py:383-384`

---

## 8. API调用流程

### 8.1 搜索公告流程

```
1. 调用 /search/prefix.do 获取股票ID
   ↓
2. 使用股票ID调用 /search/titleSearchServlet.do 搜索公告
   ↓
3. 解析响应数据（清理HTML编码、转义字符）
   ↓
4. 提取公告信息并构建AnnouncementItem对象
```

### 8.2 获取最新公告流程

```
1. 调用 /ncms/json/eds/lcisehk1relsdc_1.json 获取最新公告
   ↓
2. 应用客户端过滤（市场、股票代码、分类代码）
   ↓
3. 解析日期时间、构建PDF链接
   ↓
4. 提取公告信息并构建AnnouncementItem对象
```

---

## 9. 错误处理

### 9.1 网络错误

**处理**: 捕获`httpx.HTTPError`，记录错误日志

### 9.2 解析错误

**处理**: 捕获`json.JSONDecodeError`，返回空结果或抛出异常

### 9.3 数据格式错误

**处理**: 跳过无效数据项，继续处理其他项

---

## 10. 性能考虑

### 10.1 请求超时

**默认超时**: 30秒

**配置位置**: `app/core/config.py:21`

### 10.2 并发控制

**建议**: 避免过于频繁的请求，可能触发限流

### 10.3 缓存策略

**分类数据**: 建议缓存，减少重复请求

**实现位置**: `app/services/category_service.py:20, 29-30`

---

## 11. 项目实现映射

| 港交所API端点 | 项目服务方法 | 文件位置 |
|--------------|-------------|----------|
| `/search/prefix.do` | `HKEXService.get_stock_id()` | `app/services/hkex_service.py:70-115` |
| `/search/titleSearchServlet.do` | `HKEXService.search_announcements()` | `app/services/hkex_service.py:117-275` |
| `/ncms/json/eds/lcisehk1relsdc_1.json` | `HKEXService.get_latest_announcements()` | `app/services/hkex_service.py:329-434` |
| `/ncms/script/eds/*.json` | `CategoryService.load_categories()` | `app/services/category_service.py:22-56` |

---

**文档版本**: v1.0.0  
**最后更新**: 2025-11-07  
**维护者**: HKEX项目组

