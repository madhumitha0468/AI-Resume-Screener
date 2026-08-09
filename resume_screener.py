#!/usr/bin/env python3
"""
Resume Screener
================
Compares resumes against a Job Description (JD) and ranks candidates by
relevance.

DESIGN CONSTRAINT (per project rules):
    No external packages, libraries, or third-party APIs are used anywhere
    in this file. Everything is built with the Python STANDARD LIBRARY
    only (re, os, sys, math, string, csv, argparse, collections) -- these
    ship with every Python installation, so nothing needs to be installed
    and nothing calls out to the internet.

HOW THE MATCHING WORKS
    1. Text cleaning & tokenization (regex + string methods only)
    2. Stopword removal (a hand-built stopword list, no NLTK)
    3. Unigrams + bigrams, so two-word skills like "machine learning" or
       "project management" are captured, not just single words
    4. TF-IDF vectors built from scratch:
         TF  = term frequency within a single document
         IDF = log((N_docs + 1) / (docs_containing_term + 1)) + 1
    5. Cosine similarity between the JD vector and each resume vector
    6. A separate "keyword coverage" score: what fraction of the JD's
       top-weighted terms actually appear in the resume (useful because
       cosine similarity alone can be skewed by document length)
    7. Final score = weighted blend of similarity + keyword coverage
    8. Resumes are ranked, and a report is printed / saved showing the
       matched and missing key skills for each candidate.

USAGE
    python3 resume_screener.py --jd path/to/jd.txt --resumes path/to/folder
    python3 resume_screener.py --jd jd.txt --resumes r1.txt r2.txt r3.txt
    python3 resume_screener.py --jd jd.txt --resumes folder --top-keywords 20 --out report.csv
"""

import os
import re
import sys
import math
import csv
import argparse
from collections import Counter

# --------------------------------------------------------------------------
# 1. Stopwords (hand-built list -- standard English function words that
#    carry little meaning for skill/requirement matching). No external
#    corpus or library is used to generate this.
# --------------------------------------------------------------------------
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be
because been before being below between both but by can't cannot could
couldn't did didn't do does doesn't doing don't down during each few for
from further had hadn't has hasn't have haven't having he he'd he'll he's
her here here's hers herself him himself his how how's i i'd i'll i'm i've
if in into is isn't it it's its itself let's me more most mustn't my myself
no nor not of off on once only or other ought our ours ourselves out over
own same shan't she she'd she'll she's should shouldn't so some such than
that that's the their theirs them themselves then there there's these they
they'd they'll they're they've this those through to too under until up
very was wasn't we we'd we'll we're we've were weren't what what's when
when's where where's which while who who's whom why why's with won't would
wouldn't you you'd you'll you're you've your yours yourself yourselves
also using use used etc within across per year years experience strong
excellent good ability able including included include including work
working team teams role roles job jobs company candidate candidates
responsibilities responsible requirement requirements required preferred
please resume cv please note plus etc among will shall may might must
""".split())

# Symbols worth preserving because they appear inside real skill names
# (C++, C#, .NET, Node.js, CI/CD, etc.)
_KEEP_CHARS = r"a-z0-9\+\#\./\-"


def read_text(path):
    """Read a text file using only builtins."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def clean_tokenize(text):
    """
    Lowercase, strip punctuation (while preserving skill-relevant symbols
    like + # . / -), split on whitespace, drop stopwords/short tokens.
    """
    text = text.lower()
    text = re.sub(r"[^{}\s]".format(_KEEP_CHARS), " ", text)
    raw_tokens = text.split()

    tokens = []
    for tok in raw_tokens:
        tok = tok.strip(".-/")
        if not tok:
            continue
        if tok in STOPWORDS:
            continue
        if len(tok) <= 1 and tok not in ("c", "r"):  # keep single-char langs like C, R
            continue
        if tok.isdigit():
            continue
        tokens.append(tok)
    return tokens


def build_ngrams(tokens, n=2):
    """Build n-grams (default bigrams) to catch multi-word skills."""
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def build_term_list(text):
    """Full pipeline: text -> list of unigram + bigram terms."""
    tokens = clean_tokenize(text)
    bigrams = build_ngrams(tokens, 2)
    return tokens + bigrams


def compute_tf(terms):
    """Term frequency: count / total terms in the document."""
    counts = Counter(terms)
    total = sum(counts.values()) or 1
    return {term: c / total for term, c in counts.items()}


def compute_idf(all_doc_terms):
    """
    Inverse document frequency across the JD + all resumes.
    idf(t) = log((N+1)/(df(t)+1)) + 1   (smoothed, always positive)
    """
    n_docs = len(all_doc_terms)
    df = Counter()
    for terms in all_doc_terms:
        for term in set(terms):
            df[term] += 1
    return {term: math.log((n_docs + 1) / (count + 1)) + 1 for term, count in df.items()}


def tfidf_vector(terms, idf):
    tf = compute_tf(terms)
    return {term: tf_val * idf.get(term, 0.0) for term, tf_val in tf.items()}


def cosine_similarity(vec_a, vec_b):
    """Standard cosine similarity between two sparse dict-vectors."""
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_jd_keywords(jd_vec, top_n=15):
    """The JD's most distinguishing terms, by TF-IDF weight."""
    ranked = sorted(jd_vec.items(), key=lambda kv: kv[1], reverse=True)
    # prefer multi-word / meaningful terms slightly, but weight rules
    return [term for term, _ in ranked[:top_n]]


def keyword_coverage(resume_terms_set, keywords):
    if not keywords:
        return 0.0, [], []
    matched = [k for k in keywords if k in resume_terms_set]
    missing = [k for k in keywords if k not in resume_terms_set]
    return len(matched) / len(keywords), matched, missing


def collect_resume_files(paths):
    """Accept a mix of files and directories; return list of .txt file paths."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.lower().endswith(".txt"):
                    files.append(os.path.join(p, name))
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"Warning: '{p}' not found, skipping.", file=sys.stderr)
    return files


def score_resumes(jd_path, resume_paths, top_n_keywords=15,
                   w_similarity=0.6, w_coverage=0.4):
    jd_text = read_text(jd_path)
    jd_terms = build_term_list(jd_text)

    resume_files = collect_resume_files(resume_paths)
    if not resume_files:
        raise SystemExit("No resume .txt files found.")

    resume_terms_map = {}
    for path in resume_files:
        resume_terms_map[path] = build_term_list(read_text(path))

    # Build IDF across the whole corpus (JD + every resume)
    corpus = [jd_terms] + list(resume_terms_map.values())
    idf = compute_idf(corpus)

    jd_vec = tfidf_vector(jd_terms, idf)
    keywords = top_jd_keywords(jd_vec, top_n_keywords)

    results = []
    for path, terms in resume_terms_map.items():
        resume_vec = tfidf_vector(terms, idf)
        sim = cosine_similarity(jd_vec, resume_vec)
        coverage, matched, missing = keyword_coverage(set(terms), keywords)
        final = w_similarity * sim + w_coverage * coverage
        results.append({
            "file": path,
            "similarity": sim,
            "coverage": coverage,
            "score": final,
            "matched_keywords": matched,
            "missing_keywords": missing,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results, keywords


def print_report(results, keywords):
    print("=" * 78)
    print("RESUME SCREENING REPORT")
    print("=" * 78)
    print(f"Top JD keywords considered: {', '.join(keywords)}\n")

    for rank, r in enumerate(results, start=1):
        name = os.path.basename(r["file"])
        print(f"#{rank}  {name}")
        print(f"    Overall match score : {r['score']*100:6.2f} / 100")
        print(f"    Text similarity     : {r['similarity']*100:6.2f} / 100")
        print(f"    Keyword coverage    : {r['coverage']*100:6.2f} / 100 "
              f"({len(r['matched_keywords'])}/{len(keywords)} keywords)")
        if r["matched_keywords"]:
            print(f"    Matched keywords    : {', '.join(r['matched_keywords'])}")
        if r["missing_keywords"]:
            print(f"    Missing keywords    : {', '.join(r['missing_keywords'])}")
        print("-" * 78)


def write_csv_report(results, keywords, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "resume_file", "score_percent",
                          "similarity_percent", "coverage_percent",
                          "matched_keywords", "missing_keywords"])
        for rank, r in enumerate(results, start=1):
            writer.writerow([
                rank,
                os.path.basename(r["file"]),
                f"{r['score']*100:.2f}",
                f"{r['similarity']*100:.2f}",
                f"{r['coverage']*100:.2f}",
                "; ".join(r["matched_keywords"]),
                "; ".join(r["missing_keywords"]),
            ])
    print(f"\nCSV report written to: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Screen resumes against a job description using only "
                    "the Python standard library.")
    parser.add_argument("--jd", required=True, help="Path to the job description .txt file")
    parser.add_argument("--resumes", required=True, nargs="+",
                         help="One or more resume .txt files and/or a folder containing them")
    parser.add_argument("--top-keywords", type=int, default=15,
                         help="Number of top JD keywords to check coverage against (default: 15)")
    parser.add_argument("--w-similarity", type=float, default=0.6,
                         help="Weight for cosine similarity in final score (default: 0.6)")
    parser.add_argument("--w-coverage", type=float, default=0.4,
                         help="Weight for keyword coverage in final score (default: 0.4)")
    parser.add_argument("--out", default=None,
                         help="Optional path to write a CSV report")
    args = parser.parse_args()

    results, keywords = score_resumes(
        args.jd, args.resumes,
        top_n_keywords=args.top_keywords,
        w_similarity=args.w_similarity,
        w_coverage=args.w_coverage,
    )
    print_report(results, keywords)
    if args.out:
        write_csv_report(results, keywords, args.out)


if __name__ == "__main__":
    main()

