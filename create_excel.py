import pandas as pd

# 创建示例数据
data = {
    'A': [
        "什么是人工智能？",
        "Python 是什么编程语言？",
        "如何学习编程？"
    ]
}

# 创建 DataFrame
df = pd.DataFrame(data)

# 保存为 Excel 文件
df.to_excel('input.xlsx', index=False)

print("已创建 input.xlsx 文件！") 