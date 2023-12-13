from pymongo import MongoClient
from argparse import ArgumentParser
import json
from bson import json_util


def parse_json(data):
    return json.loads(json_util.dumps(data))


def export_to_jsonl(db_name, collection_name=None):
    client = MongoClient()
    db = client[db_name]

    # If collection_name is not specified, export all collections.
    if collection_name is None:
        collections = db.list_collection_names()
    else:
        collections = [collection_name]

    # Export all collections into to a single json file.
    with open(f'{db_name}.jsonl', 'w', encoding='utf-8') as f:
        for collection_name in collections:
            collection = db[collection_name]
            for document in collection.find():
                f.write(json.dumps(parse_json(document), ensure_ascii=False))
                f.write('\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-d', '--db', help='Database Name', default='大众点评')
    parser.add_argument('-c', '--collection', help='Collection Name', default=None)
    args = parser.parse_args()
    export_to_jsonl(args.db, args.collection)
