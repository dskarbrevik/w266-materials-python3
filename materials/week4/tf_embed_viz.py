import sys, os

import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector

def mkdirp(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

class TFEmbeddingVizWrapper(object):
    """Wrapper class to handle vizualizing an embedding matrix with TensorBoard.

    Based on https://www.tensorflow.org/how_tos/embedding_viz/, but attempting 
    to hide some of the boilerplate involved in setting up a graph, session, 
    checkpoints, etc.
    """

    def __init__(self, LOGDIR="tf_embedding_viz"):
        mkdirp(LOGDIR)

        self.LOGDIR = LOGDIR
        self.VOCAB_FILE = os.path.join(LOGDIR, "metadata.tsv")
        self.CHECKPOINT_FILE = os.path.join(LOGDIR, "model.ckpt")

    def write_vocab_file(self, words):
        """Write a vocab list to a file.
        
        Args:
          words: (list of string)
        """
        with open(self.VOCAB_FILE, 'w') as fd:
            for word in words:
                fd.write(word + "\n")
        print ("Vocabulary (%d words) written to '%s'" % (len(words), 
                self.VOCAB_FILE))

    def write_embeddings(self, Wv, name="WordVectors"):
        """Write embedding matrix to the right place.
        
        Args:
          Wv: (numpy.ndarray) |V| x d matrix of word embeddings
        """
    with tf.Graph().as_default(), tf.Session() as session:

        # Feed embeddings to tf, and save.
        embedding_var = tf.Variable(Wv, name=name, dtype=tf.float32)
        session.run(tf.global_variables_initializer())

        saver = tf.train.Saver() 
        saver.save(session, self.CHECKPOINT_FILE, 0)

        # Save metadata
        summary_writer = tf.summary.FileWriter(self.LOGDIR)
        config = projector.ProjectorConfig()
        embedding = config.embeddings.add()
        embedding.tensor_name = embedding_var.name
        embedding.metadata_path = self.VOCAB_FILE
        projector.visualize_embeddings(summary_writer, config)

        msg = "Saved {s0:d} x {s1:d} embedding matrix '{name}'"
        msg += " to LOGDIR='{logdir}'"
        print (msg.format(s0=Wv.shape[0], s1=Wv.shape[1], name=name, 
                logdir=self.LOGDIR))

        print ("To view, run:")
        print ("\n  tensorboard --logdir=\"{logdir}\"\n".format(logdir=self.LOGDIR))
        print ("and navigate to the \"Embeddings\" tab in the web interface.")


