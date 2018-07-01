#!/usr/bin/env python
# coding: utf8
"""Export spaCy model vectors for use in TensorBoard's standalone embedding projector.
https://github.com/tensorflow/embedding-projector-standalone

Usage:

 python vectors_tensorboard_standalone.py ./myVectorModel ./output [name]

This outputs two files that have to be copied into the "oss_data" of the standalone projector:

 [name]_labels.tsv - metadata such as human readable labels for vectors
 [name]_tensors.bytes - numpy.ndarray of numpy.float32 precision vectors

"""
from __future__ import unicode_literals

import json
import math
from os import path

import numpy
import plac
import spacy
import tqdm


@plac.annotations(
    vectors_loc=("Path to spaCy model that contains vectors", "positional", None, str),
    out_loc=("Path to output folder writing tensors and labels data", "positional", None, str),
    name=("Human readable name for tsv file and vectors tensor", "positional", None, str),
)
def main(vectors_loc, out_loc, name="spaCy_vectors"):
    # A tab-separated file that contains information about the vectors for visualization
    #
    # Learn more: https://www.tensorflow.org/programmers_guide/embedding#metadata
    meta_file = "{}_labels.tsv".format(name)
    out_meta_file = path.join(out_loc, meta_file)

    print('Loading spaCy vectors model: {}'.format(vectors_loc))
    model = spacy.load(vectors_loc)

    print('Finding lexemes with vectors attached: {}'.format(vectors_loc))
    voacb_strings = [
        w for w in tqdm.tqdm(model.vocab.strings, total=len(model.vocab.strings), leave=False)
        if model.vocab.has_vector(w)
    ]
    vector_count = len(voacb_strings)

    print('Building Projector labels for {} vectors: {}'.format(vector_count, out_meta_file))
    vector_dimensions = model.vocab.vectors.shape[1]
    tf_vectors_variable = numpy.zeros((vector_count, vector_dimensions), dtype=numpy.float32)

    # Write a tab-separated file that contains information about the vectors for visualization
    #
    # Reference: https://www.tensorflow.org/programmers_guide/embedding#metadata
    with open(out_meta_file, 'wb') as file_metadata:
        # Define columns in the first row
        file_metadata.write("Text\tFrequency\n".encode('utf-8'))
        # Write out a row for each vector that we add to the tensorflow variable we created
        vec_index = 0

        for text in tqdm.tqdm(voacb_strings, total=len(voacb_strings), leave=False):
            # https://github.com/tensorflow/tensorflow/issues/9094
            text = '<Space>' if text.lstrip() == '' else text
            lex = model.vocab[text]

            # Store vector data and metadata
            tf_vectors_variable[vec_index] = numpy.float64(model.vocab.get_vector(text))
            file_metadata.write("{}\t{}\n".format(text, math.exp(lex.prob) * len(voacb_strings)).encode('utf-8'))
            vec_index += 1

    # Write out "[name]_tensors.bytes" file for standalone embeddings projector to load
    tensor_path = '{}_tensors.bytes'.format(name)
    tf_vectors_variable.tofile(path.join(out_loc, tensor_path))

    print('Done.')
    print('Add the following entry to "oss_data/oss_demo_projector_config.json"')
    print(json.dumps({
        "tensorName": name,
        "tensorShape": [vector_count, vector_dimensions],
        "tensorPath": 'oss_data/{}'.format(tensor_path),
        "metadataPath": 'oss_data/{}'.format(meta_file)
    }, indent=2))


if __name__ == '__main__':
    plac.call(main)
