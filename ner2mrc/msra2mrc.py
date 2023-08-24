#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# file: msra2mrc.py

import os
from bmes_decode import bos_decode
import json


def convert_file(input_file, output_file, tag2query_file):
    """
    Convert MSRA raw data to MRC format
    """
    origin_count = 0
    new_count = 1
    tag2query = json.load(open(tag2query_file))
    mrc_samples = []
    contexts, labels = [], []
    with open(input_file) as fin:
        for line in fin:
            line = line.strip()
            if line:
                context, label = line.split("\t")
                contexts.append(context)
                labels.append(label)
            else:
                tags = bos_decode(
                    char_label_list=[
                        (char, label) for char, label in zip(contexts, labels)
                    ]
                )

                #         tags = bmes_decode(char_label_list=[(char, label) for char, label in zip(src.split(), labels.split())])
                for label, query in tag2query.items():
                    start_position = [tag.begin for tag in tags if tag.tag == label]
                    end_position = [tag.end - 1 for tag in tags if tag.tag == label]
                    mrc_samples.append(
                        {
                            "qas_id": "{}.{}".format(origin_count, new_count),
                            "context": " ".join(contexts),
                            "start_position": start_position,
                            "end_position": end_position,
                            "query": query,
                            "impossible": False
                            if start_position and end_position
                            else True,
                            "entity_label": label,
                            "span_position": [
                                f"{start};{end}"
                                for start, end in zip(start_position, end_position)
                            ],
                        }
                    )
                    new_count += 1

                contexts, labels = [], []
                origin_count += 1
                new_count = 1
        if len(contexts) > 0:
            tags = bos_decode(
                char_label_list=[
                    (char, label) for char, label in zip(contexts, labels)
                ]
            )
            for label, query in tag2query.items():
                start_position = [tag.begin for tag in tags if tag.tag == label]
                end_position = [tag.end - 1 for tag in tags if tag.tag == label]
                mrc_samples.append(
                    {
                        "qas_id": "{}.{}".format(origin_count, new_count),
                        "context": " ".join(contexts),
                        "start_position": start_position,
                        "end_position": end_position,
                        "query": query,
                        "impossible": False
                        if start_position and end_position
                        else True,
                        "entity_label": label,
                        "span_position": [
                            f"{start};{end}"
                            for start, end in zip(start_position, end_position)
                        ],
                    }
                )
                new_count += 1

    json.dump(
        mrc_samples,
        open(output_file, "w"),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )


def main():
    msra_raw_dir = "ner2mrc/vlsp2016"
    msra_mrc_dir = "ner2mrc/vlsp2016/mrc_format"
    tag2query_file = "ner2mrc/vlsp2016/queries.json"
    os.makedirs(msra_mrc_dir, exist_ok=True)
    for phase in ["train", "dev", "test"]:
        old_file = os.path.join(msra_raw_dir, f"{phase}.txt")
        new_file = os.path.join(msra_mrc_dir, f"mrc-ner.{phase}")
        convert_file(old_file, new_file, tag2query_file)


if __name__ == "__main__":
    main()
