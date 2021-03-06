# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Layer serialization/deserialization functions.
"""
# pylint: disable=wildcard-import
# pylint: disable=unused-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python import tf2
from tensorflow.python.keras.engine.base_layer import TensorFlowOpLayer
from tensorflow.python.keras.engine.input_layer import Input
from tensorflow.python.keras.engine.input_layer import InputLayer
from tensorflow.python.keras.layers.advanced_activations import *
from tensorflow.python.keras.layers.convolutional import *
from tensorflow.python.keras.layers.convolutional_recurrent import *
from tensorflow.python.keras.layers.core import *
from tensorflow.python.keras.layers.cudnn_recurrent import *
from tensorflow.python.keras.layers.embeddings import *
from tensorflow.python.keras.layers.local import *
from tensorflow.python.keras.layers.merge import *
from tensorflow.python.keras.layers.noise import *
from tensorflow.python.keras.layers.normalization import *
from tensorflow.python.keras.layers.pooling import *
from tensorflow.python.keras.layers.recurrent import *
from tensorflow.python.keras.layers.wrappers import *
from tensorflow.python.keras.utils.generic_utils import deserialize_keras_object
from tensorflow.python.util.tf_export import keras_export

# TODO(b/124791387): replace mapping with layer attribute.
# Name conversion between class name and API symbol in config.
_SERIALIZATION_TABLE = {
    'BatchNormalizationV1': 'BatchNormalization',
    'BatchNormalizationV2': 'BatchNormalization',
    'UnifiedLSTM': 'LSTM',
    'UnifiedGRU': 'GRU',
}

# Name conversion between API symbol in config and class name.
# Note that the class names is a list where the first item is v1 class name and
# the second item is the v2 class name.
_DESERIALIZATION_TABLE = {
    'LSTM': {'v1': 'LSTM', 'v2': 'UnifiedLSTM'},
    'GRU': {'v1': 'GRU', 'v2': 'UnifiedGRU'},
}


@keras_export('keras.layers.serialize')
def serialize(layer):
  layer_class_name = layer.__class__.__name__
  if layer_class_name in _SERIALIZATION_TABLE:
    layer_class_name = _SERIALIZATION_TABLE[layer_class_name]
  return {'class_name': layer_class_name, 'config': layer.get_config()}


@keras_export('keras.layers.deserialize')
def deserialize(config, custom_objects=None):
  """Instantiates a layer from a config dictionary.

  Arguments:
      config: dict of the form {'class_name': str, 'config': dict}
      custom_objects: dict mapping class names (or function names)
          of custom (non-Keras) objects to class/functions

  Returns:
      Layer instance (may be Model, Sequential, Network, Layer...)
  """
  from tensorflow.python.keras import models  # pylint: disable=g-import-not-at-top
  globs = globals()  # All layers.
  globs['Network'] = models.Network
  globs['Model'] = models.Model
  globs['Sequential'] = models.Sequential
  layer_class_name = config['class_name']
  if layer_class_name in _DESERIALIZATION_TABLE:
    version = 'v2' if tf2.enabled() else 'v1'
    config['class_name'] = _DESERIALIZATION_TABLE[layer_class_name][version]

  return deserialize_keras_object(
      config,
      module_objects=globs,
      custom_objects=custom_objects,
      printable_module_name='layer')
