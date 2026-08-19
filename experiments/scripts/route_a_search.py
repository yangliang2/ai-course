"""
路线 A（知识库）检索脚本：查询 → top-k 片段。

用法: python route_a_search.py <index_pkl> "<query>"
"""
import pickle
import sys

import numpy as np


def search(index_path, query, top_k=8):
    with open(index_path, 'rb') as f:
        idx = pickle.load(f)
    chunks, meta, vectorizer, tfidf = idx['chunks'], idx['meta'], idx['vectorizer'], idx['tfidf']
    q = vectorizer.transform([query])
    scores = (tfidf @ q.T).toarray().ravel()
    top = np.argsort(scores)[::-1][:top_k]
    for rank, i in enumerate(top):
        src, kind, ln = meta[i]
        print(f"\n[{rank+1}] score={scores[i]:.3f} | {src} | {kind} | {ln} chars")
        print("    " + chunks[i][:150].replace('\n', ' '))
    return [(meta[i], scores[i], chunks[i]) for i in top]


if __name__ == '__main__':
    search(sys.argv[1], sys.argv[2])
