"""Assignment 4 algorithms. State is local to each JSON Lines request."""
from array import array
from collections import deque


def lcs(request):
    a, b = request['a'], request['b']
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = (dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1]
                        else max(dp[i - 1][j], dp[i][j - 1]))
    sequence = []
    i, j = n, m
    while i and j:
        if a[i - 1] == b[j - 1]:
            sequence.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return {'length': dp[n][m], 'sequence': ''.join(reversed(sequence))}


def merge(request):
    sizes = request['sizes']
    n = len(sizes)
    if n < 2:
        return {'cost': 0, 'plan': []}
    prefix = [0]
    for size in sizes:
        prefix.append(prefix[-1] + size)
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            best, pivot = min((dp[left][k] + dp[k + 1][right], k)
                              for k in range(left, right))
            dp[left][right] = best + prefix[right + 1] - prefix[left]
            split[left][right] = pivot
    plan = []
    stack = [(0, n - 1, False)]
    while stack:
        left, right, ready = stack.pop()
        if left == right:
            continue
        pivot = split[left][right]
        if ready:
            plan.append([left, pivot, right])
        else:
            # LIFO postorder emits both child plans before their parent merge.
            stack.extend([(left, right, True), (pivot + 1, right, False),
                          (left, pivot, False)])
    return {'cost': dp[0][-1], 'plan': plan}


def tree(request):
    n, weights = request['n'], request['weights']
    if not n:
        return {'weight': 0, 'selected': []}
    adjacent = [[] for _ in range(n)]
    for u, v in request['edges']:
        adjacent[u].append(v)
        adjacent[v].append(u)
    parent = [-1] * n
    order = [0]
    for u in order:
        for v in adjacent[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)
    take, skip = weights[:], [0] * n
    for u in reversed(order[1:]):
        p = parent[u]
        take[p] += skip[u]
        skip[p] += max(take[u], skip[u])
    chosen = [False] * n
    selected = []
    for u in order:
        chosen[u] = (parent[u] == -1 or not chosen[parent[u]]) and take[u] > skip[u]
        if chosen[u]:
            selected.append(u)
    return {'weight': max(take[0], skip[0]), 'selected': selected}


def naive(request):
    text, pattern = request['text'], request['pattern']
    n, m = len(text), len(pattern)
    positions = []
    for start in range(n - m + 1):
        j = 0
        while j < m and text[start + j] == pattern[j]:
            j += 1
        if j == m:
            positions.append(start)
    return {'positions': positions}


def kmp(request):
    text, pattern = request['text'], request['pattern']
    m = len(pattern)
    if not m:
        return {'positions': list(range(len(text) + 1))}
    pi = [0] * m
    j = 0
    for i in range(1, m):
        while j and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    positions = []
    j = 0
    for i, character in enumerate(text):
        while j and character != pattern[j]:
            j = pi[j - 1]
        if character == pattern[j]:
            j += 1
        if j == m:
            positions.append(i - m + 1)
            j = pi[j - 1]
    return {'positions': positions}


def rk(request):
    text, pattern = request['text'], request['pattern']
    n, m = len(text), len(pattern)
    if not m:
        return {'positions': list(range(n + 1))}
    if m > n:
        return {'positions': []}
    power = pow(31, m - 1, 101)
    target = window = 0
    for i in range(m):
        target = (target * 31 + ord(pattern[i])) % 101
        window = (window * 31 + ord(text[i])) % 101
    positions = []
    for start in range(n - m + 1):
        if target == window:
            j = 0
            while j < m and text[start + j] == pattern[j]:
                j += 1
            if j == m:
                positions.append(start)
        if start < n - m:
            # Python % with a positive divisor normalizes negative intermediates.
            window = ((window - ord(text[start]) * power) * 31 + ord(text[start + m])) % 101
    return {'positions': positions}


def suffix(request):
    text = request['text']
    n = len(text)
    sa = list(range(n))
    rank = list(map(ord, text))
    width = 1
    while width < n:
        pairs = [(rank[i], rank[i + width] if i + width < n else -1) for i in range(n)]
        sa.sort(key=pairs.__getitem__)
        new_rank = [0] * n
        for j in range(1, n):
            new_rank[sa[j]] = new_rank[sa[j - 1]] + (pairs[sa[j]] != pairs[sa[j - 1]])
        rank = new_rank
        if rank[sa[-1]] == n - 1:
            break
        width *= 2
    inverse = [0] * n
    for j, start in enumerate(sa):
        inverse[start] = j
    lcp = [0] * n
    common = best_length = best_start = 0
    for start in range(n):
        place = inverse[start]
        if place == 0:
            common = 0
            continue
        other = sa[place - 1]
        while start + common < n and other + common < n and text[start + common] == text[other + common]:
            common += 1
        lcp[place] = common
        if common > best_length:
            best_length, best_start = common, start
        common = max(0, common - 1)
    return {'sa': sa, 'lcp': lcp, 'repeated': text[best_start:best_start + best_length]}


def aho(request):
    # Packed rows avoid millions of separate Python integer objects.
    transitions = [array('i', [0]) * 95]
    terminal = []
    for pattern in request['patterns']:
        state = 0
        for character in pattern:
            c = ord(character) - 32
            if transitions[state][c] == 0:
                transitions[state][c] = len(transitions)
                transitions.append(array('i', [0]) * 95)
            state = transitions[state][c]
        terminal.append(state)
    states = len(transitions)
    failure = [0] * states
    queue = deque(child for child in transitions[0] if child)
    order = []
    while queue:
        state = queue.popleft()
        order.append(state)
        row, fallback = transitions[state], transitions[failure[state]]
        for c in range(95):
            child = row[c]
            if child:
                failure[child] = fallback[c]
                queue.append(child)
            else:
                row[c] = fallback[c]
    counts = []
    for text in request['texts']:
        visits = [0] * states
        state = 0
        for character in text:
            state = transitions[state][ord(character) - 32]
            visits[state] += 1
        for state in reversed(order):
            visits[failure[state]] += visits[state]
        counts.append([visits[state] for state in terminal])
    return {'counts': counts}
