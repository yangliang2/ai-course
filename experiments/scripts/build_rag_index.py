"""
知识库路线（路线 A）的索引构建脚本。
将 fork 的 README + docs + 源码切片，TF-IDF 向量化建立检索索引。

用法: python build_rag_index.py <fork_path> <output_pkl_path>
例:   python build_rag_index.py ../loguru-fork rag_index.pkl
"""
import os
import re
import pickle
import sys

from sklearn.feature_extraction.text import TfidfVectorizer


def add_chunk(chunks, meta, text, source, kind):
    text = text.strip()
    if len(text) < 20:
        return
    chunks.append(text)
    meta.append((source, kind, len(text)))


def build_index(fork_path, out_path):
    chunks, meta = [], []

    # README
    with open(os.path.join(fork_path, 'README.md')) as f:
        readme = f.read()
    for i, block in enumerate(re.split(r'```[\s\S]*?```|\n\n+', readme)):
        if block.strip():
            add_chunk(chunks, meta, block, f'README.md#{i}', 'doc')

    # docs/
    docs_dir = os.path.join(fork_path, 'docs')
    for root, _, files in os.walk(docs_dir):
        for fn in files:
            if fn.endswith(('.md', '.rst', '.py')):
                p = os.path.join(root, fn)
                try:
                    with open(p) as f:
                        text = f.read()
                except Exception:
                    continue
                for i, block in enumerate(re.split(r'\n#{1,4} |\n\n+', text)):
                    if block.strip():
                        add_chunk(chunks, meta, block, p, 'doc')

    # loguru/*.py 源码，按 def/class 切片
    pkg_dir = os.path.join(fork_path, 'loguru')
    for fn in os.listdir(pkg_dir):
        if not fn.endswith('.py'):
            continue
        p = os.path.join(pkg_dir, fn)
        with open(p) as f:
            lines = f.readlines()
        cur = []
        def flush():
            if cur:
                add_chunk(chunks, meta, ''.join(cur), p, 'code')
        for line in lines:
            if re.match(r'\s*(def |class |@|async def )', line):
                flush(); cur = [line]
            else:
                cur.append(line)
        flush()

    print(f"总切片数: {len(chunks)}")
    kinds = {}
    for _, k, _ in meta:
        kinds[k] = kinds.get(k, 0) + 1
    print(f"类型分布: {kinds}")

    vectorizer = TfidfVectorizer(stop_words='english', max_features=20000)
    tfidf = vectorizer.fit_transform(chunks)
    print(f"TF-IDF 矩阵: {tfidf.shape}")

    with open(out_path, 'wb') as f:
        pickle.dump({'chunks': chunks, 'meta': meta,
                     'vectorizer': vectorizer, 'tfidf': tfidf}, f)
    print(f"索引已保存: {out_path}")


if __name__ == '__main__':
    build_index(sys.argv[1], sys.argv[2])
