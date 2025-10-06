# 通用领域Abstract收集器

一个可扩展的学术论文abstract收集系统，支持多个研究领域。

## 🚀 特性

- **多领域支持**: CS, Chemistry, Biology, Physics, Medicine
- **可扩展设计**: 通过学者名单文件轻松添加新领域
- **连续发表检测**: 找到连续4年(2021-2024)第一/二作者发表论文的研究者
- **API优化**: 支持Semantic Scholar API key，提高请求限制
- **进度保存**: 支持中断恢复，避免重复工作

## 📁 项目结构

```
abstract_collection/
├── src/
│   └── cs_abstract_collector.py  # 主程序（已重命名为通用收集器）
├── scholars/
│   └── cs_scholars.txt           # CS领域学者名单
├── output_CS/                    # CS领域输出目录
├── requirements.txt
└── README.md
```

## 🛠️ 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

在 `src/cs_abstract_collector.py` 中设置你的Semantic Scholar API key：

```python
api_key = "your_api_key_here"
```

### 3. 运行程序

```bash
cd src
python cs_abstract_collector.py
```

## 📚 学者名单文件格式

学者名单文件位于 `scholars/` 目录，命名格式：`{field}_scholars.txt`

### 文件格式示例：

```
# CS领域学者名单
# 每行一个学者姓名，支持注释（以#开头）

# ===== 资深学者 =====
Yoshua Bengio
Geoffrey Hinton
Yann LeCun
Andrew Ng

# ===== 机器学习专家 =====
Kaiming He
Ross Girshick
Ilya Sutskever
```

## 🔧 添加新领域

### 1. 创建学者名单文件

在 `scholars/` 目录下创建新的学者名单文件，例如 `chemistry_scholars.txt`

### 2. 修改程序配置

在 `src/cs_abstract_collector.py` 中：

```python
# 修改领域
field = "Chemistry"  # 新领域
collector = AbstractCollector(field=field, output_dir=f"output_{field}", api_key=api_key)
```

### 3. 添加领域关键词（可选）

在 `_get_field_keywords()` 方法中添加新领域的关键词：

```python
'CHEMISTRY': [
    'chemistry', 'chemical', 'molecule', 'compound', 'synthesis',
    'reaction', 'catalyst', 'organic', 'inorganic', 'analytical'
]
```

## 📊 输出格式

### 文件命名规则

```
Academic_{Field}_{Year}_{Index}.txt
```

例如：
- `Academic_CS_2021_01.txt` - CS领域2021年，作者索引01
- `Academic_CS_2022_01.txt` - CS领域2022年，作者索引01（同一作者）

### 文件内容格式

```
Title: 论文标题

Abstract:
论文摘要内容...
```

## 🎯 使用场景

### CS领域示例

```python
field = "CS"
collector = AbstractCollector(field=field, output_dir="output_CS", api_key=api_key)
collector.run(target_authors=20)  # 找20个连续4年第一/二作者
```

### 化学领域示例

```python
field = "Chemistry"
collector = AbstractCollector(field=field, output_dir="output_Chemistry", api_key=api_key)
collector.run(target_authors=20)
```

## 📈 扩展计划

- [ ] 添加更多领域支持
- [ ] 支持自定义年份范围
- [ ] 添加论文质量筛选
- [ ] 支持批量处理多个领域
- [ ] 添加Web界面

## 🔍 技术细节

- **API限制**: 1请求/秒（使用API key）
- **搜索策略**: 学者名单 + 论文关键词搜索
- **筛选条件**: 年份(2021-2024) + 领域关键词 + 作者位置(第一/二作者)
- **连续性要求**: 严格连续4年每年都有论文发表

## 📝 注意事项

1. **API Key**: 建议申请Semantic Scholar API key以提高请求限制
2. **网络稳定**: 确保网络连接稳定，程序会自动处理限流
3. **存储空间**: 每个领域约产生80-100个文件，请确保有足够存储空间
4. **运行时间**: 完整运行可能需要数小时，程序支持进度保存和恢复

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License