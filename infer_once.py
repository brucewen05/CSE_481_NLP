from pydoc import locate
import tensorflow as tf
import numpy as np
from seq2seq import tasks, models
from seq2seq.training import utils as training_utils
from seq2seq.tasks.inference_task import InferenceTask, unbatch_dict

class DecodeOnce(InferenceTask):

  def __init__(self, params):
    super(DecodeOnce, self).__init__(params)
  
  @staticmethod
  def default_params():
    params = {}
    params.update({"delimiter": " "})
    return params

  def before_run(self, _run_context):
    fetches = {}
    fetches["predicted_tokens"] = self._predictions["predicted_tokens"]
    fetches["features.source_len"] = self._predictions["features.source_len"]
    fetches["features.source_tokens"] = self._predictions["features.source_tokens"]
    return tf.train.SessionRunArgs(fetches)

  def after_run(self, _run_context, run_values):
    fetches_batch = run_values.results
    for fetches in unbatch_dict(fetches_batch):
      # Convert to unicode
      fetches["predicted_tokens"] = np.char.decode(
          fetches["predicted_tokens"].astype("S"), "utf-8")
      predicted_tokens = fetches["predicted_tokens"]

      # If we're using beam search we take the first beam
      if np.ndim(predicted_tokens) > 1:
        predicted_tokens = predicted_tokens[:, 0]

      fetches["features.source_tokens"] = np.char.decode(
          fetches["features.source_tokens"].astype("S"), "utf-8")
      source_tokens = fetches["features.source_tokens"]
      source_len = fetches["features.source_len"]

      sent = self.params["delimiter"].join(predicted_tokens)
      print(sent)

      _run_context.request_stop()



if __name__ == "__main__":
  tf.logging.set_verbosity(tf.logging.INFO)

  MODEL_DIR = "model/sms_large"

  # Load saved training options
  train_options = training_utils.TrainOptions.load(MODEL_DIR)

  # Create the model
  model_cls = locate(train_options.model_class) or \
    getattr(models, train_options.model_class)
  model_params = train_options.model_params

  model = model_cls(
      params=model_params,
      mode=tf.contrib.learn.ModeKeys.INFER)

  source_tokens = u"^ 在 那 呢 ？ | w o d a o q i a o".split()

  predictions, _, _ = model(
      features={
        "source_tokens": tf.constant([source_tokens]),
        "source_len": tf.constant([len(source_tokens)])
      },
      labels=None,
      params={
        "vocab_source": "data/vocab/sms",
        "vocab_target": "data/vocab/sms"
      }
    )

  saver = tf.train.Saver()
  # checkpoint_path = FLAGS.checkpoint_path
  # if not checkpoint_path:
  checkpoint_path = tf.train.latest_checkpoint(MODEL_DIR)

  def session_init_op(_scaffold, sess):
    saver.restore(sess, checkpoint_path)
    tf.logging.info("Restored model from %s", checkpoint_path)

  scaffold = tf.train.Scaffold(init_fn=session_init_op)
  session_creator = tf.train.ChiefSessionCreator(scaffold=scaffold)
  with tf.train.MonitoredSession(
      session_creator=session_creator, hooks=[DecodeOnce({})]) as sess:

    while not sess.should_stop():
      sess.run([])
