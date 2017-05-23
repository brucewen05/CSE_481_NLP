from pydoc import locate
import tensorflow as tf
import numpy as np
from seq2seq import tasks, models
from seq2seq.training import utils as training_utils
from seq2seq.tasks.inference_task import InferenceTask, unbatch_dict
import pprint
import logging
import eval as ev

class DecodeOnce(InferenceTask):
  '''
  Similar to tasks.DecodeText, but for one input only.
  Source fed via features.source_tokens and features.source_len
  '''
  def __init__(self, params, callback_func):
    super(DecodeOnce, self).__init__(params)
    self.callback_func=callback_func
    self._beam_accum = {
      "predicted_ids": [],
      "beam_parent_ids": [],
      "scores": [],
      "log_probs": []
    }
    self.top_k = 10
  
  @staticmethod
  def default_params():
    return {}

  def before_run(self, _run_context):
    fetches = {}
    fetches["predicted_tokens"] = self._predictions["predicted_tokens"]
    fetches["features.source_tokens"] = self._predictions["features.source_tokens"]
    fetches["beam_search_output.predicted_ids"] = self._predictions["beam_search_output.predicted_ids"]
    fetches["beam_search_output.beam_parent_ids"] = self._predictions["beam_search_output.beam_parent_ids"]
    fetches["beam_search_output.scores"] = self._predictions["beam_search_output.scores"]
    fetches["beam_search_output.log_probs"] = self._predictions["beam_search_output.log_probs"]
    return tf.train.SessionRunArgs(fetches)

  def after_run(self, _run_context, run_values):
    fetches_batch = run_values.results
    for fetches in unbatch_dict(fetches_batch):
      # Convert to unicode
      fetches["predicted_tokens"] = np.char.decode(
      fetches["predicted_tokens"].astype("S"), "utf-8")
      predicted_tokens = fetches["predicted_tokens"]

      #self._beam_accum["predicted_ids"].append(fetches["beam_search_output.predicted_ids"])
      #self._beam_accum["beam_parent_ids"].append(fetches["beam_search_output.beam_parent_ids"])
      #self._beam_accum["scores"].append(fetches["beam_search_output.scores"])
      #self._beam_accum["log_probs"].append(fetches["beam_search_output.log_probs"])

      self._beam_accum["predicted_ids"] = [fetches["beam_search_output.predicted_ids"]]
      self._beam_accum["beam_parent_ids"] = [fetches["beam_search_output.beam_parent_ids"]]
      self._beam_accum["scores"] = [fetches["beam_search_output.scores"]]
      self._beam_accum["log_probs"] = [fetches["beam_search_output.log_probs"]]

 #     print("\n\n")
#      print(self._beam_accum)
      #print(predicted_tokens)
#      print("\n\n")
      
      def beam_search_traceback(i, cur_id):
        if i == 0: return np.array([])
        else:
          cur_prediction = predicted_tokens[i-1:i,cur_id]
          parent_id = self._beam_accum["beam_parent_ids"][0][i-1][cur_id]
          return np.append(beam_search_traceback(i-1, parent_id), cur_prediction)

      # If we're using beam search we take the first beam
      # TODO: beam search top k
      if np.ndim(predicted_tokens) > 1:
        #predicted_tokens = predicted_tokens[:, 0]
        try:
          beam_search_predicted_tokens = []
          seq_len = predicted_tokens.shape[0]
          beam_width = predicted_tokens.shape[1]

          for length in range(seq_len, 0, -1):
            for k in range(0, beam_width):
              parent_id = self._beam_accum["beam_parent_ids"][0][length - 1][k]
              log_prob = self._beam_accum["log_probs"][0][length - 1][k]
              #parent_log_prob = self._beam_accum["log_probs"][0][length - 2][parent_id]
              bigram_score = 0
              char_cur = predicted_tokens[length-1, k]
              char_prev = predicted_tokens[length - 2, parent_id]
              if char_cur == "SEQUENCE_END":
                char_cur = "^"
              else:
                char_cur = char_cur[0]
              if char_prev == "SEQUENCE_END":
                char_prev = "^"
              else:
                char_prev = char_prev[len(char_prev) - 1]
              try:
                bigram_score = (ev.bigram_dict[(char_prev, char_cur)]+1) / float(ev.unigram_dict[(char_prev)] + len(ev.dictionary.keys()))
              except KeyError:
                bigram_score = 1 / float(len(ev.dictionary.keys()))
              self._beam_accum["scores"][0][length - 1][k] = log_prob + 5 * bigram_score
              
          #print(self._beam_accum["beam_parent_ids"])    
          #print(self._beam_accum["log_probs"])
          #print(self._beam_accum["scores"])
        
          for length in range(0, seq_len-1):
           #print(np.argsort(self._beam_accum["scores"][0][length])[::-1][:beam_width])
           pass
         
          for length in range(1, seq_len):
            prediction_per_len = []
            for k in range(0, min(beam_width, self.top_k)):
              pred_tokens_k  = beam_search_traceback(length, k)
              prob_pred_token_k = self._beam_accum["scores"][0][length-1][k]
              if not _arreq_in_list(pred_tokens_k, prediction_per_len):
                prediction_per_len.append((pred_tokens_k, prob_pred_token_k))
            prediction_per_len = sorted(prediction_per_len, key=lambda x: x[1], reverse=True)[:beam_width]
            beam_search_predicted_tokens.append(prediction_per_len)
          predicted_tokens = beam_search_predicted_tokens
        except IndexError as e:
          logging.exception("")
          print(self._beam_accum)
          print(predicted_tokens)
          predicted_tokens = []
          print("parents dim", np.ndim(self._beam_accum["beam_parent_ids"]))
          print("predicted tokends dim", np.ndim(predicted_tokens))
      
      fetches["features.source_tokens"] = np.char.decode(
          fetches["features.source_tokens"].astype("S"), "utf-8")
      source_tokens = fetches["features.source_tokens"]
      
      self.callback_func(source_tokens, predicted_tokens)


# TODO: pass via args
MODEL_DIR = "/data/model/mixed_abbrs_05_07"
checkpoint_path = tf.train.latest_checkpoint(MODEL_DIR)

# Load saved training options
train_options = training_utils.TrainOptions.load(MODEL_DIR)

# Create the model
model_cls = locate(train_options.model_class) or \
  getattr(models, train_options.model_class)
model_params = train_options.model_params

model_params["inference.beam_search.beam_width"] = 10

model = model_cls(
    params=model_params,
    mode=tf.contrib.learn.ModeKeys.INFER)


# first dim is batch size
source_tokens_ph = tf.placeholder(dtype=tf.string, shape=(1, None))
source_len_ph = tf.placeholder(dtype=tf.int32, shape=(1,))

model(
  features={
    "source_tokens": source_tokens_ph,
    "source_len": source_len_ph
  },
  labels=None,
  params={
    "vocab_source": "/data/vocab/mixed_abbrs",
    "vocab_target": "/data/vocab/mixed_abbrs"
  }
)

saver = tf.train.Saver()

def _session_init_op(_scaffold, sess):
  saver.restore(sess, checkpoint_path)
  tf.logging.info("Restored model from %s", checkpoint_path)

scaffold = tf.train.Scaffold(init_fn=_session_init_op)
session_creator = tf.train.ChiefSessionCreator(scaffold=scaffold)


def _tokens_to_str(tokens):
  return " ".join(tokens).split("SEQUENCE_END")[0].strip()

# A hacky way to retrieve prediction result from the task hook...
prediction_dict = {}
def _save_prediction_to_dict(source_tokens, predicted_tokens):
  prediction_dict[_tokens_to_str(source_tokens)] = [[(_tokens_to_str(predicted_token[0]), predicted_token[1]) for predicted_token in predicted_tokens_len] for predicted_tokens_len in predicted_tokens]

def _arreq_in_list(target_ndarray, list_ndarrays):
      return next((True for elem in list_ndarrays if np.array_equal(elem[0], target_ndarray)), False)
    
sess = tf.train.MonitoredSession(
  session_creator=session_creator,
  hooks=[DecodeOnce({}, callback_func=_save_prediction_to_dict)])

# The main APIs exposed
def query_once(source_tokens):
  #print("received source tokens:", source_tokens)
  tf.reset_default_graph()
  source_tokens = source_tokens.split() + ["SEQUENCE_END"]
  sess.run([], {
      source_tokens_ph: [source_tokens],
      source_len_ph: [len(source_tokens)]
    })
  
  predictions_list = prediction_dict.pop(_tokens_to_str(source_tokens))
  return predictions_list
  #print("all result:")
  #print(predictions_list)
  #result = sort_and_merge_predictions(predictions_list)
  #print("result to be returned:")
  #print(result)
  #return result

def sort_and_merge_predictions(predictions_list, max_items=10, cutoff=3):
    flat_list = []
    num_keep = 1
    for sublist in reversed(predictions_list):
      ranked_sublist = sorted(sublist, key=lambda x: x[1], reverse=True)[:num_keep]
      num_keep = num_keep + 1
      if (num_keep > cutoff):
        num_keep = cutoff
      for t in ranked_sublist:
        flat_list.append((t[0].replace(" ", ""), t[1]))
    print("flat list before sorting:")
    print(flat_list)
    ranked = sorted(flat_list, key=lambda x: x[1] / len(x[0]), reverse=True)[:max_items]
    #print("after sorting:")
    #print(ranked)
    return ranked #[x[0] for x in ranked]

def query(context, pinyins):
  # TODO: do not hard code window size here
  context = " ".join(list(context)[-10:])
  pinyins = " ".join(list("".join(pinyins)))
  #print("------------", context + " | " + pinyins)
  return query_once(context + " | " + pinyins)
      
if __name__ == "__main__":
  tf.logging.set_verbosity(tf.logging.INFO)
  # current prediction time ~20ms
  #unigram_dict, bigram_dict, dictionary = ng.load_model("model/ngrams_model")
  samples = [
     u"^ 下 班 | h o u y i q i c h i f a n",
     u"^ … 还 以 为 你 关 机 | s h u i z h a o l e",
     u"^ 你 带 钥 匙 | m e i y o u a",
     u"^ 我 妹 妹 | t a",
     u"^ 我 弟 弟 | t a",
     u"^ 我 妈 妈 现 在 在 家 , | t a",
     u"^ 我 爸 爸 现 在 在 家 , | t a",
     u"^ 我 叫 | w e n q i n g d a"
  ]
  for sample_in in samples:
     pprint.pprint(sample_in)
     print(query_once(sample_in))
     print()
  # query("^", "w")
  # query("^", "wo")
  # query("^我", "j")
  # query("^我", "ji")
  # query("^我", "jia")
  # query("^我", "jiao")
  # query(u"^我叫", "w")
  # query(u"^我叫", "we")
  # query(u"^我叫", "wen")
  # query(u"^我叫", "wenq")
  # query(u"^我叫", "wenqi")
  # query(u"^我叫", "wenqin")
  # query(u"^我叫", "wenqing")
  # query(u"^我叫", "wenqingd")
  #query(u"^我叫", "wenqingda")
  #query(u"^下班", "houyiqichifan")
