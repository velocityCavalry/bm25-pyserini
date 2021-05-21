RESET_OPT=0
while getopts ":l:" opt; do
    case ${opt} in
        l ) LANGUAGE=$OPTARG;;
    esac
done

python -m wikiextractor.WikiExtractor /gscratch/cse/datasets/wikidump/${LANGUAGE}wiki-20190201-pages-articles-multistream.xml.bz2 \
--json -o /gscratch/cse/datasets/wikidump/${LANGUAGE}-wiki-dump -b 100M;
echo "finish dumping";


cd /gscratch/cse/xyu530/bm25_pyserini/;
mkdir /gscratch/cse/datasets/wikidump/${LANGUAGE}-wiki-edit;
# change jsonl files' field from text to contents
python edit_json_file.py --input-dir /gscratch/cse/datasets/wikidump/${LANGUAGE}-wiki-dump/AA --output-dir /gscratch/cse/datasets/wikidump/${LANGUAGE}-wiki-edit;
cd /gscratch/cse/datasets/wikidump/${LANGUAGE}-wiki-edit/;
for f in wiki_*; do
  mv -- "$f" "$f.jsonl";
done
echo "finish trimming the paragraphs";

#index the jsonl files
cd /gscratch/scrubbed/xyu530/pyserini/;
python -m pyserini.index -collection JsonCollection -language ${LANGUAGE} -generator DefaultLuceneDocumentGenerator -threads 8  \
-input /gscratch/cse/datasets/wikidump/${LANGUAGE}-wiki-edit -index indexes/${LANGUAGE}wiki-collection-jsonl -storePositions \
 -storeDocvectors -storeRaw;
echo "finish indexing the wiki";

export PYTHONPATH=$(pwd); # in pyserini directory
python /gscratch/cse/xyu530/bm25_pyserini/search_index.py --index-path indexes/${LANGUAGE}wiki-collection-jsonl --query-path /gscratch/cse/xyu530/mkqa.jsonl.gz --output work_dir/${LANGUAGE}-output.json --lang ${LANGUAGE};
echo "finish all"