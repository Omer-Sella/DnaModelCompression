import os

def get_error_summary(ref, read, is_seq=False):
    """
    Computes alignment between reference sequence and sequence provided. Assumes performing single
    sequence alignment.
    Parameters
    ----------
    ref : string
        Reference sequence
    read : string
        Read sequence
    is_seq : bool
        If True, ref and read are interpreted as raw sequences. Otherwise, they are interpreted as
        filenames for the reference and read sequence.
    Returns
    -------
    (int, int, int, int):
        Number of insertions, deletions, substitutions, and length of reference.
    """
    if not is_seq:
        # Read from files
        with open(os.path.join(ref)) as ref_f:
            ref = ref_f.readlines()[1].strip()
        with open(os.path.join(read)) as read_f:
            read = read_f.readlines()[1].strip()

    error_summary = sm_align(ref, read)

    _, _, _, ins, dels, subs = error_summary
    ref_length = len(ref)
    print("Insertion errors %.3f%%, deletion errors %.3f%%, substitution errors %.3f%%, error rate %.3f%%"
        % (ins / ref_length * 100, dels / ref_length * 100, subs / ref_length * 100, (ins + dels + subs) / ref_length * 100))

    return ins, dels, subs, ref_length


# get_similarity_score and sm_align adapted from
# https://github.com/JiaShun-Xiao/BLAST-bioinfor-tool/blob/master/blast.py
# TODO: refactor
def get_similarity_score(a, b, match_score=1, mismatch_score=-1):
    if a == b:
        return 1
    else:
        return -1


# Smith–Waterman Alignment
def sm_align(seq1, seq2, gap_penalty=3):
    ins = 0
    dels = 0
    subs = 0
    m = len(seq1)
    n = len(seq2)
    g = -gap_penalty
    matrix = []
    for i in range(0, m):
        tmp = []
        for j in range(0, n):
            tmp.append(0)
        matrix.append(tmp)
    for sii in range(0, m):
        matrix[sii][0] = sii*g
    for sjj in range(0, n):
        matrix[0][sjj] = sjj*g
    for siii in range(1, m):
        for sjjj in range(1, n):
            matrix[siii][sjjj] = max(matrix[siii-1][sjjj] + g, matrix[siii - 1][sjjj - 1] + get_similarity_score(seq1[siii], seq2[sjjj]), matrix[siii][sjjj-1] + g)
    sequ1 = [seq1[m-1]]
    sequ2 = [seq2[n-1]]
    while m > 1 and n > 1:
        if max(matrix[m-1][n-2], matrix[m-2][n-2], matrix[m-2][n-1]) == matrix[m-2][n-2]:
            m -= 1
            n -= 1
            sequ1.append(seq1[m-1])
            sequ2.append(seq2[n-1])
            if seq1[m-1] != seq2[n-1]:
                # Subsitution
                subs += 1
        elif max(matrix[m-1][n-2], matrix[m-2][n-2], matrix[m-2][n-1]) == matrix[m-1][n-2]:
            # Insertion
            n -= 1
            sequ1.append('-')
            sequ2.append(seq2[n-1])
            ins += 1
        else:
            # Deletion
            m -= 1
            sequ1.append(seq1[m-1])
            sequ2.append('-')
            dels += 1
    sequ1.reverse()
    sequ2.reverse()
    align_seq1 = ''.join(sequ1)
    align_seq2 = ''.join(sequ2)
    align_score = 0.
    for k in range(0, len(align_seq1)):
        if align_seq1[k] == align_seq2[k]:
            align_score += 1
    align_score = float(align_score)/len(align_seq1)
    return align_seq1, align_seq2, align_score, ins, dels, subs
