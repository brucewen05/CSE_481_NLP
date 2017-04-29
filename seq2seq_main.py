import numpy as np
import tensorflow as tf
from tensorflow.contrib.rnn import LSTMCell, GRUCell, MultiRNNCell

from model_seq2seq import Seq2SeqModel
import pandas as pd
import codecs
import helpers

import warnings
warnings.filterwarnings("ignore")

tf.reset_default_graph()
tf.set_random_seed(1)


def train_on_task(session, model, source_file, target_file, vocab_file,
                  batch_size=32,
                  max_batches=5000,
                  batches_between_evals=100,
                  verbose=True):
    loss_track = []
    data_manager = helpers.DataManager(source_file, target_file, vocab_file, batch_size)

    try:
        for batch_num in range(max_batches+1):
            batch_train_in, batch_train_out = data_manager.next_batch()

            fd = model.make_train_inputs(batch_train_in, batch_train_out)
            _, l = session.run([model.train_op, model.loss], fd)
            loss_track.append(l)

            if verbose:
                if batch_num % batches_between_evals == 0:
                    print('batch #{}'.format(batch_num))
                    
                    print('  minibatch loss: {}'.format(session.run(model.loss, fd)))
                    for i, (e_in, dt_pred) in enumerate(zip(
                            fd[model.encoder_inputs].T,
                            session.run(model.decoder_prediction_train, fd).T
                        )):
                        print('  sample {}:'.format(i + 1))
                        print('    enc input           > {}'.format(data_manager.num_decode(e_in)))
                        print('    dec train predicted > {}'.format(data_manager.num_decode(dt_pred)))
                        if i >= 2:
                            break
                    print()
                    # TODO: validation loss and samples
                    # TODO: save to disk
    except KeyboardInterrupt:
        print('training interrupted')

    return loss_track


with tf.Session() as session:

    source_file = "data/train/sms_large.source"
    target_file = "data/train/sms_large.target"
    vocab_file = "data/vocab/sms"

    with codecs.open(vocab_file, encoding='utf-8') as f:
        lines = f.readlines()
    vocab_size = len(lines) + 2  # EOS and PAD

    # with bidirectional encoder, decoder state size should be
    # 2x encoder state size
    # TODO: Add dropout
    model = Seq2SeqModel(encoder_cell=MultiRNNCell([GRUCell(256), GRUCell(256)]),
                         decoder_cell=MultiRNNCell([GRUCell(256), GRUCell(256)]), 
                         vocab_size=vocab_size,
                         embedding_size=256,
                         attention=True,
                         bidirectional=True,
                         debug=False)

    session.run(tf.global_variables_initializer())

    train_on_task(session, model, source_file, target_file, vocab_file)