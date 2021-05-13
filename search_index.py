from pyserini.search import SimpleSearcher
from pyserini.index import IndexReader
import argparse
import json
from gzip import GzipFile
from tqdm import tqdm
#
# searcher = SimpleSearcher('indexes/jawiki-collection-jsonl')
# index_reader = IndexReader('indexes/jawiki-collection-jsonl')
# hits = searcher.search('ラムズはいつスーパーボウルでプレーしましたか')
#
# for i in range(len(hits)):
#     print(f'{i + 1:2} {hits[i].docid:15} {hits[i].score:.5f}')
#     print(hits[i].raw)

# export PYTHONPATH=$(pwd)

def return_q2id_answer(file, lang):
    q2idan = {}
    with GzipFile(fileobj=open(file, 'rb')) as f:
        for line in f:
            line = line.decode('utf-8')
            example = json.loads(line)
            question = example["queries"][lang]
            answer = example["answers"][lang]
            id = example["example_id"]
            if question in q2idan:
                print(f'prev question: {question}, prev id:{q2idan[question][0]}, curr id: {id}\n')
            q2idan[question] = (id, answer)
    return q2idan


def search_indexes(searcher, query, id, answers, fp):
    # index_reader = IndexReader(index_path)
    hits = searcher.search(query, k=10)
    for i in range(len(hits)):
        single = {"id": id, "question": query, "answers": answers}
        single["contents"] = json.loads(hits[i].raw)['contents']
        # index_reader.compute_query_document_score(docid, query)
        single["bm25_scores"] = hits[i].score
        json.dump(single, fp, ensure_ascii=False)
        fp.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index-path', required=True, type=str, help='the path to the wikipedia index')
    parser.add_argument('--query-path', required=True, type=str, help='the path to the mkqa question file')
    parser.add_argument('--output', required=True, type=str, help='the path to the output jsonl file')
    parser.add_argument('--lang', required=True, help='the language')
    parser.add_argument('--k1', default=0.82, help='the k1 in bm25')
    parser.add_argument('--b', default=0.68, help='the b in bm25')
    args = parser.parse_args()

    q2id = return_q2id_answer(args.query_path, 'ja')
    searcher = SimpleSearcher(args.index_path)
    searcher.set_bm25(args.k1, args.b)

    with open(args.output, 'w+', encoding='utf-8') as fw:
        for i, query in enumerate(tqdm(q2id)):
            id, answer = q2id[query]
            search_indexes(searcher, query, id, answer, fw)
        fw.flush()


if __name__ == '__main__':
    main()















