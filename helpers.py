import numpy as np
import random
import codecs

random.seed(1)

def batch(inputs, max_sequence_length=None):
    """    
    Args:
        inputs:
            list of sentences in the current batch (integer lists)
        max_sequence_length:
            integer specifying how large should `max_time` dimension be.
            If None, maximum sequence length would be used
    
    Outputs:
        inputs_time_major:
            input sentences transformed into time-major matrix 
            (shape [max_time, batch_size]) padded with 0s
        sequence_lengths:
            batch-sized list of integers specifying amount of active 
            time steps in each input sequence
    """
    
    sequence_lengths = [len(seq) for seq in inputs]
    batch_size = len(inputs)
    
    if max_sequence_length is None:
        max_sequence_length = max(sequence_lengths)
    
    inputs_batch_major = np.zeros(shape=[batch_size, max_sequence_length], dtype=np.int32) # == PAD
    
    for i, seq in enumerate(inputs):
        for j, element in enumerate(seq):
            inputs_batch_major[i, j] = element

    # [batch_size, max_time] -> [max_time, batch_size]
    inputs_time_major = inputs_batch_major.swapaxes(0, 1)

    return inputs_time_major, sequence_lengths


class DataManager:
    def __init__(self, source_file, target_file, vocab_file, batch_size):
        self.num2char = {0: "PAD", 1: "EOS"}
        self.char2num = {}
        with codecs.open(vocab_file, encoding='utf-8') as f:
            count = 1
            for line in f:
                count += 1
                ch = line[0]
                self.num2char[count] = ch
                self.char2num[ch] = count

        with codecs.open(source_file, encoding='utf-8') as f:
            lines = f.readlines()
        source_seqs = [self.num_encode("".join(line.strip().split())) for line in lines]

        with codecs.open(target_file, encoding='utf-8') as f:
            lines = f.readlines()
        dest_seqs = [self.num_encode("".join(line.strip().split())) for line in lines]

        self.data = list(zip(source_seqs, dest_seqs))
        #  truncate to make sure every batch has batch_size entries
        self.data = self.data[:len(self.data) - len(self.data) % batch_size]
        assert len(self.data) % batch_size == 0
        self.batch_size = batch_size
        self.iter = self._make_random_iter()

    def next_batch(self):
        try:
            idxs = next(self.iter)
        except StopIteration:
            self.iter = self._make_random_iter()
            idxs = next(self.iter)
            
        X, Y = zip(*[self.data[i] for i in idxs])
        X = np.array(X).T
        Y = np.array(Y).T
        return X, Y

    def _make_random_iter(self):
        n = len(self.data)
        shuffled_indexes = np.array(range(n))
        random.shuffle(shuffled_indexes)
        batch_indexes = [shuffled_indexes[i:i + self.batch_size] for i in range(0, n, self.batch_size)]
        return iter(batch_indexes)

    def num_decode(self, num_seq):
        return " ".join([self.num2char[k] for k in num_seq])
    
    def num_encode(self, char_seq):
        return [self.char2num[ch] for ch in char_seq]
