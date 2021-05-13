
# change jsonl files' field from text to contents
python edit_json_file.py --input-dir ../ja-wiki-dump/AA --output-dir ../ja-wiki-edit

#index the jsonl files
python -m pyserini.index -collection JsonCollection -generator DefaultLuceneDocumentGenerator -threads 8  \
-input /gscratch/cse/xyu530/ja-wiki-edit -index indexes/jawiki-collection-jsonl -storePositions \
 -storeDocvectors -storeRaw

export PYTHONPATH=$(pwd) # in pyserini directory
python /gscratch/cse/xyu530/bm25_pyserini/search_index.py --index-path indexes/jawiki-collection-jsonl --query-path
/gscratch/cse/xyu530/mkqa.jsonl.gz --output work_dir/ja-test-output.jsonl --lang ja