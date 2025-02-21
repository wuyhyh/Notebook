from collections import defaultdict

def group_anagrams(strs):
    # 创建一个字典来存储字母异位词组
    anagrams = defaultdict(list)

    # 遍历字符串列表
    for s in strs:
        # 将字符串排序，作为字典的键
        sorted_str = ''.join(sorted(s))
        # 将原始字符串加入对应的键的列表中
        anagrams[sorted_str].append(s)

    # 返回字典中所有值的列表
    return list(anagrams.values())

# 示例用法
strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
result = group_anagrams(strs)

# 输出结果
print(result)  # 输出: [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
