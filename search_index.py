from pyserini.search import SimpleSearcher
from pyserini.index import IndexReader
from pyserini import analysis
import argparse
import json
from gzip import GzipFile
from tqdm import tqdm

# hu, da, it, fi, ru, nl, no, pt, th, tr, sv
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
    q2idan = dict()
    with GzipFile(fileobj=open(file, 'rb')) as f:
        for line in f:
            line = line.decode('utf-8')
            example = json.loads(line)
            question = example["queries"][lang]
            answers = []
            for answer in example["answers"][lang]:
                answer_item = dict()
                answer_item["text"] = answer["text"]
                answer_item["answer_start"] = -1
                answers.append(answer_item)
                if "aliases" in answer:
                    for alias in answer["aliases"]:
                        answer_item = dict()
                        answer_item["text"] = alias
                        answer_item["answer_start"] = -1
                        answers.append(answer_item)
            id = example["example_id"]
            if question in q2idan:
                print(f'prev question: {question}, prev id:{q2idan[question][0]}, curr id: {id}\n')
            q2idan[question] = (id, answers)
    return q2idan


def search_indexes(searcher, query, id, answers):
    # index_reader = IndexReader(index_path)
    hits = searcher.search(query, k=10)
    paragraphs = []
    for i in range(len(hits)):
        qas = dict()
        qas['qas'] = [{"id": id, "question": query, "answers": answers}]
        qas["context"] = json.loads(hits[i].raw)['contents']
        # index_reader.compute_query_document_score(docid, query)
        qas["bm25_scores"] = hits[i].score
        paragraphs.append(qas)
    return paragraphs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index-path', required=True, type=str, help='the path to the wikipedia index')
    parser.add_argument('--query-path', required=True, type=str, help='the path to the mkqa question file')
    parser.add_argument('--output', required=True, type=str, help='the path to the output jsonl file')
    parser.add_argument('--lang', required=True, help='the language')
    parser.add_argument('--k1', default=0.82, help='the k1 in bm25')
    parser.add_argument('--b', default=0.68, help='the b in bm25')
    args = parser.parse_args()

    # if args.lang == 'zh':
    #     args.lang = 'zh_cn'

    q2id = return_q2id_answer(args.query_path, args.lang)
    searcher = SimpleSearcher(args.index_path)
    if args.lang == 'ar':
        analyzer = analysis.get_lucene_analyzer(name="Arabic")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'de':
        analyzer = analysis.get_lucene_analyzer(name="German")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'fr':
        analyzer = analysis.get_lucene_analyzer(name="French")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'es':
        analyzer = analysis.get_lucene_analyzer(name="Spanish")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'it':
        analyzer = analysis.get_lucene_analyzer(name="Italian")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'ru':
        analyzer = analysis.get_lucene_analyzer(name="Russian")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'sv':
        analyzer = analysis.get_lucene_analyzer(name="Swedish")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'no':
        analyzer = analysis.get_lucene_analyzer(name="Norwegian")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'nl':
        analyzer = analysis.get_lucene_analyzer(name="Dutch")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'tr':
        analyzer = analysis.get_lucene_analyzer(name="Turkish")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'th':
        analyzer = analysis.get_lucene_analyzer(name="Thai")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'pt':
        analyzer = analysis.get_lucene_analyzer(name="Portuguese")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'fi':
        analyzer = analysis.get_lucene_analyzer(name="Finnish")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'da':
        analyzer = analysis.get_lucene_analyzer(name="Danish")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'hu':
        analyzer = analysis.get_lucene_analyzer(name="Hungarian")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'id':
        analyzer = analysis.get_lucene_analyzer(name="Indonesian")
        searcher.set_analyzer(analyzer)
    elif args.lang == 'zh_cn' or args.lang == 'zh_tw' or args.lang == 'ja' or args.lang == 'ko':
        analyzer = analysis.get_lucene_analyzer(name="CJK")
        searcher.set_analyzer(analyzer)

    searcher.set_bm25(args.k1, args.b)


    with open(args.output, 'w+', encoding='utf-8') as fw:
        squad_formatted_content = dict()
        squad_formatted_content["version"] = f"{args.lang}-bm25"
        data = []
        for i, query in enumerate(tqdm(q2id)):
            data_element = dict()
            data_element['title'] = str(i)  # dummy
            id, answers = q2id[query]
            data_element['paragraphs'] = search_indexes(searcher, query, id, answers)
            data.append(data_element)
        squad_formatted_content["data"] = data
        json.dump(squad_formatted_content, fw, ensure_ascii=False)
        fw.flush()


if __name__ == '__main__':
    main()















