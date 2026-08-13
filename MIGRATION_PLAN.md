# MIGRATION_PLAN.md — tkinter → CustomTkinter 迁移任务规划

> **文档状态：历史迁移记录。** 当前主程序已经使用 CustomTkinter；本文保留的是迁移时的阶段计划与检查清单，不代表当前待办、版本号或最新构建命令。运行与打包请以 [README](README.md) 和 [快速开始](docs/quickstart.md) 为准。

## 迁移目标

将 `at24c02_pat_generator.py` 的 GUI 层从原生 tkinter 迁移到 CustomTkinter，实现现代化 UI 外观（圆角控件、内置暗色主题、平滑动画），同时保持所有功能完全不变。

## 核心原则

1. **逻辑层零改动** — I2CVectorGenerator、TestPatternGenerator、PATFormatter、所有 Engine/Simulator 类完全不动
2. **逐方法迁移** — 每次只迁移一个方法，迁移完立即测试
3. **Canvas 保持原生** — 波形图、Shmoo、Wafer Map、流程图等 Canvas 绑定代码不动（CTkCanvas 就是 tk.Canvas）
4. **功能冻结** — 迁移期间不加新功能，只改外观

## 新增依赖

仅增加一个依赖：
```bash
pip install customtkinter
```

打包命令变为：
```bash
pyinstaller --onefile --windowed --name AT24C02_PAT_Generator_v2.0 --hidden-import customtkinter at24c02_pat_generator.py
```

注意：PyInstaller 打包 CustomTkinter 时需要 `--hidden-import customtkinter`，否则运行时可能报 ModuleNotFoundError。如果仍有问题，追加：
```bash
--collect-data customtkinter
```

---

## 阶段0: 迁移前准备

### 0.1 创建备份
```bash
copy at24c02_pat_generator.py at24c02_pat_generator_tkonly_backup.py
```

### 0.2 修改导入头部

找到文件顶部的 import 区域，替换/新增：

```python
# 旧代码
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# 新代码
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext  # 保留这三个，CTk没有替代
import customtkinter as ctk

# 设置 CustomTkinter 全局配置
ctk.set_appearance_mode("dark")       # 强制暗色主题
ctk.set_default_color_theme("blue")   # 内置蓝色主题
```

注意：`filedialog`、`messagebox`、`scrolledtext` 没有 CustomTkinter 替代品，继续用 tkinter 原生的。

### 0.3 确认 ttk 使用范围

在迁移前搜索所有 `ttk.` 引用，列出需要替换的控件清单。常见映射：

| tkinter / ttk | CustomTkinter | 备注 |
|---------------|---------------|------|
| `tk.Tk()` | `ctk.CTk()` | 主窗口 |
| `tk.Toplevel()` | `ctk.CTkToplevel()` | 弹窗 |
| `tk.Frame()` | `ctk.CTkFrame()` | 框架 |
| `tk.Label()` | `ctk.CTkLabel()` | 标签 |
| `tk.Button()` | `ctk.CTkButton()` | 按钮 |
| `tk.Entry()` | `ctk.CTkEntry()` | 输入框 |
| `tk.Checkbutton()` / `ttk.Checkbutton` | `ctk.CTkCheckBox()` | 复选框 |
| `ttk.Combobox()` | `ctk.CTkComboBox()` | 下拉框 |
| `tk.Spinbox()` | `ctk.CTkEntry()` + 手动增减按钮 | CTk 无 Spinbox，需自定义 |
| `ttk.Notebook()` | `ctk.CTkTabview()` | Tab标签页 |
| `ttk.Progressbar()` | `ctk.CTkProgressBar()` | 进度条 |
| `ttk.Separator()` | `ctk.CTkFrame(height=1)` | 分割线 |
| `tk.Scale()` | `ctk.CTkSlider()` | 滑块 |
| `tk.Scrollbar()` | `ctk.CTkScrollbar()` | 滚动条，但通常用 CTkScrollableFrame 代替 |
| `tk.Canvas()` | `tk.Canvas()` | **不替换**，CTk 无 Canvas |
| `scrolledtext.ScrolledText()` | `ctk.CTkTextbox()` | 带滚动条的文本框 |
| `tk.Text()` | `ctk.CTkTextbox()` | 文本框 |
| `ttk.Style()` | 删除 | CTk 自带主题，不需要 ttk.Style |

### 0.4 处理不兼容的 API 差异

**关键差异清单（迁移时逐项检查）：**

#### a) 颜色参数名变化
```python
# tkinter
tk.Label(parent, text="hi", fg="white", bg="#1a1f2e")

# CustomTkinter
ctk.CTkLabel(parent, text="hi", text_color="white", fg_color="#1a1f2e")
```

| tkinter 参数 | CTk 参数 |
|-------------|---------|
| `fg` | `text_color` |
| `bg` | `fg_color`（控件背景）或 `bg_color`（透明时的父级底色） |
| `activebackground` | `hover_color` |
| `relief` | 删除（CTk 无 relief） |
| `bd` / `borderwidth` | `border_width` |
| `padx` / `pady`（构造函数里的） | 改用 `.pack(padx=..., pady=...)` 或 `CTkFrame(... )` 配合内部 padding |
| `font=("Segoe UI", 10, "bold")` | `font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold")` 或直接用 tuple |
| `cursor="hand2"` | `cursor="hand2"` (不变) |

#### b) pack/grid/place 不变
布局管理器完全一样，不需要改。

#### c) StringVar / IntVar / BooleanVar
```python
# tkinter
self.var = tk.StringVar(value="hello")
self.bool_var = tk.BooleanVar(value=True)
self.int_var = tk.IntVar(value=0)

# CustomTkinter — 同样用 tkinter 的变量，不变
self.var = tk.StringVar(value="hello")
self.bool_var = tk.BooleanVar(value=True)  # 但 CTkCheckBox 用 ctk.BooleanVar 更好
self.int_var = tk.IntVar(value=0)
```

CTkCheckBox 推荐用 `variable=ctk.StringVar(value="on")` + `onvalue="on"` + `offvalue="off"`，也可以继续用 `tk.BooleanVar`。

#### d) CTkTabview 与 ttk.Notebook 差异
```python
# ttk.Notebook
self.notebook = ttk.Notebook(parent)
tab1 = tk.Frame(self.notebook)
self.notebook.add(tab1, text="PAT向量")
self.notebook.pack(fill=tk.BOTH, expand=True)

# CTkTabview
self.tabview = ctk.CTkTabview(parent)
self.tabview.pack(fill="both", expand=True)
tab1 = self.tabview.add("PAT向量")  # 返回的就是 CTkFrame，直接往里放控件
```

关键区别：
- `ttk.Notebook.add(frame, text=...)` → `CTkTabview.add("标签名")` 返回 frame
- 不需要预先创建 Frame
- `self.notebook.select(0)` → `self.tabview.set("标签名")`
- 获取当前tab: `self.notebook.index("current")` → `self.tabview.get()`

#### e) ScrolledText → CTkTextbox
```python
# tkinter
self.text = scrolledtext.ScrolledText(parent, wrap=tk.NONE, font=("Consolas", 9))
self.text.insert("1.0", content)
self.text.delete("1.0", tk.END)
self.text.config(state=tk.DISABLED)

# CustomTkinter
self.text = ctk.CTkTextbox(parent, wrap="none", font=("Consolas", 13))
self.text.insert("0.0", content)    # 注意：CTkTextbox 用 "0.0" 不是 "1.0"
self.text.delete("0.0", "end")      # 用字符串 "end" 不是 tk.END
self.text.configure(state="disabled")
```

**重要**：CTkTextbox 的索引用 `"0.0"` 起始，不是 `"1.0"`。这是最常见的迁移 bug。全局搜索 `"1.0"` 和 `tk.END` 替换。

#### f) CTkCheckBox vs Checkbutton
```python
# tkinter
tk.Checkbutton(parent, text="开短路测试", variable=self.os_var,
               fg="white", bg="#2a3042", selectcolor="#1a1f2e")

# CustomTkinter
ctk.CTkCheckBox(parent, text="开短路测试", variable=self.os_var,
                text_color="white", fg_color="#4f8cff",
                hover_color="#3a7ae8", border_color="#353d52")
```

#### g) Spinbox 替代方案

CTk 没有 Spinbox。替代方案是用 CTkFrame + CTkButton + CTkEntry 手动实现：

```python
class CTkSpinbox(ctk.CTkFrame):
    """CustomTkinter 风格的 Spinbox 替代"""
    def __init__(self, master, from_=0, to=1, initial=0, width=60, command=None, **kwargs):
        super().__init__(master, fg_color="transparent")
        self._var = tk.IntVar(value=initial)
        self._from = from_
        self._to = to
        self._command = command

        self._entry = ctk.CTkEntry(self, width=width-40, textvariable=self._var,
                                    justify="center", font=("Consolas", 12))
        self._entry.pack(side="left", padx=(0, 2))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent", width=20)
        btn_frame.pack(side="left")

        self._up = ctk.CTkButton(btn_frame, text="▲", width=20, height=14,
                                  font=("Arial", 8), command=self._increment)
        self._up.pack()
        self._down = ctk.CTkButton(btn_frame, text="▼", width=20, height=14,
                                    font=("Arial", 8), command=self._decrement)
        self._down.pack()

    def _increment(self):
        val = self._var.get()
        if val < self._to:
            self._var.set(val + 1)
            if self._command: self._command()

    def _decrement(self):
        val = self._var.get()
        if val > self._from:
            self._var.set(val - 1)
            if self._command: self._command()

    def get(self):
        return self._var.get()

    def set(self, value):
        self._var.set(value)
```

将这个类放在文件顶部（常量定义之后、I2CVectorGenerator 之前），然后所有 `tk.Spinbox(...)` 替换为 `CTkSpinbox(...)`。

---

## 阶段1: 主窗口和顶层结构

### 1.1 替换主窗口

找到 `main()` 函数：

```python
# 旧
root = tk.Tk()

# 新
root = ctk.CTk()
```

### 1.2 删除 ttk.Style 配置

找到 `setup_styles()` 方法，**整个方法体清空或删除**。CTk 自带主题，不需要手动配置 Style。如果有其他地方调用 `self.setup_styles()`，改为 `pass` 或删除调用。

### 1.3 替换主窗口配置

```python
# 旧
self.root.configure(bg=self.colors["bg"])

# 新
# CTk 主窗口不需要手动设 bg，主题自动处理
# 如果想自定义颜色：
self.root.configure(fg_color=self.colors["bg"])
```

### 1.4 测试检查点 ✓

迁移完阶段1后：
- [ ] `python at24c02_pat_generator.py` 能启动
- [ ] 窗口出现，标题栏正常
- [ ] 窗口内部可能是空白或布局错乱（正常，因为子控件还没迁移）

---

## 阶段2: 顶部工具栏 (build_toolbar)

### 2.1 替换工具栏容器

```python
# 旧
toolbar = tk.Frame(self.root, bg=self.colors["bg"], ...)

# 新
toolbar = ctk.CTkFrame(self.root, fg_color=self.colors["sidebar"], corner_radius=0)
```

### 2.2 替换工具栏里的控件

按顺序替换：
- `tk.Label` → `ctk.CTkLabel`
- `tk.Button` → `ctk.CTkButton`
- `tk.Spinbox` → `CTkSpinbox`（用阶段0定义的自定义类）
- `ttk.Combobox` → `ctk.CTkComboBox`
- `tk.Checkbutton` → `ctk.CTkCheckBox`

### 2.3 生成/导出按钮突出显示

```python
gen_btn = ctk.CTkButton(
    toolbar, text="▶ 生成PAT",
    command=self.on_generate,
    font=ctk.CTkFont(size=13, weight="bold"),
    fg_color="#4f8cff",
    hover_color="#3a7ae8",
    corner_radius=8,
    height=32, width=120
)

export_btn = ctk.CTkButton(
    toolbar, text="💾 导出文件",
    command=self.on_export,
    font=ctk.CTkFont(size=13, weight="bold"),
    fg_color="#38d9a9",
    hover_color="#2bc299",
    text_color="#1a1f2e",
    corner_radius=8,
    height=32, width=120
)
```

### 2.4 测试检查点 ✓

- [ ] 工具栏显示正常，所有按钮可点击
- [ ] A2/A1/A0 Spinbox 能增减
- [ ] VCC Combobox 能下拉选择
- [ ] 生成/导出按钮颜色醒目

---

## 阶段3: 左侧配置面板 (build_config_panel)

### 3.1 替换面板容器

```python
# 旧
left_panel = tk.Frame(main_frame, bg=self.colors["sidebar"], width=320)

# 新
left_panel = ctk.CTkFrame(main_frame, fg_color=self.colors["sidebar"],
                           width=320, corner_radius=0)
```

如果左侧面板内容过多需要滚动：
```python
left_panel = ctk.CTkScrollableFrame(main_frame, fg_color=self.colors["sidebar"],
                                      width=320, corner_radius=0)
```

### 3.2 可折叠分组（如果尚未实现）

```python
class CollapsibleSection(ctk.CTkFrame):
    """可折叠的配置分组"""
    def __init__(self, master, title, expanded=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._expanded = expanded
        self._title = title

        # 标题栏（可点击）
        self.header = ctk.CTkButton(
            self, text=f"{'▼' if expanded else '▶'}  {title}",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("gray75", "gray25"),  # (light_mode, dark_mode)
            hover_color=("gray65", "gray35"),
            text_color=("gray10", "gray90"),
            anchor="w", corner_radius=6, height=30,
            command=self._toggle
        )
        self.header.pack(fill="x", padx=4, pady=(4, 0))

        # 内容区
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        if expanded:
            self.content.pack(fill="x", padx=8, pady=(4, 8))

    def _toggle(self):
        if self._expanded:
            self.content.pack_forget()
            self.header.configure(text=f"▶  {self._title}")
        else:
            self.content.pack(fill="x", padx=8, pady=(4, 8))
            self.header.configure(text=f"▼  {self._title}")
        self._expanded = not self._expanded
```

使用方式：
```python
section = CollapsibleSection(left_panel, "芯片配置", expanded=True)
section.pack(fill="x", padx=4, pady=2)

# 往 section.content 里放控件
ctk.CTkLabel(section.content, text="器件地址引脚:").pack(anchor="w")
# ...
```

### 3.3 复选框列表（测试类型选择）

```python
section_test = CollapsibleSection(left_panel, "测试类型选择", expanded=True)
section_test.pack(fill="x", padx=4, pady=2)

for key, label, desc in test_options:
    var = tk.BooleanVar(value=True)
    self.test_vars[key] = var

    item = ctk.CTkFrame(section_test.content, fg_color=self.colors["card"],
                         corner_radius=8)
    item.pack(fill="x", pady=2)

    ctk.CTkCheckBox(
        item, text=label, variable=var,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color="#4f8cff", hover_color="#3a7ae8",
        border_color="#353d52", corner_radius=4
    ).pack(anchor="w", padx=8, pady=(6, 0))

    ctk.CTkLabel(
        item, text=desc,
        font=ctk.CTkFont(size=11),
        text_color=self.colors["text_dim"],
        justify="left"
    ).pack(anchor="w", padx=(32, 8), pady=(0, 6))
```

### 3.4 芯片引脚图

引脚图用的是 Canvas，**不需要迁移**。Canvas 在 CustomTkinter 环境下正常工作：
```python
# Canvas 保持原样
self.pinout_canvas = tk.Canvas(section.content, width=280, height=180,
                                bg=self.colors["card"], highlightthickness=0)
```

### 3.5 测试检查点 ✓

- [ ] 左侧面板所有分组可折叠/展开
- [ ] 10个测试类型复选框可勾选/取消
- [ ] 芯片引脚图正常显示
- [ ] 自定义参数输入框可编辑
- [ ] 配置保存/加载按钮正常工作

---

## 阶段4: 右侧预览面板 (build_preview_panel)

### 4.1 替换 ttk.Notebook → CTkTabview

这是最大的单点改动。

```python
# 旧
self.notebook = ttk.Notebook(parent)
pat_frame = tk.Frame(self.notebook)
self.notebook.add(pat_frame, text="PAT向量")
txt_frame = tk.Frame(self.notebook)
self.notebook.add(txt_frame, text="TXT预览")
# ... 16个tab
self.notebook.pack(fill=tk.BOTH, expand=True)

# 新
self.tabview = ctk.CTkTabview(parent, corner_radius=8,
                                fg_color=self.colors["card"],
                                segmented_button_fg_color=self.colors["sidebar"],
                                segmented_button_selected_color="#4f8cff",
                                segmented_button_unselected_color=self.colors["card"])
self.tabview.pack(fill="both", expand=True, padx=4, pady=4)

pat_frame = self.tabview.add("PAT")        # 缩短标签名
txt_frame = self.tabview.add("TXT")
wave_frame = self.tabview.add("波形")
info_frame = self.tabview.add("说明")
flow_frame = self.tabview.add("流程")
stat_frame = self.tabview.add("统计")
shmoo_frame = self.tabview.add("Shmoo")
# ... 其余 tab
```

### 4.2 修改所有 notebook 引用

全局搜索替换：

| 旧代码 | 新代码 |
|--------|--------|
| `self.notebook.select(0)` | `self.tabview.set("PAT")` |
| `self.notebook.select(N)` | `self.tabview.set("对应标签名")` |
| `self.notebook.index("current")` | `self.tabview.get()` |
| `self.notebook.add(frame, text="xxx")` | 不需要，add() 在创建时已完成 |

### 4.3 替换 ScrolledText → CTkTextbox

```python
# 旧
self.pat_text = scrolledtext.ScrolledText(pat_frame, wrap=tk.NONE,
    font=("Consolas", 9), bg="#2a3042", fg="#e8ecf1")
self.pat_text.pack(fill=tk.BOTH, expand=True)

# 新
self.pat_text = ctk.CTkTextbox(pat_frame, wrap="none",
    font=("Consolas", 13), fg_color="#2a3042", text_color="#e8ecf1",
    corner_radius=8)
self.pat_text.pack(fill="both", expand=True, padx=4, pady=4)
```

**全局替换索引** — 在所有 `.insert()` / `.delete()` / `.get()` 调用中：
- `"1.0"` → `"0.0"`
- `tk.END` → `"end"`

用正则搜索确认：搜索 `\.insert\(["']1\.0` 和 `\.delete\(["']1\.0` 和 `tk\.END`。

### 4.4 波形图 / Shmoo / Wafer Map / 流程图等 Canvas

**全部保持不变。** Canvas 不需要迁移。只需要确保 Canvas 的父容器从 `tk.Frame` 改成了 `ctk.CTkFrame` 或 `self.tabview.add()` 返回的 frame。

### 4.5 测试检查点 ✓

- [ ] 所有16个Tab标签显示正常
- [ ] Tab切换正常
- [ ] PAT/TXT 文本框内容显示正常
- [ ] 波形图Canvas绘制正常
- [ ] Shmoo/Wafer Map Canvas正常
- [ ] 文本框可以滚动
- [ ] Ctrl+F搜索功能正常（如果绑定在Text widget上）

---

## 阶段5: 弹窗和对话框

### 5.1 Toplevel 弹窗

```python
# 旧
dialog = tk.Toplevel(self.root)
dialog.title("时序检查结果")
dialog.geometry("500x400")

# 新
dialog = ctk.CTkToplevel(self.root)
dialog.title("时序检查结果")
dialog.geometry("500x400")
```

### 5.2 messagebox 不变

`messagebox.showinfo()` / `messagebox.showerror()` / `messagebox.showwarning()` 保持原样，这些是 OS 原生弹窗。

### 5.3 filedialog 不变

`filedialog.askdirectory()` / `filedialog.askopenfilename()` / `filedialog.asksaveasfilename()` 保持原样。

### 5.4 测试检查点 ✓

- [ ] 时序检查弹窗正常弹出
- [ ] 协议检查弹窗正常
- [ ] 文件导出对话框正常
- [ ] 配置加载对话框正常

---

## 阶段6: 主题和配色系统

### 6.1 统一配色

删除手动的 `self.colors` 字典中与 CTk 主题重复的颜色。保留自定义色用于 Canvas 和特殊控件。

CustomTkinter 的颜色可以用 tuple 指定 (light_mode_color, dark_mode_color)：
```python
ctk.CTkButton(parent, fg_color=("#3B8ED0", "#4f8cff"))  # 自动跟随主题
```

由于你的工具主要用暗色主题，可以简化为只指定暗色值。

### 6.2 主题切换（如果已实现）

```python
def _toggle_theme(self):
    current = ctk.get_appearance_mode()
    if current == "Dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")
    # CTk 会自动刷新所有控件，不需要手动重建UI
```

这比原来的 tkinter 实现简单得多——原来可能需要销毁重建整个UI，CTk自动处理。

### 6.3 测试检查点 ✓

- [ ] 暗色模式下所有控件颜色协调
- [ ] 如果有浅色模式切换，切换后不崩溃
- [ ] Canvas 里的颜色在主题切换后是否需要手动更新（通常需要）

---

## 阶段7: 高DPI和最终打磨

### 7.1 高DPI

CustomTkinter 自动处理高DPI（内部调用了 `ctypes.windll.shcore.SetProcessDpiAwareness`），不需要手动添加。但确认一下主窗口创建前没有其他地方设置了冲突的 DPI 设置。

### 7.2 字体统一

```python
# 定义全局字体常量
FONT_TITLE = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
FONT_HEADING = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
FONT_BODY = ctk.CTkFont(family="Segoe UI", size=12)
FONT_SMALL = ctk.CTkFont(family="Segoe UI", size=11)
FONT_MONO = ctk.CTkFont(family="Consolas", size=13)
FONT_MONO_SMALL = ctk.CTkFont(family="Consolas", size=11)
```

注意：`ctk.CTkFont()` 必须在 CTk() 主窗口创建之后才能调用。所以这些常量要放在 `PatGeneratorApp.__init__()` 里初始化，不能放在模块顶层。

### 7.3 控件间距规范

| 位置 | 间距 |
|------|------|
| 分组之间 | `pady=8` |
| 控件之间（同组） | `pady=3` |
| 控件内部 padding | `padx=8, pady=6` |
| 面板边距 | `padx=8, pady=8` |
| Tab内边距 | `padx=4, pady=4` |

### 7.4 PyInstaller 打包测试

```bash
pip install customtkinter pyinstaller
pyinstaller --onefile --windowed --name AT24C02_PAT_Generator_v2.0 --hidden-import customtkinter --collect-data customtkinter at24c02_pat_generator.py
```

打包后测试：
- [ ] 双击 .exe 正常启动
- [ ] 所有Tab页正常
- [ ] 生成按钮正常
- [ ] 导出文件正常
- [ ] 弹窗正常

### 7.5 测试检查点 ✓ (最终)

- [ ] exe 在 Windows 10 上正常运行
- [ ] exe 在 Windows 11 上正常运行
- [ ] 全量10段测试生成不崩溃
- [ ] 导出所有文件类型（.pat/.txt/.prg/.tim/.lvl/.html/.json）正常
- [ ] 波形图/Shmoo/WaferMap/流程图 Canvas 正常绘制
- [ ] 主题切换不崩溃
- [ ] 语言切换不崩溃
- [ ] 配置保存/加载正常

---

## 常见迁移 Bug 速查

| 症状 | 原因 | 修复 |
|------|------|------|
| `TclError: bad screen distance` | pady/padx tuple 放在了构造函数里 | 移到 .pack()/.grid() |
| `AttributeError: 'CTkFrame' has no attribute 'configure'` → bg | CTk 用 `fg_color` 不是 `bg` | 替换参数名 |
| 文本框内容显示不出来 | insert 用了 `"1.0"` | 改为 `"0.0"` |
| Tab切换报错 | 用了 `self.notebook.select(0)` | 改为 `self.tabview.set("标签名")` |
| exe启动后白屏崩溃 | PyInstaller 缺少 customtkinter 数据文件 | 加 `--collect-data customtkinter` |
| CheckBox 取值不对 | CTkCheckBox 默认用 "on"/"off" 字符串 | 设置 `onvalue=True, offvalue=False` 或用 BooleanVar |
| CTkTextbox 没有 tag_config | CTkTextbox 不支持 tkinter Text 的 tag 系统 | 语法高亮需要用 CTkTextbox 的有限 API 或保持 tk.Text |

### 关于语法高亮的特殊处理

CTkTextbox 底层是 tk.Text 的封装，部分支持 tag 操作。如果你的 PAT 预览有语法高亮（用 `tag_add` / `tag_config`），试一下能否直接在 CTkTextbox 上用：

```python
# 尝试访问内部 Text widget
self.pat_text._textbox.tag_config("keyword", foreground="#4f8cff")
self.pat_text._textbox.tag_add("keyword", "1.0", "1.5")
```

如果 `_textbox` 不可用或版本不同，回退到直接用 `tk.Text` 并手动包一个 CTkFrame + CTkScrollbar。

---

## 迁移顺序总结

```
阶段0: 准备（备份+导入+API映射表）         → 0.5天
阶段1: 主窗口 CTk()                        → 0.5天 → 测试
阶段2: 顶部工具栏                          → 1天   → 测试
阶段3: 左侧配置面板                        → 2天   → 测试
阶段4: 右侧预览面板（最大改动）            → 3天   → 测试
阶段5: 弹窗和对话框                        → 0.5天 → 测试
阶段6: 主题和配色                          → 1天   → 测试
阶段7: 高DPI + 最终打包测试                → 1天   → 测试
                                            ─────────
                                     合计约 ~10天 (Claude Code 实际执行)
```

每个阶段完成后，务必运行一次 `python at24c02_pat_generator.py` 确认不崩溃，再进入下一阶段。
