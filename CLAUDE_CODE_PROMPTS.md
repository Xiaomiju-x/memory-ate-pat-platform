# Claude Code 迁移指令手册

> **文档状态：历史开发记录。** 当前迁移已经落地；以下提示词用于解释当时的执行过程，不是当前贡献流程，也不应直接当作最新构建命令。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [快速开始](docs/quickstart.md)。

> 使用方法：每个阶段分两步
> 1. 先用 Plan mode 发送 【Plan指令】，让 Claude Code 理解任务并输出计划
> 2. 确认计划合理后，发送 【Execute指令】让它动手改代码
> 3. 改完后运行测试命令，确认不崩溃再进下一阶段

---

## 阶段0: 迁移前准备

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段0: 迁移前准备」部分。

我要把这个项目的 GUI 从 tkinter 迁移到 CustomTkinter。现在先做准备工作：

1. 把 at24c02_pat_generator.py 备份为 at24c02_pat_generator_tkonly_backup.py
2. 分析当前文件里所有 tkinter/ttk 控件的使用情况，列出需要替换的清单
3. 统计有多少处 tk.Frame / tk.Label / tk.Button / tk.Entry / ttk.Notebook / ttk.Combobox / tk.Checkbutton / scrolledtext.ScrolledText / tk.Spinbox / tk.Scale / ttk.Separator / ttk.Progressbar / tk.Toplevel / tk.Text
4. 统计所有 .insert("1.0" 和 tk.END 的使用位置（这些后面要改索引）

只做分析，不改代码。给我一份替换清单和工作量评估。
```

### 【Execute指令】

```
执行准备工作：

1. 复制 at24c02_pat_generator.py → at24c02_pat_generator_tkonly_backup.py
2. 在 at24c02_pat_generator.py 顶部修改 import：
   - 保留 from tkinter import filedialog, messagebox, scrolledtext
   - 新增 import customtkinter as ctk
   - 新增 ctk.set_appearance_mode("dark") 和 ctk.set_default_color_theme("blue")
3. 在常量区（I2CVectorGenerator类之前）添加 MIGRATION_PLAN.md 里定义的 CTkSpinbox 类
4. 不改其他任何代码

改完后运行 python -c "import at24c02_pat_generator" 确认导入不报错。
```

### 【测试命令】
```bash
pip install customtkinter
python -c "import at24c02_pat_generator; print('Import OK')"
```

---

## 阶段1: 主窗口和顶层结构

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段1: 主窗口和顶层结构」。

现在要做三件事：
1. main() 函数里把 tk.Tk() 改成 ctk.CTk()
2. 找到 setup_styles() 方法（如果存在），清空方法体改为 pass
3. 找到所有 self.root.configure(bg=...) 调用，改为 self.root.configure(fg_color=...)

列出你找到的所有需要修改的位置，告诉我具体行号和改动内容。
```

### 【Execute指令】

```
执行阶段1的修改：

1. main() 里 tk.Tk() → ctk.CTk()
2. setup_styles() 方法体清空为 pass（保留方法定义避免其他地方调用报错）
3. self.root.configure(bg=...) → self.root.configure(fg_color=...)
4. 如果有 ctypes.windll.shcore.SetProcessDpiAwareness 调用，删除它（CTk自动处理高DPI）

只改这些，不碰其他代码。改完后告诉我改了哪几行。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 预期：窗口能弹出，内部可能布局异常但不崩溃。关闭窗口后无报错。

---

## 阶段2: 顶部工具栏

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段2: 顶部工具栏」和「阶段0」里的 API 映射表。

找到 build_toolbar() 方法，分析里面用到的所有 tkinter 控件，列出每个控件当前的代码和替换后的代码。

注意事项：
- tk.Frame → ctk.CTkFrame（参数 bg → fg_color，删除 relief/bd）
- tk.Label → ctk.CTkLabel（参数 fg → text_color，bg → fg_color）
- tk.Button → ctk.CTkButton（参数 bg → fg_color，fg → text_color，activebackground → hover_color，删除 relief/cursor 保留）
- tk.Spinbox → CTkSpinbox（用我们在阶段0定义的自定义类）
- ttk.Combobox → ctk.CTkComboBox
- tk.Checkbutton → ctk.CTkCheckBox（selectcolor 删除，加 fg_color/hover_color/border_color）
- 所有 font=("Segoe UI", 10, "bold") 可保持tuple格式或改为 ctk.CTkFont

列出完整的替换对照表，不要改代码。
```

### 【Execute指令】

```
执行 build_toolbar() 方法的 CustomTkinter 迁移。

按照你刚才列出的替换对照表逐个替换。额外注意：
- 生成按钮和导出按钮要用醒目颜色：生成=#4f8cff，导出=#38d9a9
- 删除所有 relief=tk.FLAT / relief=tk.RAISED 参数
- 删除所有 bd=0 / borderwidth=0 参数（CTk控件默认无边框）
- 如果有 ttk.Separator，替换为 ctk.CTkFrame(parent, height=1, fg_color="#353d52")
- 确保 pack/grid 调用不变

改完后告诉我改了多少个控件。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 预期：工具栏显示现代化控件，按钮可点击，Spinbox/Combobox可操作。

---

## 阶段3: 左侧配置面板

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段3: 左侧配置面板」。

找到 build_config_panel() 方法，分析所有控件。这个方法比较大，包含：
- 芯片配置区（地址引脚、WP、器件地址显示）
- 测试类型选择区（10个复选框+描述文字）
- 自定义参数区（Entry输入框）
- 其他配置区（地址范围、周期、前缀等）
- 操作按钮（生成、导出、检查等）

分析以下问题：
1. 左侧面板是否已经有可折叠分组？如果有，列出现有实现方式
2. 如果面板内容超出窗口高度，是否需要改为 CTkScrollableFrame？
3. 芯片引脚图的 Canvas 有哪些，位置在哪里（这些不需要改）
4. 有多少个 tk.Checkbutton 需要替换

列出所有需要替换的控件和它们的行号范围。
```

### 【Execute指令】

```
执行 build_config_panel() 方法的 CustomTkinter 迁移。

分批进行，按面板区域从上到下：

第一批：替换面板容器
- 最外层 tk.Frame → ctk.CTkFrame 或 ctk.CTkScrollableFrame
- 所有内部分区的 tk.Frame → ctk.CTkFrame

第二批：替换芯片配置区控件
- tk.Label → ctk.CTkLabel
- tk.Spinbox → CTkSpinbox
- tk.Checkbutton → ctk.CTkCheckBox
- tk.Entry → ctk.CTkEntry

第三批：替换测试类型选择区
- 10个测试复选框 tk.Checkbutton → ctk.CTkCheckBox
- 描述文字 tk.Label → ctk.CTkLabel
- 卡片容器 tk.Frame → ctk.CTkFrame（加 corner_radius=8）

第四批：替换自定义参数区和操作按钮
- tk.Entry → ctk.CTkEntry
- tk.Button → ctk.CTkButton
- tk.Label → ctk.CTkLabel

重要：
- Canvas（芯片引脚图）不要动
- 所有 .pack()/.grid() 调用保持不变
- pady/padx tuple 只出现在 .pack()/.grid() 中
- 如果现有代码有可折叠面板的实现，保留它并替换内部控件

每批改完告诉我进度。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 预期：左侧面板所有控件现代化，可折叠分组正常，芯片引脚图正常，所有复选框可操作。

---

## 阶段4: 右侧预览面板（最大改动）

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段4: 右侧预览面板」，特别注意 ttk.Notebook → CTkTabview 的差异和 ScrolledText → CTkTextbox 的索引变化。

找到 build_preview_panel() 方法，分析：

1. 当前有多少个 Tab 页？列出每个 Tab 的名称
2. 每个 Tab 里主要放了什么控件？（Text/Canvas/Frame/Label...）
3. 搜索全文件，所有 self.notebook 的引用位置（select/add/index 等）
4. 搜索全文件，所有 .insert("1.0" 和 tk.END 和 .delete("1.0" 的位置
5. 哪些 Tab 用了 Canvas（这些 Canvas 不需要改）
6. 哪些 Tab 用了 ScrolledText 或 tk.Text（这些需要改为 CTkTextbox）

这是最复杂的阶段，给我一份详细的改动清单，按Tab分组列出。
```

### 【Execute指令 - 第一步：Tabview替换】

```
先只做 Notebook → Tabview 的替换：

1. 把 ttk.Notebook 创建替换为 ctk.CTkTabview
2. 把所有 self.notebook.add(frame, text="xxx") 替换为 frame = self.tabview.add("xxx")
3. 16个Tab名称尽量缩短（如果原来很长的话），避免Tab栏拥挤
4. 把所有 self.notebook.select(N) 替换为 self.tabview.set("标签名")
5. 把所有 self.notebook.pack(...) 替换为 self.tabview.pack(...)

注意：先不改 Tab 内部的控件，只改 Notebook → Tabview 外壳。这样可以分步测试。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 预期：Tab栏显示为CTk风格的分段按钮，Tab可切换，内部内容可能显示异常但Tab框架不崩溃。

### 【Execute指令 - 第二步：Text控件替换】

```
现在替换所有 Tab 内部的文本控件：

1. 所有 scrolledtext.ScrolledText → ctk.CTkTextbox
2. 所有 tk.Text → ctk.CTkTextbox
3. 参数替换：
   - wrap=tk.NONE → wrap="none"
   - wrap=tk.WORD → wrap="word"
   - bg="xxx" → fg_color="xxx"
   - fg="xxx" → text_color="xxx"
   - insertbackground → 删除（CTkTextbox不支持）
   - selectbackground → 删除
   - relief=tk.FLAT → 删除
   - state=tk.DISABLED → state="disabled"
   - state=tk.NORMAL → state="normal"

4. 全局替换文本索引（最关键！）：
   - 所有 .insert("1.0", → .insert("0.0",
   - 所有 .delete("1.0", tk.END) → .delete("0.0", "end")
   - 所有 .get("1.0", tk.END) → .get("0.0", "end")
   - 其他 tk.END 引用 → "end"

5. 如果有 text.config(state=tk.DISABLED) → text.configure(state="disabled")

6. 如果有语法高亮用到 tag_config / tag_add：
   - 尝试通过 self.pat_text._textbox.tag_config(...) 访问底层Text widget
   - 如果不行，在该控件上保持使用 tk.Text 不迁移，外面包一个 CTkFrame

列出所有修改位置。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 预期：点击生成后，PAT/TXT预览Tab能正常显示文本内容。

### 【Execute指令 - 第三步：Frame和Label替换】

```
替换所有 Tab 内部剩余的 tkinter 控件：

1. 所有 tk.Frame（在Tab页内部的） → ctk.CTkFrame
   - bg= → fg_color=
   - relief= → 删除
   - bd= → 删除
2. 所有 tk.Label（在Tab页内部的） → ctk.CTkLabel
   - fg= → text_color=
   - bg= → fg_color= 或 fg_color="transparent"
3. 所有 tk.Button（在Tab页内部的） → ctk.CTkButton
4. tk.Canvas 不动

注意：有些 Tab 页里可能混合了 Canvas 和其他控件，Canvas 的父容器换成 CTkFrame 后 Canvas 仍然正常工作。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 逐个点击所有16个Tab页，确认每个Tab都不崩溃，Canvas绘制正常。

---

## 阶段5: 弹窗和对话框

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段5: 弹窗和对话框」。

搜索全文件：
1. 所有 tk.Toplevel 的使用位置
2. 所有在 Toplevel 内部创建的控件
3. messagebox 和 filedialog 使用位置（这些不需要改，只需确认）

列出需要修改的 Toplevel 弹窗清单。
```

### 【Execute指令】

```
替换所有弹窗：

1. tk.Toplevel → ctk.CTkToplevel
2. 弹窗内部的 tk.Frame → ctk.CTkFrame
3. 弹窗内部的 tk.Label → ctk.CTkLabel
4. 弹窗内部的 tk.Button → ctk.CTkButton
5. 弹窗内部的 tk.Text / ScrolledText → ctk.CTkTextbox（记得改索引 "1.0" → "0.0"）
6. messagebox 和 filedialog 保持不变

改完后告诉我总共替换了几个弹窗。
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 点击"时序检查"和"协议检查"按钮，确认弹窗正常弹出和显示。

---

## 阶段6: 主题和配色系统

### 【Plan指令】

```
读一下 MIGRATION_PLAN.md 的「阶段6: 主题和配色系统」。

分析当前的主题系统：
1. self.colors 字典有哪些key和value？
2. _toggle_theme() 方法是怎么实现的？是销毁重建还是逐控件更新？
3. 有没有 THEMES 常量定义多套主题色？
4. Canvas 绘制代码里硬编码了哪些颜色？

评估：CTk 的自动主题切换能替代多少现有的手动主题逻辑？
```

### 【Execute指令】

```
优化主题系统：

1. 如果 _toggle_theme() 是销毁重建UI的方式，简化为：
   def _toggle_theme(self):
       current = ctk.get_appearance_mode()
       ctk.set_appearance_mode("light" if current == "Dark" else "dark")
       # Canvas 需要手动更新颜色
       self._update_canvas_colors()

2. 添加 _update_canvas_colors() 方法：在主题切换后更新所有 Canvas 的背景色和绘制颜色

3. 删除 self.colors 字典中已被 CTk 主题覆盖的颜色（如控件背景色、文字色）
   保留 Canvas 专用色和自定义强调色

4. 确保暗色模式下所有文字可读、所有控件可见
```

### 【测试命令】
```bash
python at24c02_pat_generator.py
```
> 点击主题切换按钮，确认：暗色→浅色→暗色 切换不崩溃，Canvas颜色跟随切换。

---

## 阶段7: 最终打磨和打包

### 【Plan指令】

```
迁移基本完成。现在做最终检查：

1. 搜索全文件，是否还有残留的 ttk. 引用（除了 ttk.Style 的 pass 方法）
2. 搜索是否还有 tk.Frame / tk.Label / tk.Button 引用（Canvas 除外）
3. 搜索是否还有 "1.0" 字符串用于文本索引（应该全改成 "0.0"）
4. 搜索是否还有 tk.END 引用（应该改成 "end"）
5. 检查所有 .configure() 调用是否有 bg= 参数（应改为 fg_color=）
6. 列出所有残留项
```

### 【Execute指令】

```
修复所有残留项。然后做以下最终打磨：

1. 统一字体：
   - 在 PatGeneratorApp.__init__() 里定义字体常量：
     self.FONT_TITLE = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
     self.FONT_HEADING = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
     self.FONT_BODY = ctk.CTkFont(family="Segoe UI", size=12)
     self.FONT_MONO = ctk.CTkFont(family="Consolas", size=13)
   - 替换所有硬编码的 font=(...) 为这些常量

2. 统一控件间距：
   - 分组之间 pady=8
   - 同组控件之间 pady=3
   - 面板边距 padx=8, pady=8

3. 确保生成和导出按钮在视觉上最突出（最大、颜色最醒目）

4. 删除所有已无用的 ttk.Style 相关代码

5. 更新文件顶部的版本号注释（v8.x → v9.0 或标注 CustomTkinter 迁移版本）
```

### 【打包测试指令】

```
现在测试 PyInstaller 打包。运行以下命令并报告结果：

pip install customtkinter pyinstaller
pyinstaller --onefile --windowed --name AT24C02_PAT_Generator_v2.0 --hidden-import customtkinter --collect-data customtkinter at24c02_pat_generator.py

如果报错，分析错误信息并修复。常见问题：
- ModuleNotFoundError: customtkinter → 加 --hidden-import
- 缺少数据文件 → 加 --collect-data customtkinter
- DLL 加载失败 → 检查是否需要 --collect-all customtkinter
```

### 【最终验收测试清单】

```
打包成功后，双击 dist/AT24C02_PAT_Generator_v2.0.exe，逐项测试：

1. [ ] exe 正常启动，无白屏
2. [ ] 顶部工具栏所有控件可操作
3. [ ] A2/A1/A0 Spinbox 可增减，器件地址实时更新
4. [ ] VCC Combobox 可下拉选择
5. [ ] 左侧面板可折叠/展开
6. [ ] 10个测试复选框可勾选/取消
7. [ ] 点击「生成PAT」→ 右侧PAT预览正常显示内容
8. [ ] 切换到TXT预览Tab → 正常显示
9. [ ] 切换到波形图Tab → Canvas波形正常绘制
10. [ ] 切换到流程图Tab → Canvas流程图正常
11. [ ] 切换到统计Tab → 条形图/饼图正常
12. [ ] 切换到Shmoo Tab → Canvas散点图正常
13. [ ] 切换到Wafer Map Tab → 晶圆图正常
14. [ ] 切换到调试器Tab → 功能正常
15. [ ] 点击「导出文件」→ 文件正常保存
16. [ ] 导出的 .pat 文件内容正确
17. [ ] 导出的 .prg / .tim / .lvl 文件正确
18. [ ] 点击「时序检查」→ 弹窗正常
19. [ ] 点击「协议检查」→ 弹窗正常
20. [ ] 主题切换（暗↔亮）不崩溃
21. [ ] 语言切换（中↔英）不崩溃
22. [ ] 配置保存/加载正常
23. [ ] 关闭窗口无报错
```

---

## 回滚方案

如果迁移过程中某个阶段出了严重问题无法修复：

```
回滚到备份版本：
copy at24c02_pat_generator_tkonly_backup.py at24c02_pat_generator.py

这会恢复到迁移前的纯tkinter版本，所有功能正常。
```

每完成一个阶段且测试通过后，建议额外备份一次：
```
copy at24c02_pat_generator.py at24c02_pat_generator_stage1_ok.py
copy at24c02_pat_generator.py at24c02_pat_generator_stage2_ok.py
...
```
这样如果阶段4出问题可以回滚到阶段3而不是最初版本。
