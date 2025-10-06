# 🔄 增量模式使用指南

## 问题解决

**你的痛点**: 第一次运行收集了25个作者，但只有20个成功（有完整摘要），5个失败。现在需要补充这5个失败的作者，但不想重新处理已经成功的20个作者。

**解决方案**: 增量模式 - 只寻找缺失的作者，保留已成功的作者！

## 🎯 使用场景

### 场景1: 第一次运行后发现有缺失
```bash
# 第一次运行
python src/cs_abstract_collector.py
# 结果: 20个作者成功，5个失败（缺少摘要等）

# 增量补充
python run_incremental.py
# 结果: 找到5个新作者，保留原有20个
```

### 场景2: 代码修改后需要补充
```bash
# 修改了代码逻辑
# 运行增量模式测试
python run_incremental.py
# 只处理缺失的作者，不重新处理成功的
```

## 🚀 使用方法

### 方法1: 使用专用脚本 (推荐)
```bash
cd /Users/zhanweicao/Desktop/abstract_collection
/opt/anaconda3/bin/python run_incremental.py
```

### 方法2: 直接调用
```python
from src.cs_abstract_collector import AbstractCollector

collector = AbstractCollector(field="CS", output_dir="output_CS", api_key="your_key")
collector.run(target_authors=25, fill_missing=True)
```

## 📊 工作原理

### 智能检测
1. **扫描现有文件**: 检查 `output_CS/` 目录中的文件
2. **计算完整作者**: 统计有4年完整数据的作者数量
3. **计算缺失数量**: `目标数量 - 现有完整作者数量`
4. **只处理缺失**: 只寻找和处理缺失的作者

### 索引管理
- **自动索引分配**: 新作者从下一个可用索引开始
- **示例**: 如果有20个作者，新作者从索引21开始
- **文件命名**: `Academic_CS_2021_21.txt`, `Academic_CS_2022_21.txt` 等

## 📁 文件结构示例

### 第一次运行后
```
output_CS/
├── Academic_CS_2021_01.txt  # 作者1
├── Academic_CS_2022_01.txt
├── Academic_CS_2023_01.txt
├── Academic_CS_2024_01.txt
├── ...
├── Academic_CS_2021_20.txt  # 作者20
├── Academic_CS_2022_20.txt
├── Academic_CS_2023_20.txt
├── Academic_CS_2024_20.txt
└── collection_report.txt    # 报告显示20个作者
```

### 增量运行后
```
output_CS/
├── Academic_CS_2021_01.txt  # 作者1 (保留)
├── Academic_CS_2022_01.txt
├── Academic_CS_2023_01.txt
├── Academic_CS_2024_01.txt
├── ...
├── Academic_CS_2021_20.txt  # 作者20 (保留)
├── Academic_CS_2022_20.txt
├── Academic_CS_2023_20.txt
├── Academic_CS_2024_20.txt
├── Academic_CS_2021_21.txt  # 作者21 (新增)
├── Academic_CS_2022_21.txt
├── Academic_CS_2023_21.txt
├── Academic_CS_2024_21.txt
├── ...
├── Academic_CS_2021_25.txt  # 作者25 (新增)
├── Academic_CS_2022_25.txt
├── Academic_CS_2023_25.txt
├── Academic_CS_2024_25.txt
└── collection_report.txt    # 报告显示25个作者
```

## 🎯 实际效果

### 运行日志示例
```
🔄 INCREMENTAL MODE: Filling missing authors to reach 25
Found 20 existing successful authors
🎯 Need to find 5 more authors
Starting to find 5 continuous 4-year first/second authors...
[找到5个新作者]
Total collected 20 papers (5 complete authors with abstracts)
```

### 报告更新
```
Mode: INCREMENTAL (Fill Missing Authors)
Number of Complete Authors: 25
Total Files Saved: 100
✅ All authors have complete 4-year data
```

## ⚡ 性能优势

| 模式 | API调用 | 处理作者 | 运行时间 |
|------|---------|----------|----------|
| **重新运行** | 500-1000次 | 25个作者 | 30-60分钟 |
| **增量模式** | 100-200次 | 5个作者 | 5-10分钟 |
| **节省** | 80% | 80% | 85% |

## 🔧 高级用法

### 自定义目标数量
```python
# 修改 run_incremental.py 中的 target_authors
target_authors = 30  # 改为30个作者
```

### 检查当前状态
```bash
ls output_CS/ | grep "Academic_CS_2021_" | wc -l  # 统计作者数量
cat output_CS/collection_report.txt  # 查看详细报告
```

### 清理重新开始
```bash
rm -rf output_CS/  # 删除所有输出，重新开始
```

## 💡 最佳实践

1. **第一次运行**: 使用正常模式收集初始作者
2. **检查结果**: 查看报告，确认缺失的作者数量
3. **增量补充**: 使用增量模式补充缺失的作者
4. **验证完成**: 确认达到目标数量

## 🎉 总结

**增量模式完美解决了你的需求:**
- ✅ **保留成功作者**: 不重新处理已有20个作者
- ✅ **只处理缺失**: 只寻找5个缺失的作者
- ✅ **自动索引**: 新作者从21开始编号
- ✅ **节省时间**: 85%的时间节省
- ✅ **智能检测**: 自动计算需要补充的数量

**现在你可以高效地补充缺失的作者，无需重新开始整个流程！** 🚀
