# PR #333 測試指南

## 功能概述

此 PR 添加了兩個主要功能：
1. **`--show-thinking` 標誌**：顯示 Agent 的推理過程
2. **`Ctrl+O` 切換工具輸出**：動態控制工具調用輸出的可見性

---

## 測試環境準備

### 1. 確認當前分支
```bash
cd /Users/ericp/PycharmProjects/deepagents-hk
git status
# 應該顯示: On branch feature/show-thinking-and-tool-outputs
```

### 2. 確保依賴已安裝
```bash
source .venv/bin/activate
uv sync
```

---

## 測試場景

### 場景 1：測試 `--show-thinking` 標誌

#### 1.1 不帶 `--show-thinking` 啟動（默認行為）
```bash
hkex
```

**預期行為**：
- 啟動正常
- Agent 回應時**不顯示**推理過程（reasoning blocks）
- 只看到最終回答

**測試步驟**：
1. 輸入簡單問題：`你是誰？`
2. 觀察輸出，應該只看到回答，不會顯示推理過程

---

#### 1.2 帶 `--show-thinking` 啟動
```bash
hkex --show-thinking
```

**預期行為**：
- 啟動正常
- Agent 回應時**顯示**推理過程（以 dim 樣式顯示）
- 可以看到 Agent 如何思考和分析問題

**測試步驟**：
1. 輸入問題：`分析一下 00700 騰訊最近的公告`
2. 觀察輸出，應該看到：
   - 推理過程（灰色/暗淡顯示）
   - 工具調用（如果工具輸出未啟用，則不顯示詳細內容）
   - 最終回答

---

### 場景 2：測試 `Ctrl+O` 工具輸出切換

#### 2.1 啟動 CLI 並檢查初始狀態
```bash
hkex
```

**預期行為**：
- 底部工具欄顯示：`tool outputs off (CTRL+O to toggle)` （灰色背景）
- 默認情況下，工具輸出是**關閉**的

---

#### 2.2 開啟工具輸出
**測試步驟**：
1. 在提示符下按 `Ctrl+O`
2. 觀察工具欄變化

**預期行為**：
- 工具欄變為：`tool outputs ON (CTRL+O to toggle)` （青色背景）
- 狀態成功切換

---

#### 2.3 測試工具輸出顯示（ON 狀態）
**測試步驟**：
1. 確保工具輸出已開啟（工具欄顯示 "tool outputs ON"）
2. 輸入需要調用工具的問題：`查詢 00700 最近的公告`

**預期行為**：
- 看到工具調用的詳細輸出
- 輸出格式：` ↳ <工具返回內容>` （淡青色 dim cyan 樣式）
- 每次工具調用後有空行分隔

**示例輸出**：
```
● Agent is thinking...
 ↳ Searching HKEX announcements for stock 00700...
 ↳ Found 5 announcements in date range...

根據查詢結果，00700 最近有以下公告：
...
```

---

#### 2.4 測試工具輸出顯示（OFF 狀態）
**測試步驟**：
1. 按 `Ctrl+O` 關閉工具輸出
2. 確認工具欄顯示 "tool outputs off"
3. 輸入相同問題：`查詢 00700 最近的公告`

**預期行為**：
- **不顯示**工具調用的詳細輸出
- 只看到最終回答
- 體驗更簡潔

---

#### 2.5 測試運行時切換
**測試步驟**：
1. 提問：`查詢 00700 和 03800 的公告`（會觸發多次工具調用）
2. 在 Agent 處理過程中，嘗試多次按 `Ctrl+O` 切換

**預期行為**：
- 每次按 `Ctrl+O`，工具欄立即更新
- 後續的工具調用會根據當前狀態顯示/隱藏輸出
- 切換不會打斷 Agent 的工作流程

---

### 場景 3：組合測試 `--show-thinking` + `Ctrl+O`

#### 3.1 同時啟用兩個功能
```bash
hkex --show-thinking
# 啟動後按 Ctrl+O 開啟工具輸出
```

**測試步驟**：
1. 確認工具欄顯示 "tool outputs ON"
2. 輸入複雜問題：`分析 00328 的供股情況並生成報告`

**預期行為**：
- 顯示推理過程（reasoning blocks，dim 樣式）
- 顯示工具輸出（` ↳ ...`，dim cyan 樣式）
- 看到完整的 Agent 思考和執行過程

**示例輸出**：
```
● [推理過程] 
  我需要先查詢 00328 的供股相關公告，然後分析內容...

 ↳ Searching for rights issue announcements for stock 00328...
 ↳ Found announcement: 2025-10-13-建議按於記錄日期...

[推理過程]
  分析表明這是一個 1:4 的供股...

最終分析報告：
...
```

---

### 場景 4：檢查幫助文檔

#### 4.1 測試交互式幫助
```bash
hkex
# 啟動後輸入
/help
```

**預期行為**：
- 在 "Editing Features" 部分看到：
  - `Ctrl+T          Toggle auto-approve mode`
  - `Ctrl+O          Toggle tool output visibility` ← **新增**

---

#### 4.2 測試命令行幫助
```bash
hkex help
```

**預期行為**：
1. "Usage" 部分顯示：
   ```
   hkex [--agent NAME] [--auto-approve] [--show-thinking]     Start interactive session
   ```

2. "Examples" 部分包含：
   ```
   hkex --show-thinking              # Show agent's reasoning process
   ```

3. "Interactive Features" 部分包含：
   ```
   Ctrl+O          Toggle tool output visibility
   ```

---

#### 4.3 測試啟動提示
```bash
hkex
```

**預期行為**：
- 啟動時的 "Tips" 行顯示：
  ```
  Tips: Enter to submit, Alt+Enter for newline, Ctrl+E for editor, 
        Ctrl+T to toggle auto-approve, Ctrl+O to toggle tool outputs, 
        Ctrl+C to interrupt
  ```

---

## 視覺驗證檢查清單

### 工具欄狀態
- [ ] 默認顯示 "tool outputs off (CTRL+O to toggle)" 灰色背景
- [ ] 切換後顯示 "tool outputs ON (CTRL+O to toggle)" 青色背景
- [ ] 切換時 UI 立即響應，無延遲

### 輸出樣式
- [ ] 推理過程以 dim 樣式顯示（較暗）
- [ ] 工具輸出使用 `↳` 符號 + dim cyan 樣式
- [ ] 每個工具輸出後有空行分隔
- [ ] 最終回答正常顯示（非 dim）

### 快捷鍵響應
- [ ] `Ctrl+O` 立即切換狀態
- [ ] `Ctrl+T` 仍然正常切換 auto-approve
- [ ] 其他快捷鍵（Ctrl+E, Ctrl+C）不受影響

---

## 邊界情況測試

### 1. 無工具調用的問題
```bash
hkex --show-thinking
# 開啟工具輸出後問
你好
```
**預期**：只看到推理過程，沒有工具輸出（因為沒調用工具）

---

### 2. 大量工具調用
```bash
hkex
# 開啟工具輸出
查詢最近一個月所有股票的供股公告
```
**預期**：
- 多個工具調用輸出按順序顯示
- 性能正常，無卡頓
- 可以隨時用 `Ctrl+O` 關閉輸出

---

### 3. 錯誤處理
```bash
hkex --show-thinking
# 問一個會導致錯誤的問題
查詢一個不存在的股票代碼 99999
```
**預期**：
- 錯誤信息正常顯示
- 推理過程（如果有）顯示
- 不會崩潰

---

## 回歸測試

### 確保現有功能未受影響
- [ ] `/help` 命令正常工作
- [ ] `/clear` 清除歷史正常
- [ ] `/tokens` 顯示 token 使用
- [ ] `Ctrl+T` 切換 auto-approve 正常
- [ ] `@` 文件補全正常
- [ ] PDF 下載和分析功能正常
- [ ] 彩虹橫幅顯示正常

---

## 性能測試

### 1. 啟動時間
```bash
time hkex --show-thinking
```
**預期**：啟動時間與之前一致，無明顯延遲

### 2. 響應時間
- [ ] `Ctrl+O` 切換響應時間 < 100ms
- [ ] 工具輸出顯示不影響整體性能
- [ ] 大量輸出時終端渲染流暢

---

## 已知限制

1. **推理過程內容**：依賴於模型是否返回 reasoning blocks，某些模型可能不支持
2. **工具輸出格式**：所有工具使用統一的 ` ↳ ` 格式
3. **樣式衝突**：在某些終端主題下，dim 樣式可能不明顯

---

## 測試完成後

### 成功標準
- [ ] 所有場景測試通過
- [ ] 視覺驗證檢查清單全部完成
- [ ] 無崩潰或錯誤
- [ ] 回歸測試通過

### 如發現問題
請記錄：
1. 測試場景編號
2. 實際行為 vs 預期行為
3. 錯誤信息（如有）
4. 終端輸出截圖（如有）

---

## 快速測試腳本

如需快速驗證核心功能，可運行：

```bash
# 測試 1: 默認行為
hkex
# 輸入：你是誰？
# 檢查：無推理過程，無工具輸出
# 按 Ctrl+C 退出

# 測試 2: show-thinking
hkex --show-thinking
# 輸入：你是誰？
# 檢查：顯示推理過程
# 按 Ctrl+C 退出

# 測試 3: 工具輸出切換
hkex
# 按 Ctrl+O（檢查工具欄變化）
# 輸入：查詢 00700 公告
# 檢查：顯示工具輸出（帶 ↳ 符號）
# 按 Ctrl+O 再次切換
# 輸入：查詢 00700 公告
# 檢查：不顯示工具輸出
# 按 Ctrl+C 退出
```

---

## 提交前最後檢查

```bash
# 1. 確認所有修改文件
git status

# 2. 檢查 linter
ruff check src/cli/

# 3. 運行現有測試
pytest

# 4. 生成 diff 確認
git diff src/cli/config.py
git diff src/cli/execution.py
git diff src/cli/input.py
git diff src/cli/main.py
git diff src/cli/ui.py
```

完成測試後，請反饋：
- ✅ 所有測試通過
- ⚠️ 部分問題（附詳細說明）
- ❌ 重大問題（需修復）

