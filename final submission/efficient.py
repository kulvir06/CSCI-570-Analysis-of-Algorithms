#!/usr/bin/env python3
import sys
import time
import psutil

DELTA = 30  # gap penalty

# mismatch costs
ALPHA = {
    'A': {'A': 0,   'C': 110, 'G': 48,  'T': 94},
    'C': {'A': 110, 'C': 0,   'G': 118, 'T': 48},
    'G': {'A': 48,  'C': 118, 'G': 0,   'T': 110},
    'T': {'A': 94,  'C': 48,  'G': 110, 'T': 0}
}

# ----- Input parsing (string generator) -----
def read_generator_input(path):
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() != '']

    i = 0
    # first base string s0
    if i >= len(lines):
        raise ValueError("Empty input")
    s0 = lines[i]; i += 1

    s_indices = []
    # numbers until next base string line (non-digit = base string)
    while i < len(lines) and lines[i].isdigit():
        s_indices.append(int(lines[i]))
        i += 1

    if i >= len(lines):
        raise ValueError("Input incomplete: missing second base string")
    t0 = lines[i]; i += 1

    t_indices = []
    while i < len(lines) and lines[i].isdigit():
        t_indices.append(int(lines[i]))
        i += 1

    def build_string(base, indices):
        cur = base
        for idx in indices:
            cur = cur[:idx+1] + cur + cur[idx+1:]
        return cur

    s_final = build_string(s0, s_indices)
    t_final = build_string(t0, t_indices)
    return s_final, t_final

# ----- Full DP (need when one dimension small) -----
def needleman_wunsch_full(X, Y):
    m, n = len(X), len(Y)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        dp[i][0] = i * DELTA
    for j in range(1, n+1):
        dp[0][j] = j * DELTA

    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = min(
                dp[i-1][j-1] + ALPHA[X[i-1]][Y[j-1]],
                dp[i-1][j] + DELTA,
                dp[i][j-1] + DELTA
            )

    # backtrack
    i, j = m, n
    aX, aY = [], []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + ALPHA[X[i-1]][Y[j-1]]:
            aX.append(X[i-1])
            aY.append(Y[j-1])
            i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + DELTA:
            aX.append(X[i-1])
            aY.append('_')
            i -= 1
        else:
            aX.append('_')
            aY.append(Y[j-1])
            j -= 1

    return ''.join(reversed(aX)), ''.join(reversed(aY))

# ----- Linear-space DP returning score vector -----
def nw_score_vector(X, Y):
    m, n = len(X), len(Y)
    prev = [j * DELTA for j in range(n+1)]
    for i in range(1, m+1):
        curr = [i * DELTA] + [0] * n
        xi = X[i-1]
        for j in range(1, n+1):
            curr[j] = min(
                prev[j-1] + ALPHA[xi][Y[j-1]],
                prev[j] + DELTA,
                curr[j-1] + DELTA
            )
        prev = curr
    return prev

# ----- Hirschberg recursion -----
def hirschberg(X, Y):
    m, n = len(X), len(Y)

    # base cases
    if m == 0:
        return ('_'*n, Y)
    if n == 0:
        return (X, '_'*m)
    # when one side is small, run full DP (safe and simple)
    if m == 1 or n == 1:
        return needleman_wunsch_full(X, Y)

    mid = m // 2
    scoreL = nw_score_vector(X[:mid], Y)
    scoreR = nw_score_vector(X[mid:][::-1], Y[::-1])

    best_k = 0
    best_val = None
    for k in range(n+1):
        val = scoreL[k] + scoreR[n-k]
        if best_val is None or val < best_val:
            best_val = val
            best_k = k

    leftX, leftY = hirschberg(X[:mid], Y[:best_k])
    rightX, rightY = hirschberg(X[mid:], Y[best_k:])
    return (leftX + rightX, leftY + rightY)

# ----- cost compute from alignment -----
def compute_alignment_cost(a1, a2):
    cost = 0
    for c1, c2 in zip(a1, a2):
        if c1 == '_' or c2 == '_':
            cost += DELTA
        else:
            cost += ALPHA[c1][c2]
    return cost

# ----- MAIN -----
def main():
    if len(sys.argv) != 3:
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    # generate strings
    s, t = read_generator_input(in_path)

    # measure memory using psutil
    proc = psutil.Process()

    mem_before = proc.memory_info().rss // 1024   # KB
    t_start = time.time()

    aligned_s, aligned_t = hirschberg(s, t)

    t_end = time.time()
    mem_after = proc.memory_info().rss // 1024    # KB

    time_ms = (t_end - t_start) * 1000.0
    mem_kb = mem_after - mem_before
    if mem_kb < 0:
        # in some environments rss can decrease; report 0 difference
        mem_kb = 0.0

    cost = compute_alignment_cost(aligned_s, aligned_t)

    # Write output to output file
    with open(out_path, 'w') as f:
        f.write(str(cost) + '\n')
        f.write(aligned_s + '\n')
        f.write(aligned_t + '\n')
        f.write(str(time_ms) + '\n')
        f.write(str(mem_kb) + '\n')

if __name__ == '__main__':
    main()
