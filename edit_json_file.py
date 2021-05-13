import json
import os
import argparse

def read_and_change_json(input_file, output_file):

    res = []
    with open(input_file, 'r+', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            single = json.loads(line)
            edit = {"id": single["id"], "revid": single["revid"], "url": single["url"], "title": single["title"],
                    "contents": single["text"]}
            res.append(edit)

    with open(output_file, 'w+', encoding='utf-8') as f:
        for single in res:
            json.dump(single, f)
            f.write('\n')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True, help='The path to the input dir that contains jsonl file')
    parser.add_argument('--output-dir', required=True, help='The path to the output dir that contains jsonl file')
    args = parser.parse_args()
    for file in os.listdir(args.input_dir):
        if file.startswith('wiki'):
            input_filepath = os.path.join(args.input_dir, file)
            output_filepath = os.path.join(args.output_dir, file)
            read_and_change_json(input_filepath, output_filepath)


if __name__ == '__main__':
    main()