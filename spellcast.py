from collections import Counter, defaultdict
from functools import reduce
from itertools import chain, product

# 2x is upper case
LETTERS = 'abcdefghijklmnopqrstuvwxyz'
LETTERVALS = (1, 4, 5, 3, 1, 5, 3, 4, 1, 7, 3, 3, 4, 2, 1, 4, 8, 2, 2, 2, 4, 5, 5, 7, 4, 8)

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

class WordBoard:
    def __init__(self):
        self.double = (-1,-1)
        with open('words.txt') as f:
            self.words = [word[:-1] for word in f.readlines()]
        
        self.trie = Trie()
        for word in self.words:
            self.trie.insert(word)

    def recalculate(self):
        maxGlobalMultiplier = max(self.wordMultipliers.values(), default=1)
        maxCharMultiplier = defaultdict(lambda: 1)
        for i, j in product(range(5), range(5)):
            maxCharMultiplier[self.board[i][j]] = max(maxCharMultiplier[self.board[i][j]], maxGlobalMultiplier, self.letterMultipliers[(i, j)])

        self.letterVals = [v * maxCharMultiplier[LETTERS[i]] for i, v in enumerate(LETTERVALS)]
        self.boardValue = {(i, j): self.letterVals[ord(self.board[i][j].lower()) - ord('a')] for i, j in product(range(5), range(5))}
        self.value = lambda word: sum(self.letterVals[ord(c.lower()) - ord('a')] for c in word if c.lower() in LETTERS)
        self.wordValues = [(self.value(word), word) for word in self.words]
        self.wordValues.sort(reverse=True)
    
    def setBoard(self, board):
        self.board = board
        self.n = len(board)
        self.m = len(board[0])
        self.totalCount = Counter(chain(*board))
        
        self.wordMultipliers = defaultdict(lambda: 1) # word multiplier at (i, j)
        self.letterMultipliers = defaultdict(lambda: 1) # letter multiplier at (i, j)
        self.recalculate()

    def precheck(self, word):
        wCount = Counter(word)
        for c in wCount:
            if wCount[c] > self.totalCount[c]:
                return False
        return self.trie.search(word)
    def boardContains(self, word, skips=0):
        n, m = self.n, self.m
        if not skips and not self.precheck(word):
            return ([], 0, [])
        
        stack = []
        memo = set()

        for i in range(n):
            for j in range(m):
                if self.board[i][j] != word[0]:
                    continue

                stack.append(([(i, j)], 1, {(i, j): True}, [], skips))
                memo.clear()

                while stack:
                    path, index, visited, skipped, remaining_skips = stack[-1]

                    if index == len(word):
                        value = sum(self.letterMultipliers[x] * LETTERVALS[ord(word[ind].lower()) - ord('a')] for ind, x in enumerate(path[::-1])) * reduce(lambda acc, cur: acc * self.wordMultipliers[cur], path, 1)
                        return path, value, skipped

                    x, y = path[-1]
                    found_next = False
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and (nx, ny) not in visited:
                            if self.board[nx][ny] == word[index]:
                                if (nx, ny, index, remaining_skips) not in memo:
                                    stack.append((path + [(nx, ny)], index + 1, {**visited, (nx, ny): True}, skipped + [(nx, ny)], remaining_skips))
                                    memo.add((nx, ny, index, remaining_skips))
                                    found_next = True
                                    break
                            elif remaining_skips > 0:
                                if (nx, ny, index, remaining_skips - 1) not in memo:
                                    stack.append((path + [(nx, ny)], index + 1, {**visited, (nx, ny): True}, skipped + [(nx, ny)], remaining_skips - 1))
                                    memo.add((nx, ny, index, remaining_skips - 1))
                                    found_next = True
                                    break
                    if not found_next:
                        stack.pop()

        return ([], 0, [])


    def bestWord(self, skips=0):
        curBest = ("", 0, [], [])
        curVal = 0
        for _, word in self.wordValues:
            path, actualValue, skipped = self.boardContains(word, skips)
            visword = word
            if(self.double in path):
                actualValue *= 2
                visword += "(2x "  + str(actualValue//2) + "->" + str(actualValue) + ")"
            if(len(word) >= 6):
                actualValue += 10
                visword += "(long +10)"
            if path and actualValue > curVal:
                curVal = actualValue
                curBest = (visword, actualValue, path, skipped)
        return curBest

if __name__ == "__main__":
    # Read board and create wordboard
    #input("input dl")
    board = [[c for c in input()] for _ in range(5)]
    for i in range(len(board)):
        for j in range(len(board[0])):
            coord = (i,j)
            if(board[i][j].upper() == board[i][j]):
                double = coord
            board[i][j] = board[i][j].lower()
    wb = WordBoard()
    wb.double = double
    wb.setBoard(board)

    # Find best words
    wg = wb.bestWord()    # no swaps
    wgS1 = wb.bestWord(1)    # one swap
    wgS2 = wb.bestWord(2)    # two swaps

    print("No swaps:", wg)
    print("One swap:", wgS1)
    print("Two swaps:", wgS2)