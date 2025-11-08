# ASCII艺术字生成说明

## 📚 Python库推荐

### 1. **pyfiglet** (已集成)
最流行的ASCII艺术字生成库，支持400+种字体。

```python
import pyfiglet

# 基本使用
banner = pyfiglet.figlet_format("HKEX Agent")
print(banner)

# 指定字体
banner = pyfiglet.figlet_format("HKEX Agent", font="slant")
print(banner)
```

### 2. **art** (备选方案)
另一个强大的ASCII艺术库，支持emoji和装饰。

```bash
uv add art
```

```python
from art import text2art

# 基本使用
banner = text2art("HKEX Agent")
print(banner)
```

---

## 🎨 已集成到项目

### 实现位置
`src/cli/config.py` - `get_hkex_banner()` 函数

### 核心代码

```python
def get_hkex_banner(font: str = "slant") -> str:
    """动态生成HKEX Agent横幅"""
    font = os.getenv("HKEX_ASCII_FONT", font)
    try:
        import pyfiglet
        return pyfiglet.figlet_format("HKEX Agent", font=font)
    except ImportError:
        return "🏢 HKEX Agent | 港交所公告分析助手\n"
```

### 配置方法

#### 方式1：通过环境变量
```bash
# .env 文件
HKEX_ASCII_FONT=slant    # 默认，倾斜风格
```

#### 方式2：修改代码
```python
# src/cli/config.py
HKEX_AGENT_ASCII = get_hkex_banner(font="banner")
```

---

## 🌟 推荐字体样式

### 紧凑简洁类
```bash
slant          # 默认，倾斜风格，视觉平衡
banner         # 经典横幅，粗体
standard       # 标准风格，易读性高
```

### 数字科技类
```bash
digital        # 数字风格，现代感
colossal       # 巨型字体，震撼
cybermedium    # 赛博风格
```

### 艺术装饰类
```bash
graffiti       # 涂鸦风格
3-d            # 3D立体效果
shadow         # 阴影效果
```

### 实际效果对比

#### slant (默认)
```
    __  _____  ________  __   ___                    __ 
   / / / / / |/ / ____/ |  | / /   /\   ____ ____  / /___
  / /_/ /|   / __/     | | / /   / /  / __ `/ _ \/ __/ /
 / __  //   / /___     | |/ /   / /  / /_/ /  __/ /_  / 
/_/ /_//_/|_/_____/     |___/   /_/   \__, /\___/\__/_/  
                                     /____/              
```

#### banner
```
##     ## ##    ## ######## ##     ##    ###     ######   ######## ##    ## ########
##     ## ##   ##  ##        ##   ##    ## ##   ##    ##  ##       ###   ##    ##
##     ## ##  ##   ##         ## ##    ##   ##  ##        ##       ####  ##    ##
######### #####    ######      ###    ##     ## ##   #### ######   ## ## ##    ##
##     ## ##  ##   ##         ## ##   ######### ##    ##  ##       ##  ####    ##
##     ## ##   ##  ##        ##   ##  ##     ## ##    ##  ##       ##   ###    ##
##     ## ##    ## ######## ##     ## ##     ##  ######   ######## ##    ##    ##
```

#### digital
```
+-+-+-+-+ +-+-+-+-+-+
|H|K|E|X| |A|g|e|n|t|
+-+-+-+-+ +-+-+-+-+-+
```

---

## 🛠️ 高级使用

### 查看所有可用字体
```python
import pyfiglet

# 列出所有字体
fonts = pyfiglet.FigletFont.getFonts()
print(f"共 {len(fonts)} 种字体")
print(sorted(fonts))
```

### 预览多种字体
```python
for font in ["slant", "banner", "digital", "standard"]:
    print(f"\n=== {font} ===")
    print(pyfiglet.figlet_format("HKEX", font=font))
```

### 字符宽度控制
```python
# 设置最大宽度
banner = pyfiglet.figlet_format("HKEX Agent", font="slant", width=80)
```

---

## 💡 为什么使用动态生成？

### 优势
1. **灵活性**：通过环境变量轻松切换风格
2. **可维护性**：无需手动管理复杂的多行字符串
3. **降级支持**：库未安装时自动回退到emoji版本
4. **个性化**：不同环境可展示不同风格

### 对比

#### 之前（硬编码）
- 占用 15 行代码
- 无法修改样式
- 需要手动对齐

#### 现在（动态生成）
- 1 行配置即可
- 支持 400+ 种字体
- 自动格式化

---

## 📦 依赖安装

```bash
# 已自动添加到项目依赖
uv add pyfiglet

# 或使用 pip
pip install pyfiglet
```

---

## 🧪 测试验证

```bash
# 启动应用，查看横幅效果
cd /Users/ericp/PycharmProjects/deepagents-hk
uv run python -m src.cli
```

### 切换字体测试

```bash
# 测试 banner 风格
export HKEX_ASCII_FONT=banner
uv run python -m src.cli

# 测试 digital 风格
export HKEX_ASCII_FONT=digital
uv run python -m src.cli

# 测试 3-d 风格
export HKEX_ASCII_FONT=3-d
uv run python -m src.cli
```

---

## 📋 总结

| 特性 | 说明 |
|------|------|
| **库名** | `pyfiglet` (已集成) |
| **默认字体** | `slant` |
| **配置方式** | 环境变量 `HKEX_ASCII_FONT` |
| **可用字体** | 400+ 种 |
| **降级策略** | 自动回退到 emoji 横幅 |
| **依赖大小** | ~1.7MB |

---

## 🔗 相关资源

- [pyfiglet GitHub](https://github.com/pwaller/pyfiglet)
- [在线字体预览](http://www.figlet.org/examples.html)
- [art库文档](https://github.com/sepandhaghighi/art)

