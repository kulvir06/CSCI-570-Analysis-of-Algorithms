# imports
import sys
import os
from resource import *
import time
import psutil

DELTA = 30 

ALPHA = {
    'A': {'A': 0,   'C': 110, 'G': 48,  'T': 94},
    'C': {'A': 110, 'C': 0,   'G': 118, 'T': 48},
    'G': {'A': 48,  'C': 118, 'G': 0,   'T': 110},
    'T': {'A': 94,  'C': 48,  'G': 110, 'T': 0},
}

# reference: CSCI 570 Fall25 Project Description
def process_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024) # in KB
    return memory_consumed

""" input string generator """
def generate_input_string(base, positions):
    s = base
    for n in positions:
        # Insert s after index n
        s = s[:n+1] + s + s[n+1:]
    return s

""" read file utility """
def read_input_file(path):
    # read input file
    with open(path, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    idx = 0
    n = len(lines)

    s0 = lines[idx] # base string s0
    idx += 1 
    s_positions = []
    while idx < n and not lines[idx].isalpha():  # read numbers until next base string
        s_positions.append(int(lines[idx]))
        idx += 1

    t0 = lines[idx] # base string t0                
    idx += 1
    t_positions = []
    while idx < n:
        t_positions.append(int(lines[idx]))
        idx += 1

    return s0, s_positions, t0, t_positions


""" basic dp algorithm """
def basic_DP_algorithm(strX, strY):
    m = len(strX)
    n = len(strY)

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base Case
    for i in range(1, m+1):
        dp[i][0] = i * DELTA
    for j in range(1, n+1):
        dp[0][j] = j * DELTA

    for i in range(1, m+1):
        for j in range(1, n+1):
            strX_i = strX[i-1]
            strY_j = strY[j-1]
            dp[i][j] = min(
                dp[i-1][j-1] + ALPHA[strX_i][strY_j],
                dp[i-1][j] + DELTA,
                dp[i][j-1] + DELTA
            )
    cost = dp[m][n]

    # reconstruct alignments via top down pass
    alignment_X = ""
    alignment_Y = ""
    i = m
    j = n

    while i > 0 or j > 0:
        if i > 0 and j > 0:
            strX_i = strX[i-1]
            strY_j = strY[j-1]
            # case 1: strX_i matched with strY_j
            if dp[i][j] == dp[i-1][j-1] + ALPHA[strX_i][strY_j]:
                alignment_X += strX_i
                alignment_Y += strY_j
                i -= 1
                j -= 1
                continue
        
        # case 2: gap in string Y
        if i > 0 and dp[i][j] == dp[i-1][j] + DELTA:
            alignment_X += strX[i-1]
            alignment_Y += '_'
            i -= 1
        # case 3: gap in string X
        else:
            alignment_X += '_'
            alignment_Y += strY[j-1]
            j -= 1  
    
    # reverse alignments
    alignment_X = alignment_X[::-1]
    alignment_Y = alignment_Y[::-1]

    return cost, alignment_X, alignment_Y

def main():
    if len(sys.argv) != 3:
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    s0, s_pos, t0, t_pos = read_input_file(input_file)

    s_final = generate_input_string(s0, s_pos)
    t_final = generate_input_string(t0, t_pos)

    # Call Basic DP Algorithm
    mem_before = process_memory()
    start_time = time.time()
    cost, alignment_X, alignment_Y = basic_DP_algorithm(s_final, t_final)
    end_time = time.time()
    mem_after = process_memory()

    total_time_in_ms = (end_time - start_time) * 1000
    total_memory_in_kb = mem_after - mem_before

    # Write output to output file
    with open(output_file, "w") as f:
        f.write(f"{cost}\n")
        f.write(f"{alignment_X}\n")
        f.write(f"{alignment_Y}\n")
        f.write(f"{total_time_in_ms}\n")
        f.write(f"{total_memory_in_kb}\n")

    
if __name__ == "__main__":
    main()



