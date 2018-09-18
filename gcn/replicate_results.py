from __future__ import division
from __future__ import print_function

import time
import tensorflow as tf
from utils import *
from subsample import *
from train import train_model
from output_stats import *
from build_support import get_model_and_support
from settings import *

# Settings
flags = tf.app.flags
FLAGS = flags.FLAGS
settings = graph_settings()['Kipf']
set_tf_flags(settings['params'], flags)

WITH_TEST = settings['with_test']
MAINTAIN_LABEL_BALANCE = settings['maintain_label_balance']
MAX_LABEL_PERCENT = settings['max_label_percent']  # min % to end up with 20 labels per class, as described in the paper

# Verbose settings
SHOW_TEST_VAL_DATASET_STATS = True
VERBOSE_TRAINING = True

# Random seed
seed = settings['seed']
np.random.seed(seed)

# Load data
adj, features, y_train, y_val, y_test, initial_train_mask, val_mask, test_mask = load_data(FLAGS.dataset)
train_mask = get_train_mask(MAX_LABEL_PERCENT, y_train, initial_train_mask, MAINTAIN_LABEL_BALANCE)

# Partitioning check, ensures that no mask overlaps and that there is a label for every input in the maskS.
print_partition_index(train_mask, "Train", y_train)
print_partition_index(val_mask, "Val", y_val)
print_partition_index(test_mask, "Test", y_test)

# Some preprocessing
features = preprocess_features(features)
known_percent = show_data_stats(adj, features, y_train, y_val, y_test, train_mask, val_mask, test_mask,
                                SHOW_TEST_VAL_DATASET_STATS)

model_func, support, sub_sampled_support, num_supports = get_model_and_support(
    settings['classifier'], adj, initial_train_mask, train_mask, val_mask, test_mask, WITH_TEST)
train_model(model_func, num_supports, support, features, y_train, y_val, y_test, train_mask, val_mask, test_mask,
            sub_sampled_support, VERBOSE_TRAINING, settings['seed'])
