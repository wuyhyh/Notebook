class TrieNode:
    def __init__(self):
        self.children = {}  # 存储子节点
        self.is_end = False  # 表示是否是一个单词的结尾

class Trie:
    def __init__(self):
        self.root = TrieNode()  # 初始化根节点

    def insert(self, word):
        """
        插入一个单词到前缀树中
        :type word: str
        :rtype: None
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True  # 标记单词结尾

    def search(self, word):
        """
        搜索一个单词是否存在于前缀树中
        :type word: str
        :rtype: bool
        """
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):
        """
        判断是否存在以 prefix 为前缀的单词
        :type prefix: str
        :rtype: bool
        """
        return self._find_node(prefix) is not None

    def _find_node(self, prefix):
        """
        辅助函数：根据前缀返回最后一个节点
        :type prefix: str
        :rtype: TrieNode
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
