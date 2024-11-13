# coding=utf-8
# Copyright 2020 The Edward2 Authors.
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

"""Uncertainty-based convolutional layers."""

import functools
from edward2.tensorflow import constraints
from edward2.tensorflow import generated_random_variables
from edward2.tensorflow import initializers
from edward2.tensorflow import random_variable
from edward2.tensorflow import regularizers
from edward2.tensorflow.layers import utils

import tensorflow as tf


@utils.add_weight
class Conv2DReparameterization(tf.keras.layers.Conv2D):
  """2D convolution layer (e.g. spatial convolution over images).

  The layer computes a variational Bayesian approximation to the distribution
  over convolutional layers,

  ```
  p(outputs | inputs) = int conv2d(inputs; weights, bias) p(weights, bias)
    dweights dbias.
  ```

  It does this with a stochastic forward pass, sampling from learnable
  distributions on the kernel and bias. Gradients with respect to the
  distributions' learnable parameters backpropagate via reparameterization.
  Minimizing cross-entropy plus the layer's losses performs variational
  minimum description length, i.e., it minimizes an upper bound to the negative
  marginal likelihood.
  """

  def __init__(self,
               filters,
               kernel_size,
               strides=(1, 1),
               padding='valid',
               data_format=None,
               dilation_rate=(1, 1),
               activation=None,
               use_bias=True,
               kernel_initializer='trainable_normal',
               bias_initializer='zeros',
               kernel_regularizer='normal_kl_divergence',
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=activation,
        use_bias=use_bias,
        kernel_initializer=initializers.get(kernel_initializer),
        bias_initializer=initializers.get(bias_initializer),
        kernel_regularizer=regularizers.get(kernel_regularizer),
        bias_regularizer=regularizers.get(bias_regularizer),
        activity_regularizer=regularizers.get(activity_regularizer),
        kernel_constraint=constraints.get(kernel_constraint),
        bias_constraint=constraints.get(bias_constraint),
        **kwargs)

  def call_weights(self):
    """Calls any weights if the initializer is itself a layer."""
    if isinstance(self.kernel_initializer, tf.keras.layers.Layer):
      self.kernel = self.kernel_initializer(self.kernel.shape, self.dtype)
    if isinstance(self.bias_initializer, tf.keras.layers.Layer):
      self.bias = self.bias_initializer(self.bias.shape, self.dtype)

  def call(self, *args, **kwargs):
    self.call_weights()
    kwargs.pop('training', None)
    return super().call(*args, **kwargs)


@utils.add_weight
class Conv1DReparameterization(tf.keras.layers.Conv1D):
  """1D convolution layer (e.g. temporal convolution over sequences).

  The layer computes a variational Bayesian approximation to the distribution
  over convolutional layers,

  ```
  p(outputs | inputs) = int conv1d(inputs; weights, bias) p(weights, bias)
    dweights dbias.
  ```

  It does this with a stochastic forward pass, sampling from learnable
  distributions on the kernel and bias. Gradients with respect to the
  distributions' learnable parameters backpropagate via reparameterization.
  Minimizing cross-entropy plus the layer's losses performs variational
  minimum description length, i.e., it minimizes an upper bound to the negative
  marginal likelihood.
  """

  def __init__(self,
               filters,
               kernel_size,
               strides=1,
               padding='valid',
               data_format=None,
               dilation_rate=1,
               activation=None,
               use_bias=True,
               kernel_initializer='trainable_normal',
               bias_initializer='zeros',
               kernel_regularizer='normal_kl_divergence',
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=activation,
        use_bias=use_bias,
        kernel_initializer=initializers.get(kernel_initializer),
        bias_initializer=initializers.get(bias_initializer),
        kernel_regularizer=regularizers.get(kernel_regularizer),
        bias_regularizer=regularizers.get(bias_regularizer),
        activity_regularizer=regularizers.get(activity_regularizer),
        kernel_constraint=constraints.get(kernel_constraint),
        bias_constraint=constraints.get(bias_constraint),
        **kwargs)

  def call_weights(self):
    """Calls any weights if the initializer is itself a layer."""
    if isinstance(self.kernel_initializer, tf.keras.layers.Layer):
      self.kernel = self.kernel_initializer(self.kernel.shape, self.dtype)
    if isinstance(self.bias_initializer, tf.keras.layers.Layer):
      self.bias = self.bias_initializer(self.bias.shape, self.dtype)

  def call(self, *args, **kwargs):
    self.call_weights()
    kwargs.pop('training', None)
    return super().call(*args, **kwargs)


class Conv2DFlipout(Conv2DReparameterization):
  """2D convolution layer (e.g. spatial convolution over images).

  The layer computes a variational Bayesian approximation to the distribution
  over convolutional layers,

  ```
  p(outputs | inputs) = int conv2d(inputs; weights, bias) p(weights, bias)
    dweights dbias.
  ```

  It does this with a stochastic forward pass, sampling from learnable
  distributions on the kernel and bias. Gradients with respect to the
  distributions' learnable parameters backpropagate via reparameterization.
  Minimizing cross-entropy plus the layer's losses performs variational
  minimum description length, i.e., it minimizes an upper bound to the negative
  marginal likelihood.

  This layer uses the Flipout estimator (Wen et al., 2018) for integrating with
  respect to the `kernel`. Namely, it applies
  pseudo-independent weight perturbations via independent sign flips for each
  example, enabling variance reduction over independent weight perturbations.
  For this estimator to work, the `kernel` random variable must be able
  to decompose as a sum of its mean and a perturbation distribution; the
  perturbation distribution must be independent across weight elements and
  symmetric around zero (for example, a fully factorized Gaussian).
  """

  def call(self, inputs):
    if not isinstance(self.kernel, random_variable.RandomVariable):
      return super().call(inputs)
    self.call_weights()
    outputs = self._apply_kernel(inputs)
    if self.use_bias:
      if self.data_format == 'channels_first':
        outputs = tf.nn.bias_add(outputs, self.bias, data_format='NCHW')
      else:
        outputs = tf.nn.bias_add(outputs, self.bias, data_format='NHWC')
    if self.activation is not None:
      outputs = self.activation(outputs)
    return outputs

  def _apply_kernel(self, inputs):
    input_shape = tf.shape(inputs)
    batch_dim = input_shape[0]
    if self._convolution_op is None:
      padding = self.padding
      if self.padding == 'causal':
        padding = 'valid'
      if not isinstance(padding, (list, tuple)):
        padding = padding.upper()
      self._convolution_op = functools.partial(
          tf.nn.convolution,
          strides=self.strides,
          padding=padding,
          data_format='NHWC' if self.data_format == 'channels_last' else 'NCHW',
          dilations=self.dilation_rate)

    if self.data_format == 'channels_first':
      channels = input_shape[1]
      sign_input_shape = [batch_dim, channels, 1, 1]
      sign_output_shape = [batch_dim, self.filters, 1, 1]
    else:
      channels = input_shape[-1]
      sign_input_shape = [batch_dim, 1, 1, channels]
      sign_output_shape = [batch_dim, 1, 1, self.filters]
    sign_input = tf.cast(2 * tf.random.uniform(sign_input_shape,
                                               minval=0,
                                               maxval=2,
                                               dtype=tf.int32) - 1,
                         inputs.dtype)
    sign_output = tf.cast(2 * tf.random.uniform(sign_output_shape,
                                                minval=0,
                                                maxval=2,
                                                dtype=tf.int32) - 1,
                          inputs.dtype)
    kernel_mean = self.kernel.distribution.mean()
    perturbation = self.kernel - kernel_mean
    outputs = self._convolution_op(inputs, kernel_mean)
    outputs += self._convolution_op(inputs * sign_input,
                                    perturbation) * sign_output
    return outputs


class Conv1DFlipout(Conv1DReparameterization):
  """1D convolution layer (e.g. temporal convolution over sequences).

  The layer computes a variational Bayesian approximation to the distribution
  over convolutional layers,

  ```
  p(outputs | inputs) = int conv1d(inputs; weights, bias) p(weights, bias)
    dweights dbias.
  ```

  It does this with a stochastic forward pass, sampling from learnable
  distributions on the kernel and bias. Gradients with respect to the
  distributions' learnable parameters backpropagate via reparameterization.
  Minimizing cross-entropy plus the layer's losses performs variational
  minimum description length, i.e., it minimizes an upper bound to the negative
  marginal likelihood.

  This layer uses the Flipout estimator (Wen et al., 2018) for integrating with
  respect to the `kernel`. Namely, it applies
  pseudo-independent weight perturbations via independent sign flips for each
  example, enabling variance reduction over independent weight perturbations.
  For this estimator to work, the `kernel` random variable must be able
  to decompose as a sum of its mean and a perturbation distribution; the
  perturbation distribution must be independent across weight elements and
  symmetric around zero (for example, a fully factorized Gaussian).
  """

  def call(self, inputs):
    if not isinstance(self.kernel, random_variable.RandomVariable):
      return super().call(inputs)
    self.call_weights()
    outputs = self._apply_kernel(inputs)
    if self.use_bias:
      if self.data_format == 'channels_first':
        outputs = tf.nn.bias_add(outputs, self.bias, data_format='NCW')
      else:
        outputs = tf.nn.bias_add(outputs, self.bias, data_format='NWC')
    if self.activation is not None:
      outputs = self.activation(outputs)
    return outputs

  def _apply_kernel(self, inputs):
    input_shape = tf.shape(inputs)
    batch_dim = input_shape[0]
    if self._convolution_op is None:
      padding = self.padding
      if self.padding == 'causal':
        padding = 'valid'
      if not isinstance(padding, (list, tuple)):
        padding = padding.upper()
      self._convolution_op = functools.partial(
          tf.nn.convolution,
          strides=self.strides,
          padding=padding,
          data_format='NWC' if self.data_format == 'channels_last' else 'NCW',
          dilations=self.dilation_rate)

    if self.data_format == 'channels_first':
      channels = input_shape[1]
      sign_input_shape = [batch_dim, channels, 1]
      sign_output_shape = [batch_dim, self.filters, 1]
    else:
      channels = input_shape[-1]
      sign_input_shape = [batch_dim, 1, channels]
      sign_output_shape = [batch_dim, 1, self.filters]
    sign_input = tf.cast(
        2 * tf.random.uniform(
            sign_input_shape, minval=0, maxval=2, dtype=tf.int32) - 1,
        inputs.dtype)
    sign_output = tf.cast(
        2 * tf.random.uniform(
            sign_output_shape, minval=0, maxval=2, dtype=tf.int32) - 1,
        inputs.dtype)
    kernel_mean = self.kernel.distribution.mean()
    perturbation = self.kernel - kernel_mean
    outputs = self._convolution_op(inputs, kernel_mean)
    outputs += self._convolution_op(inputs * sign_input,
                                    perturbation) * sign_output
    return outputs


class Conv2DHierarchical(Conv2DFlipout):
  """2D convolution layer with hierarchical distributions.

  The layer computes a variational Bayesian approximation to the distribution
  over convolutional layers, and where the distribution over weights
  involves a hierarchical distribution with hidden unit noise coupling vectors
  of the kernel weight matrix (Louizos et al., 2017),

  ```
  p(outputs | inputs) = int conv2d(inputs; new_kernel, bias) p(kernel,
    local_scales, global_scale, bias) dkernel dlocal_scales dglobal_scale dbias.
  ```

  It does this with a stochastic forward pass, sampling from learnable
  distributions on the kernel and bias. The kernel is written in non-centered
  parameterization where

  ```
  new_kernel[i, j] = kernel[i, j] * local_scale[j] * global_scale.
  ```

  That is, there is "local" multiplicative noise which couples weights for each
  output filter. There is also a "global" multiplicative noise which couples the
  entire weight matrix. By default, the weights are normally distributed and the
  local and global noises are half-Cauchy distributed; this makes the kernel a
  horseshoe distribution (Carvalho et al., 2009; Polson and Scott, 2012).

  The estimation uses Flipout for variance reduction with respect to sampling
  the full weights. Gradients with respect to the distributions' learnable
  parameters backpropagate via reparameterization. Minimizing cross-entropy
  plus the layer's losses performs variational minimum description length,
  i.e., it minimizes an upper bound to the negative marginal likelihood.
  """

  def __init__(self,
               filters,
               kernel_size,
               strides=(1, 1),
               padding='valid',
               data_format=None,
               dilation_rate=(1, 1),
               activation=None,
               use_bias=True,
               kernel_initializer='trainable_normal',
               bias_initializer='zeros',
               local_scale_initializer='trainable_half_cauchy',
               global_scale_initializer='trainable_half_cauchy',
               kernel_regularizer='normal_kl_divergence',
               bias_regularizer=None,
               local_scale_regularizer='half_cauchy_kl_divergence',
               global_scale_regularizer=regularizers.HalfCauchyKLDivergence(
                   scale=1e-5),
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               local_scale_constraint='softplus',
               global_scale_constraint='softplus',
               **kwargs):
    self.local_scale_initializer = initializers.get(local_scale_initializer)
    self.global_scale_initializer = initializers.get(global_scale_initializer)
    self.local_scale_regularizer = regularizers.get(local_scale_regularizer)
    self.global_scale_regularizer = regularizers.get(global_scale_regularizer)
    self.local_scale_constraint = constraints.get(local_scale_constraint)
    self.global_scale_constraint = constraints.get(global_scale_constraint)
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=activation,
        use_bias=use_bias,
        kernel_initializer=initializers.get(kernel_initializer),
        bias_initializer=initializers.get(bias_initializer),
        kernel_regularizer=regularizers.get(kernel_regularizer),
        bias_regularizer=regularizers.get(bias_regularizer),
        activity_regularizer=regularizers.get(activity_regularizer),
        kernel_constraint=constraints.get(kernel_constraint),
        bias_constraint=constraints.get(bias_constraint),
        **kwargs)

  def build(self, input_shape):
    self.local_scale = self.add_weight(
        shape=(self.filters,),
        name='local_scale',
        initializer=self.local_scale_initializer,
        regularizer=self.local_scale_regularizer,
        constraint=self.local_scale_constraint)
    self.global_scale = self.add_weight(
        shape=(),
        name='global_scale',
        initializer=self.global_scale_initializer,
        regularizer=self.global_scale_regularizer,
        constraint=self.global_scale_constraint)
    super().build(input_shape)

  def call_weights(self):
    """Calls any weights if the initializer is itself a layer."""
    if isinstance(self.local_scale_initializer, tf.keras.layers.Layer):
      self.local_scale = self.local_scale_initializer(self.local_scale.shape,
                                                      self.dtype)
    if isinstance(self.global_scale_initializer, tf.keras.layers.Layer):
      self.global_scale = self.global_scale_initializer(self.global_scale.shape,
                                                        self.dtype)
    super().call_weights()

  def _apply_kernel(self, inputs):
    outputs = super()._apply_kernel(inputs)
    if self.data_format == 'channels_first':
      local_scale = tf.reshape(self.local_scale, [1, -1, 1, 1])
    else:
      local_scale = tf.reshape(self.local_scale, [1, 1, 1, -1])
    # TODO(trandustin): Figure out what to set local/global scales to at test
    # time. Means don't exist for Half-Cauchy approximate posteriors.
    outputs *= local_scale * self.global_scale
    return outputs


class Conv2DVariationalDropout(Conv2DReparameterization):
  """2D convolution layer with variational dropout (Kingma et al., 2015).

  Implementation follows the additive parameterization of
  Molchanov et al. (2017).
  """

  def __init__(self,
               filters,
               kernel_size,
               strides=(1, 1),
               padding='valid',
               data_format=None,
               dilation_rate=(1, 1),
               activation=None,
               use_bias=True,
               kernel_initializer='trainable_normal',
               bias_initializer='zeros',
               kernel_regularizer='log_uniform_kl_divergence',
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=activation,
        use_bias=use_bias,
        kernel_initializer=initializers.get(kernel_initializer),
        bias_initializer=initializers.get(bias_initializer),
        kernel_regularizer=regularizers.get(kernel_regularizer),
        bias_regularizer=regularizers.get(bias_regularizer),
        activity_regularizer=regularizers.get(activity_regularizer),
        kernel_constraint=constraints.get(kernel_constraint),
        bias_constraint=constraints.get(bias_constraint),
        **kwargs)

  def call(self, inputs, training=None):
    if not isinstance(self.kernel, random_variable.RandomVariable):
      return super().call(inputs)
    self.call_weights()
    if training is None:
      training = tf.keras.backend.learning_phase()
    if self._convolution_op is None:
      padding = self.padding
      if self.padding == 'causal':
        padding = 'valid'
      if not isinstance(padding, (list, tuple)):
        padding = padding.upper()
      self._convolution_op = functools.partial(
          tf.nn.convolution,
          strides=self.strides,
          padding=padding,
          data_format='NHWC' if self.data_format == 'channels_last' else 'NCHW',
          dilations=self.dilation_rate)

    def dropped_inputs():
      """Forward pass with dropout."""
      # Clip magnitude of dropout rate, where we get the dropout rate alpha from
      # the additive parameterization (Molchanov et al., 2017): for weight ~
      # Normal(mu, sigma**2), the variance `sigma**2 = alpha * mu**2`.
      mean = self.kernel.distribution.mean()
      log_variance = tf.math.log(self.kernel.distribution.variance())
      log_alpha = log_variance - tf.math.log(tf.square(mean) +
                                             tf.keras.backend.epsilon())
      log_alpha = tf.clip_by_value(log_alpha, -8., 8.)
      log_variance = log_alpha + tf.math.log(tf.square(mean) +
                                             tf.keras.backend.epsilon())

      means = self._convolution_op(inputs, mean)
      stddevs = tf.sqrt(
          self._convolution_op(tf.square(inputs), tf.exp(log_variance)) +
          tf.keras.backend.epsilon())
      if self.use_bias:
        if self.data_format == 'channels_first':
          means = tf.nn.bias_add(means, self.bias, data_format='NCHW')
        else:
          means = tf.nn.bias_add(means, self.bias, data_format='NHWC')
      outputs = generated_random_variables.Normal(loc=means, scale=stddevs)
      if self.activation is not None:
        outputs = self.activation(outputs)
      return outputs

    # Following tf.keras.Dropout, only apply variational dropout if training
    # flag is True.
    training_value = utils.smart_constant_value(training)
    if training_value is not None:
      if training_value:
        return dropped_inputs()
      else:
        return super().call(inputs)
    return tf.cond(
        pred=training,
        true_fn=dropped_inputs,
        false_fn=lambda: super(Conv2DVariationalDropout, self).call(inputs))


class Conv2DBatchEnsemble(tf.keras.layers.Conv2D):
  """A batch ensemble convolutional layer."""

  def __init__(self,
               filters,
               kernel_size,
               rank=1,
               ensemble_size=4,
               alpha_initializer='ones',
               gamma_initializer='ones',
               strides=(1, 1),
               padding='valid',
               data_format=None,
               activation=None,
               use_bias=True,
               kernel_initializer='glorot_uniform',
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        activation=None,
        use_bias=False,
        kernel_initializer=kernel_initializer,
        bias_initializer=None,
        kernel_regularizer=kernel_regularizer,
        bias_regularizer=None,
        activity_regularizer=activity_regularizer,
        kernel_constraint=kernel_constraint,
        bias_constraint=None,
        **kwargs)
    self.rank = rank
    self.ensemble_size = ensemble_size
    self.alpha_initializer = initializers.get(alpha_initializer)
    self.gamma_initializer = initializers.get(gamma_initializer)
    self.ensemble_bias_initializer = initializers.get(bias_initializer)
    self.ensemble_bias_regularizer = regularizers.get(bias_regularizer)
    self.ensemble_bias_constraint = constraints.get(bias_constraint)
    self.ensemble_activation = tf.keras.activations.get(activation)
    self.use_ensemble_bias = use_bias

  def build(self, input_shape):
    input_shape = tf.TensorShape(input_shape)
    super().build(input_shape)
    if self.data_format == 'channels_first':
      input_channel = input_shape[1]
    elif self.data_format == 'channels_last':
      input_channel = input_shape[-1]

    if self.rank > 1:
      alpha_shape = [self.rank, self.ensemble_size, input_channel]
      gamma_shape = [self.rank, self.ensemble_size, self.filters]
    else:
      alpha_shape = [self.ensemble_size, input_channel]
      gamma_shape = [self.ensemble_size, self.filters]
    self.alpha = self.add_weight(
        'alpha',
        shape=alpha_shape,
        initializer=self.alpha_initializer,
        trainable=True,
        dtype=self.dtype)
    self.gamma = self.add_weight(
        'gamma',
        shape=gamma_shape,
        initializer=self.gamma_initializer,
        trainable=True,
        dtype=self.dtype)
    if self.use_ensemble_bias:
      self.ensemble_bias = self.add_weight(
          name='ensemble_bias',
          shape=[self.ensemble_size, self.filters],
          initializer=self.ensemble_bias_initializer,
          regularizer=self.ensemble_bias_regularizer,
          constraint=self.ensemble_bias_constraint,
          trainable=True,
          dtype=self.dtype)
    else:
      self.ensemble_bias = None
    self.built = True

  def call(self, inputs):
    input_dim = self.alpha.shape[-1]
    batch_size = tf.shape(inputs)[0]
    examples_per_model = batch_size // self.ensemble_size
    # TODO(ywenxu): Merge the following two cases.
    if self.rank > 1:
      # TODO(ywenxu): Check whether the following works in channels_last case.
      axis_change = -1 if self.data_format == 'channels_first' else 2
      alpha = tf.reshape(tf.tile(self.alpha, [1, 1, examples_per_model]),
                         [self.rank, batch_size, input_dim])
      gamma = tf.reshape(tf.tile(self.gamma, [1, 1, examples_per_model]),
                         [self.rank, batch_size, self.filters])

      alpha = tf.expand_dims(alpha, axis=axis_change)
      alpha = tf.expand_dims(alpha, axis=axis_change)
      gamma = tf.expand_dims(gamma, axis=axis_change)
      gamma = tf.expand_dims(gamma, axis=axis_change)

      perturb_inputs = tf.expand_dims(inputs, 0) * alpha
      perturb_inputs = tf.reshape(perturb_inputs, tf.concat(
          [[-1], perturb_inputs.shape[2:]], 0))
      outputs = super().call(perturb_inputs)

      outputs = tf.reshape(outputs, tf.concat(
          [[self.rank, -1], outputs.shape[1:]], 0))
      outputs = tf.reduce_sum(outputs * gamma, axis=0)
    else:
      axis_change = -1 if self.data_format == 'channels_first' else 1
      alpha = tf.reshape(tf.tile(self.alpha, [1, examples_per_model]),
                         [batch_size, input_dim])
      gamma = tf.reshape(tf.tile(self.gamma, [1, examples_per_model]),
                         [batch_size, self.filters])
      alpha = tf.expand_dims(alpha, axis=axis_change)
      alpha = tf.expand_dims(alpha, axis=axis_change)
      gamma = tf.expand_dims(gamma, axis=axis_change)
      gamma = tf.expand_dims(gamma, axis=axis_change)
      outputs = super().call(inputs*alpha) * gamma

    if self.use_ensemble_bias:
      bias = tf.reshape(tf.tile(self.ensemble_bias, [1, examples_per_model]),
                        [batch_size, self.filters])
      bias = tf.expand_dims(bias, axis=axis_change)
      bias = tf.expand_dims(bias, axis=axis_change)
      outputs += bias

    if self.ensemble_activation is not None:
      outputs = self.ensemble_activation(outputs)
    return outputs

  def get_config(self):
    config = {
        'ensemble_size':
            self.ensemble_size,
        'alpha_initializer':
            initializers.serialize(self.alpha_initializer),
        'gamma_initializer':
            initializers.serialize(self.gamma_initializer),
        'ensemble_bias_initializer':
            initializers.serialize(self.ensemble_bias_initializer),
        'ensemble_bias_regularizer':
            regularizers.serialize(self.ensemble_bias_regularizer),
        'ensemble_bias_constraint':
            constraints.serialize(self.ensemble_bias_constraint),
        'ensemble_activation':
            tf.keras.activations.serialize(self.ensemble_activation),
        'use_ensemble_bias':
            self.use_ensemble_bias,
    }
    new_config = super().get_config()
    new_config.update(config)
    return new_config


class Conv1DBatchEnsemble(tf.keras.layers.Conv1D):
  """A batch ensemble convolutional layer."""

  def __init__(self,
               filters,
               kernel_size,
               ensemble_size=4,
               alpha_initializer='ones',
               gamma_initializer='ones',
               strides=1,
               padding='valid',
               data_format='channels_last',
               activation=None,
               use_bias=True,
               kernel_initializer='glorot_uniform',
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        activation=None,
        use_bias=False,
        kernel_initializer=kernel_initializer,
        bias_initializer=None,
        kernel_regularizer=kernel_regularizer,
        bias_regularizer=None,
        activity_regularizer=activity_regularizer,
        kernel_constraint=kernel_constraint,
        bias_constraint=None,
        **kwargs)
    self.ensemble_size = ensemble_size
    self.alpha_initializer = initializers.get(alpha_initializer)
    self.gamma_initializer = initializers.get(gamma_initializer)
    self.ensemble_bias_initializer = initializers.get(bias_initializer)
    self.ensemble_bias_regularizer = regularizers.get(bias_regularizer)
    self.ensemble_bias_constraint = constraints.get(bias_constraint)
    self.ensemble_activation = tf.keras.activations.get(activation)
    self.use_ensemble_bias = use_bias

  def build(self, input_shape):
    input_shape = tf.TensorShape(input_shape)
    super().build(input_shape)
    if self.data_format == 'channels_first':
      input_channel = input_shape[1]
    elif self.data_format == 'channels_last':
      input_channel = input_shape[-1]

    self.alpha = self.add_weight(
        'alpha',
        shape=[self.ensemble_size, input_channel],
        initializer=self.alpha_initializer,
        trainable=True,
        dtype=self.dtype)
    self.gamma = self.add_weight(
        'gamma',
        shape=[self.ensemble_size, self.filters],
        initializer=self.gamma_initializer,
        trainable=True,
        dtype=self.dtype)
    if self.use_ensemble_bias:
      self.ensemble_bias = self.add_weight(
          name='ensemble_bias',
          shape=[self.ensemble_size, self.filters],
          initializer=self.ensemble_bias_initializer,
          regularizer=self.ensemble_bias_regularizer,
          constraint=self.ensemble_bias_constraint,
          trainable=True,
          dtype=self.dtype)
    else:
      self.ensemble_bias = None
    self.built = True

  def call(self, inputs):
    axis_change = -1 if self.data_format == 'channels_first' else 1
    batch_size = tf.shape(inputs)[0]
    input_dim = self.alpha.shape[-1]
    examples_per_model = batch_size // self.ensemble_size
    alpha = tf.reshape(tf.tile(self.alpha, [1, examples_per_model]),
                       [batch_size, input_dim])
    gamma = tf.reshape(tf.tile(self.gamma, [1, examples_per_model]),
                       [batch_size, self.filters])
    alpha = tf.expand_dims(alpha, axis=axis_change)
    gamma = tf.expand_dims(gamma, axis=axis_change)
    outputs = super().call(inputs*alpha) * gamma

    if self.use_ensemble_bias:
      bias = tf.reshape(tf.tile(self.ensemble_bias, [1, examples_per_model]),
                        [batch_size, self.filters])
      bias = tf.expand_dims(bias, axis=axis_change)
      outputs += bias

    if self.ensemble_activation is not None:
      outputs = self.ensemble_activation(outputs)
    return outputs

  def get_config(self):
    config = {
        'ensemble_size':
            self.ensemble_size,
        'alpha_initializer':
            initializers.serialize(self.alpha_initializer),
        'gamma_initializer':
            initializers.serialize(self.gamma_initializer),
        'ensemble_bias_initializer':
            initializers.serialize(self.ensemble_bias_initializer),
        'ensemble_bias_regularizer':
            regularizers.serialize(self.ensemble_bias_regularizer),
        'ensemble_bias_constraint':
            constraints.serialize(self.ensemble_bias_constraint),
        'ensemble_activation':
            tf.keras.activations.serialize(self.ensemble_activation),
        'use_ensemble_bias':
            self.use_ensemble_bias,
    }
    new_config = super().get_config()
    new_config.update(config)
    return new_config


@utils.add_weight
class CondConv2D(tf.keras.layers.Conv2D):
  """2D conditional convolution layer (e.g. spatial convolution over images).

  This layer extends the base 2D convolution layer to compute example-dependent
  parameters. A CondConv2D layer has 'num_experts` kernels and biases. It
  computes a kernel and bias for each example as a weighted sum of experts
  using the input example-dependent routing weights, then applies the 2D
  convolution to each example.

  Attributes:
    filters: Integer, the dimensionality of the output space (i.e. the number of
      output filters in the convolution).
    kernel_size: An integer or tuple/list of 2 integers, specifying the height
      and width of the 2D convolution window. Can be a single integer to specify
      the same value for all spatial dimensions.
    num_experts: The number of expert kernels and biases in the CondConv layer.
    strides: An integer or tuple/list of 2 integers, specifying the strides of
      the convolution along the height and width. Can be a single integer to
      specify the same value for all spatial dimensions. Specifying any stride
      value != 1 is incompatible with specifying any `dilation_rate` value != 1.
    padding: one of `"valid"` or `"same"` (case-insensitive).
    data_format: A string, one of `channels_last` (default) or `channels_first`.
      The ordering of the dimensions in the inputs. `channels_last` corresponds
      to inputs with shape `(batch, height, width, channels)` while
      `channels_first` corresponds to inputs with shape `(batch, channels,
      height, width)`. It defaults to the `image_data_format` value found in
      your Keras config file at `~/.keras/keras.json`. If you never set it, then
      it will be "channels_last".
    dilation_rate: an integer or tuple/list of 2 integers, specifying the
      dilation rate to use for dilated convolution. Can be a single integer to
      specify the same value for all spatial dimensions. Currently, specifying
      any `dilation_rate` value != 1 is incompatible with specifying any stride
      value != 1.
    activation: Activation function to use. If you don't specify anything, no
      activation is applied
      (ie. "linear" activation: `a(x) = x`).
    use_bias: Boolean, whether the layer uses a bias vector.
    kernel_initializer: Initializer for the `kernel` weights matrix.
    bias_initializer: Initializer for the bias vector.
    kernel_regularizer: Regularizer function applied to the `kernel` weights
      matrix.
    bias_regularizer: Regularizer function applied to the bias vector.
    activity_regularizer: Regularizer function applied to the output of the
      layer (its "activation")..
    kernel_constraint: Constraint function applied to the kernel matrix.
    bias_constraint: Constraint function applied to the bias vector.

  Input shape:
    4D tensor with shape: `(samples, channels, rows, cols)` if
      data_format='channels_first'
    or 4D tensor with shape: `(samples, rows, cols, channels)` if
      data_format='channels_last'.

  Output shape:
    4D tensor with shape: `(samples, filters, new_rows, new_cols)` if
      data_format='channels_first'
    or 4D tensor with shape: `(samples, new_rows, new_cols, filters)` if
      data_format='channels_last'. `rows` and `cols` values might have changed
      due to padding.
  """

  def __init__(self,
               filters,
               kernel_size,
               num_experts,
               strides=(1, 1),
               padding='valid',
               data_format=None,
               dilation_rate=(1, 1),
               activation=None,
               use_bias=True,
               kernel_initializer='glorot_uniform',
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=activation,
        use_bias=use_bias,
        kernel_initializer=kernel_initializer,
        bias_initializer=bias_initializer,
        kernel_regularizer=kernel_regularizer,
        bias_regularizer=bias_regularizer,
        activity_regularizer=activity_regularizer,
        kernel_constraint=kernel_constraint,
        bias_constraint=bias_constraint,
        **kwargs)
    if num_experts < 1:
      raise ValueError('A CondConv layer must have at least one expert.')
    self.num_experts = num_experts
    if self.data_format == 'channels_first':
      self.converted_data_format = 'NCHW'
    else:
      self.converted_data_format = 'NHWC'

  def build(self, input_shape):
    if len(input_shape) != 4:
      raise ValueError(
          'Inputs to `CondConv2D` should have rank 4. '
          'Received input shape:', str(input_shape))
    input_shape = tf.TensorShape(input_shape)
    channel_axis = self._get_channel_axis()
    if input_shape.dims[channel_axis].value is None:
      raise ValueError('The channel dimension of the inputs '
                       'should be defined. Found `None`.')
    input_dim = int(input_shape[channel_axis])

    self.kernel_shape = self.kernel_size + (input_dim, self.filters)
    kernel_num_params = 1
    for kernel_dim in self.kernel_shape:
      kernel_num_params *= kernel_dim
    condconv_kernel_shape = (self.num_experts, kernel_num_params)
    self.condconv_kernel = self.add_weight(
        name='condconv_kernel',
        shape=condconv_kernel_shape,
        initializer=initializers.get_condconv_initializer(
            self.kernel_initializer,
            self.num_experts,
            self.kernel_shape),
        regularizer=self.kernel_regularizer,
        constraint=self.kernel_constraint,
        trainable=True,
        dtype=self.dtype)

    if self.use_bias:
      self.bias_shape = (self.filters,)
      condconv_bias_shape = (self.num_experts, self.filters)
      self.condconv_bias = self.add_weight(
          name='condconv_bias',
          shape=condconv_bias_shape,
          initializer=initializers.get_condconv_initializer(
              self.bias_initializer,
              self.num_experts,
              self.bias_shape),
          regularizer=self.bias_regularizer,
          constraint=self.bias_constraint,
          trainable=True,
          dtype=self.dtype)
    else:
      self.bias = None

    self.input_spec = tf.keras.layers.InputSpec(
        ndim=self.rank + 2, axes={channel_axis: input_dim})

    self.built = True

  def call(self, inputs, routing_weights):
    # Compute example dependent kernels
    kernels = tf.matmul(routing_weights, self.condconv_kernel)
    batch_size = inputs.shape[0].value
    inputs = tf.split(inputs, batch_size, 0)
    kernels = tf.split(kernels, batch_size, 0)
    # Apply example-dependent convolution to each example in the batch
    outputs_list = []
    # TODO(ywenxu): Check out tf.vectorized_map.
    for input_tensor, kernel in zip(inputs, kernels):
      kernel = tf.reshape(kernel, self.kernel_shape)
      outputs_list.append(
          tf.nn.convolution(
              input_tensor,
              kernel,
              strides=self.strides,
              padding=self._get_padding_op(),
              dilations=self.dilation_rate,
              data_format=self.converted_data_format))
    outputs = tf.concat(outputs_list, 0)

    if self.use_bias:
      # Compute example-dependent biases
      biases = tf.matmul(routing_weights, self.condconv_bias)
      outputs = tf.split(outputs, batch_size, 0)
      biases = tf.split(biases, batch_size, 0)
      # Add example-dependent bias to each example in the batch
      bias_outputs_list = []
      for output, bias in zip(outputs, biases):
        bias = tf.squeeze(bias, axis=0)
        bias_outputs_list.append(
            tf.nn.bias_add(output, bias,
                           data_format=self.converted_data_format))
      outputs = tf.concat(bias_outputs_list, 0)

    if self.activation is not None:
      return self.activation(outputs)
    return outputs

  def get_config(self):
    config = {'num_experts': self.num_experts}
    base_config = super().get_config()
    return dict(list(base_config.items()) + list(config.items()))

  def _get_channel_axis(self):
    if self.data_format == 'channels_first':
      return 1
    else:
      return -1

  def _get_padding_op(self):
    if self.padding == 'causal':
      op_padding = 'valid'
    else:
      op_padding = self.padding
    if not isinstance(op_padding, (list, tuple)):
      op_padding = op_padding.upper()
    return op_padding


@utils.add_weight
class DepthwiseCondConv2D(tf.keras.layers.DepthwiseConv2D):
  """Depthwise separable 2D conditional convolution layer.

  This layer extends the base depthwise 2D convolution layer to compute
  example-dependent parameters. A DepthwiseCondConv2D layer has 'num_experts`
  kernels and biases. It computes a kernel and bias for each example as a
  weighted sum of experts using the input example-dependent routing weights,
  then applies the depthwise convolution to each example.

  Attributes:
    kernel_size: An integer or tuple/list of 2 integers, specifying the height
      and width of the 2D convolution window. Can be a single integer to specify
      the same value for all spatial dimensions.
    num_experts: The number of expert kernels and biases in the
      DepthwiseCondConv2D layer.
    strides: An integer or tuple/list of 2 integers, specifying the strides of
      the convolution along the height and width. Can be a single integer to
      specify the same value for all spatial dimensions. Specifying any stride
      value != 1 is incompatible with specifying any `dilation_rate` value != 1.
    padding: one of `'valid'` or `'same'` (case-insensitive).
    depth_multiplier: The number of depthwise convolution output channels for
      each input channel. The total number of depthwise convolution output
      channels will be equal to `filters_in * depth_multiplier`.
    data_format: A string, one of `channels_last` (default) or `channels_first`.
      The ordering of the dimensions in the inputs. `channels_last` corresponds
      to inputs with shape `(batch, height, width, channels)` while
      `channels_first` corresponds to inputs with shape `(batch, channels,
      height, width)`. It defaults to the `image_data_format` value found in
      your Keras config file at `~/.keras/keras.json`. If you never set it, then
      it will be 'channels_last'.
    activation: Activation function to use. If you don't specify anything, no
      activation is applied
      (ie. 'linear' activation: `a(x) = x`).
    use_bias: Boolean, whether the layer uses a bias vector.
    depthwise_initializer: Initializer for the depthwise kernel matrix.
    bias_initializer: Initializer for the bias vector.
    depthwise_regularizer: Regularizer function applied to the depthwise kernel
      matrix.
    bias_regularizer: Regularizer function applied to the bias vector.
    activity_regularizer: Regularizer function applied to the output of the
      layer (its 'activation').
    depthwise_constraint: Constraint function applied to the depthwise kernel
      matrix.
    bias_constraint: Constraint function applied to the bias vector.

  Input shape:
    4D tensor with shape: `[batch, channels, rows, cols]` if
      data_format='channels_first'
    or 4D tensor with shape: `[batch, rows, cols, channels]` if
      data_format='channels_last'.

  Output shape:
    4D tensor with shape: `[batch, filters, new_rows, new_cols]` if
      data_format='channels_first'
    or 4D tensor with shape: `[batch, new_rows, new_cols, filters]` if
      data_format='channels_last'. `rows` and `cols` values might have changed
      due to padding.
  """

  def __init__(self,
               kernel_size,
               num_experts,
               strides=(1, 1),
               padding='valid',
               depth_multiplier=1,
               data_format=None,
               activation=None,
               use_bias=True,
               depthwise_initializer='glorot_uniform',
               bias_initializer='zeros',
               depthwise_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               depthwise_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        depth_multiplier=depth_multiplier,
        data_format=data_format,
        activation=activation,
        use_bias=use_bias,
        depthwise_initializer=depthwise_initializer,
        bias_initializer=bias_initializer,
        depthwise_regularizer=depthwise_regularizer,
        bias_regularizer=bias_regularizer,
        activity_regularizer=activity_regularizer,
        depthwise_constraint=depthwise_constraint,
        bias_constraint=bias_constraint,
        **kwargs)
    if num_experts < 1:
      raise ValueError('A CondConv layer must have at least one expert.')
    self.num_experts = num_experts
    if self.data_format == 'channels_first':
      self.converted_data_format = 'NCHW'
    else:
      self.converted_data_format = 'NHWC'

  def build(self, input_shape):
    if len(input_shape) < 4:
      raise ValueError(
          'Inputs to `DepthwiseCondConv2D` should have rank 4. '
          'Received input shape:', str(input_shape))
    input_shape = tf.TensorShape(input_shape)
    if self.data_format == 'channels_first':
      channel_axis = 1
    else:
      channel_axis = 3
    if input_shape.dims[channel_axis].value is None:
      raise ValueError('The channel dimension of the inputs to '
                       '`DepthwiseConv2D` '
                       'should be defined. Found `None`.')
    input_dim = int(input_shape[channel_axis])
    self.depthwise_kernel_shape = (self.kernel_size[0], self.kernel_size[1],
                                   input_dim, self.depth_multiplier)

    depthwise_kernel_num_params = 1
    for dim in self.depthwise_kernel_shape:
      depthwise_kernel_num_params *= dim
    depthwise_condconv_kernel_shape = (self.num_experts,
                                       depthwise_kernel_num_params)

    self.depthwise_condconv_kernel = self.add_weight(
        shape=depthwise_condconv_kernel_shape,
        initializer=initializers.get_condconv_initializer(
            self.depthwise_initializer,
            self.num_experts,
            self.depthwise_kernel_shape),
        name='depthwise_condconv_kernel',
        regularizer=self.depthwise_regularizer,
        constraint=self.depthwise_constraint,
        trainable=True)

    if self.use_bias:
      bias_dim = input_dim * self.depth_multiplier
      self.bias_shape = (bias_dim,)
      condconv_bias_shape = (self.num_experts, bias_dim)
      self.condconv_bias = self.add_weight(
          name='condconv_bias',
          shape=condconv_bias_shape,
          initializer=initializers.get_condconv_initializer(
              self.bias_initializer,
              self.num_experts,
              self.bias_shape),
          regularizer=self.bias_regularizer,
          constraint=self.bias_constraint,
          trainable=True,
          dtype=self.dtype)
    else:
      self.bias = None
    # Set input spec.
    self.input_spec = tf.keras.layers.InputSpec(
        ndim=4, axes={channel_axis: input_dim})
    self.built = True

  def call(self, inputs, routing_weights):
    # Compute example dependent depthwise kernels
    depthwise_kernels = tf.matmul(routing_weights,
                                  self.depthwise_condconv_kernel)
    batch_size = inputs.shape[0].value
    inputs = tf.split(inputs, batch_size, 0)
    depthwise_kernels = tf.split(depthwise_kernels, batch_size, 0)
    # Apply example-dependent depthwise convolution to each example in the batch
    outputs_list = []
    if self.data_format == 'channels_first':
      converted_strides = (1, 1) + self.strides
    else:
      converted_strides = (1,) + self.strides + (1,)
    for input_tensor, depthwise_kernel in zip(inputs, depthwise_kernels):
      depthwise_kernel = tf.reshape(depthwise_kernel,
                                    self.depthwise_kernel_shape)
      outputs_list.append(
          tf.nn.depthwise_conv2d(
              input_tensor,
              depthwise_kernel,
              strides=converted_strides,
              padding=self.padding.upper(),
              dilations=self.dilation_rate,
              data_format=self.converted_data_format))
    outputs = tf.concat(outputs_list, 0)

    if self.use_bias:
      # Compute example-dependent biases
      biases = tf.matmul(routing_weights, self.condconv_bias)
      outputs = tf.split(outputs, batch_size, 0)
      biases = tf.split(biases, batch_size, 0)
      # Add example-dependent bias to each example in the batch
      bias_outputs_list = []
      for output, bias in zip(outputs, biases):
        bias = tf.squeeze(bias, axis=0)
        bias_outputs_list.append(
            tf.nn.bias_add(output, bias,
                           data_format=self.converted_data_format))
      outputs = tf.concat(bias_outputs_list, 0)

    if self.activation is not None:
      return self.activation(outputs)

    return outputs

  def get_config(self):
    config = {'num_experts': self.num_experts}
    base_config = super().get_config()
    return dict(list(base_config.items()) + list(config.items()))


class DepthwiseConv2DBatchEnsemble(tf.keras.layers.DepthwiseConv2D):
  """Batch ensemble of depthwise separable 2D convolutions."""

  def __init__(self,
               kernel_size,
               ensemble_size=4,
               alpha_initializer='ones',
               gamma_initializer='ones',
               strides=(1, 1),
               padding='valid',
               depth_multiplier=1,
               data_format=None,
               activation=None,
               use_bias=True,
               depthwise_initializer='glorot_uniform',
               bias_initializer='zeros',
               depthwise_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               depthwise_constraint=None,
               bias_constraint=None,
               **kwargs):
    super().__init__(
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        depth_multiplier=depth_multiplier,
        data_format=data_format,
        activation=activation,
        use_bias=use_bias,
        depthwise_initializer=depthwise_initializer,
        bias_initializer=None,
        depthwise_regularizer=depthwise_regularizer,
        bias_regularizer=None,
        activity_regularizer=activity_regularizer,
        depthwise_constraint=depthwise_constraint,
        bias_constraint=None,
        **kwargs)
    self.ensemble_size = ensemble_size
    self.alpha_initializer = initializers.get(alpha_initializer)
    self.gamma_initializer = initializers.get(gamma_initializer)
    self.ensemble_bias_initializer = initializers.get(bias_initializer)
    self.ensemble_bias_regularizer = regularizers.get(bias_regularizer)
    self.ensemble_bias_constraint = constraints.get(bias_constraint)
    self.ensemble_activation = tf.keras.activations.get(activation)
    self.use_ensemble_bias = use_bias

  def build(self, input_shape):
    input_shape = tf.TensorShape(input_shape)
    super().build(input_shape)

    if self.data_format == 'channels_first':
      input_channel = input_shape[1]
    elif self.data_format == 'channels_last':
      input_channel = input_shape[-1]

    filters = input_channel * self.depth_multiplier
    self.alpha = self.add_weight(
        'alpha',
        shape=[self.ensemble_size, input_channel],
        initializer=self.alpha_initializer,
        trainable=True,
        dtype=self.dtype)
    self.gamma = self.add_weight(
        'gamma',
        shape=[self.ensemble_size, filters],
        initializer=self.gamma_initializer,
        trainable=True,
        dtype=self.dtype)
    if self.use_ensemble_bias:
      self.ensemble_bias = self.add_weight(
          name='ensemble_bias',
          shape=[self.ensemble_size, filters],
          initializer=self.ensemble_bias_initializer,
          regularizer=self.ensemble_bias_regularizer,
          constraint=self.ensemble_bias_constraint,
          trainable=True,
          dtype=self.dtype)
    else:
      self.ensemble_bias = None
    self.built = True

  def call(self, inputs):
    axis_change = -1 if self.data_format == 'channels_first' else 1
    batch_size = tf.shape(inputs)[0]
    input_dim = self.alpha.shape[-1]
    filters = self.gamma.shape[-1]
    examples_per_model = batch_size // self.ensemble_size
    alpha = tf.reshape(tf.tile(self.alpha, [1, examples_per_model]),
                       [batch_size, input_dim])
    gamma = tf.reshape(tf.tile(self.gamma, [1, examples_per_model]),
                       [batch_size, filters])
    alpha = tf.expand_dims(alpha, axis=axis_change)
    alpha = tf.expand_dims(alpha, axis=axis_change)
    gamma = tf.expand_dims(gamma, axis=axis_change)
    gamma = tf.expand_dims(gamma, axis=axis_change)
    outputs = super().call(inputs*alpha) * gamma

    if self.use_ensemble_bias:
      bias = tf.reshape(tf.tile(self.ensemble_bias, [1, examples_per_model]),
                        [batch_size, filters])
      bias = tf.expand_dims(bias, axis=axis_change)
      bias = tf.expand_dims(bias, axis=axis_change)
      outputs += bias

    if self.ensemble_activation is not None:
      outputs = self.ensemble_activation(outputs)
    return outputs

  def get_config(self):
    config = {
        'ensemble_size':
            self.ensemble_size,
        'alpha_initializer':
            initializers.serialize(self.alpha_initializer),
        'gamma_initializer':
            initializers.serialize(self.gamma_initializer),
        'ensemble_bias_initializer':
            initializers.serialize(self.bensemble_ias_initializer),
        'ensemble_bias_regularizer':
            regularizers.serialize(self.ensemble_bias_regularizer),
        'ensemble_bias_constraint':
            constraints.serialize(self.ensemble_bias_constraint),
        'ensemble_activation':
            tf.keras.activations.serialize(self.ensemble_activation),
        'use_ensemble_bias':
            self.use_ensemble_bias,
    }
    new_config = super().get_config()
    new_config.update(config)
    return new_config


@utils.add_weight
class Conv1DRank1(tf.keras.layers.Conv1D):
  """A rank-1 Bayesian NN 1D convolution layer (Dusenberry et al., 2020).

  The argument ensemble_size selects the number of mixture components over all
  weights, i.e., an ensemble of size `ensemble_size`. The layer performs a
  forward pass by enumeration, returning a forward pass under each mixture
  component. It takes an input tensor of shape
  [ensemble_size*examples_per_model,] + input_shape and returns an output tensor
  of shape [ensemble_size*examples_per_model,] + output_shape.

  To use a different batch for each mixture, take a minibatch of size
  ensemble_size*examples_per_model. To use the same batch for each mixture, get
  a minibatch of size examples_per_model and tile it by ensemble_size before
  applying any ensemble layers.
  """

  def __init__(self,
               filters,
               kernel_size,
               strides=1,
               padding='valid',
               data_format='channels_last',
               dilation_rate=1,
               activation=None,
               use_bias=True,
               alpha_initializer='trainable_normal',
               gamma_initializer='trainable_normal',
               kernel_initializer='glorot_uniform',
               bias_initializer='zeros',
               alpha_regularizer='normal_kl_divergence',
               gamma_regularizer='normal_kl_divergence',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               alpha_constraint=None,
               gamma_constraint=None,
               kernel_constraint=None,
               bias_constraint=None,
               use_additive_perturbation=False,
               min_perturbation_value=-10,
               max_perturbation_value=10,
               ensemble_size=1,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=None,
        use_bias=False,
        kernel_initializer=kernel_initializer,
        kernel_regularizer=kernel_regularizer,
        activity_regularizer=activity_regularizer,
        kernel_constraint=kernel_constraint,
        **kwargs)
    self.ensemble_activation = tf.keras.activations.get(activation)
    self.use_ensemble_bias = use_bias
    self.alpha_initializer = initializers.get(alpha_initializer)
    self.gamma_initializer = initializers.get(gamma_initializer)
    self.ensemble_bias_initializer = initializers.get(bias_initializer)
    self.alpha_regularizer = regularizers.get(alpha_regularizer)
    self.gamma_regularizer = regularizers.get(gamma_regularizer)
    self.ensemble_bias_regularizer = regularizers.get(bias_regularizer)
    self.alpha_constraint = constraints.get(alpha_constraint)
    self.gamma_constraint = constraints.get(gamma_constraint)
    self.ensemble_bias_constraint = constraints.get(bias_constraint)
    self.use_additive_perturbation = use_additive_perturbation
    self.min_perturbation_value = min_perturbation_value
    self.max_perturbation_value = max_perturbation_value
    self.ensemble_size = ensemble_size

  def build(self, input_shape):
    input_shape = tf.TensorShape(input_shape)
    super().build(input_shape)

    if self.data_format == 'channels_first':
      input_channel = input_shape[1]
    elif self.data_format == 'channels_last':
      input_channel = input_shape[-1]

    self.alpha = self.add_weight(
        'alpha',
        shape=[self.ensemble_size, input_channel],
        initializer=self.alpha_initializer,
        regularizer=self.alpha_regularizer,
        constraint=self.alpha_constraint,
        trainable=True,
        dtype=self.dtype)
    self.gamma = self.add_weight(
        'gamma',
        shape=[self.ensemble_size, self.filters],
        initializer=self.gamma_initializer,
        regularizer=self.gamma_regularizer,
        constraint=self.gamma_constraint,
        trainable=True,
        dtype=self.dtype)
    if self.use_ensemble_bias:
      self.ensemble_bias = self.add_weight(
          name='ensemble_bias',
          shape=[self.ensemble_size, self.filters],
          initializer=self.ensemble_bias_initializer,
          regularizer=self.ensemble_bias_regularizer,
          constraint=self.ensemble_bias_constraint,
          trainable=True,
          dtype=self.dtype)
      self.ensemble_bias_shape = self.ensemble_bias.shape
    else:
      self.ensemble_bias = None
      self.ensemble_bias_shape = None
    self.alpha_shape = self.alpha.shape
    self.gamma_shape = self.gamma.shape
    self.built = True

  def call(self, inputs):
    axis_change = -1 if self.data_format == 'channels_first' else 1
    batch_size = tf.shape(inputs)[0]
    input_dim = self.alpha_shape[-1]
    examples_per_model = batch_size // self.ensemble_size

    # Sample parameters for each example.
    if isinstance(self.alpha_initializer, tf.keras.layers.Layer):
      alpha = tf.clip_by_value(
          self.alpha_initializer(
              self.alpha_shape,
              self.dtype).distribution.sample(examples_per_model),
          self.min_perturbation_value,
          self.max_perturbation_value)
      alpha = tf.transpose(alpha, [1, 0, 2])
    else:
      alpha = tf.tile(self.alpha, [1, examples_per_model])
    if isinstance(self.gamma_initializer, tf.keras.layers.Layer):
      gamma = tf.clip_by_value(
          self.gamma_initializer(
              self.gamma_shape,
              self.dtype).distribution.sample(examples_per_model),
          self.min_perturbation_value,
          self.max_perturbation_value)
      gamma = tf.transpose(gamma, [1, 0, 2])
    else:
      gamma = tf.tile(self.gamma, [1, examples_per_model])

    alpha = tf.reshape(alpha, [batch_size, input_dim])
    alpha = tf.expand_dims(alpha, axis=axis_change)
    gamma = tf.reshape(gamma, [batch_size, self.filters])
    gamma = tf.expand_dims(gamma, axis=axis_change)

    if self.use_additive_perturbation:
      outputs = super().call(inputs + alpha) + gamma
    else:
      outputs = super().call(inputs * alpha) * gamma

    if self.use_ensemble_bias:
      if isinstance(self.ensemble_bias_initializer, tf.keras.layers.Layer):
        bias = self.ensemble_bias_initializer(
            self.ensemble_bias_shape,
            self.dtype).distribution.sample(examples_per_model)
        bias = tf.transpose(bias, [1, 0, 2])
      else:
        bias = tf.tile(self.ensemble_bias, [1, examples_per_model])
      bias = tf.reshape(bias, [batch_size, self.filters])
      bias = tf.expand_dims(bias, axis=axis_change)
      outputs += bias
    if self.ensemble_activation is not None:
      outputs = self.ensemble_activation(outputs)
    return outputs

  def get_config(self):
    config = {
        'ensemble_activation':
            tf.keras.activations.serialize(self.ensemble_activation),
        'use_ensemble_bias':
            self.use_ensemble_bias,
        'alpha_initializer':
            initializers.serialize(self.alpha_initializer),
        'gamma_initializer':
            initializers.serialize(self.gamma_initializer),
        'ensemble_bias_initializer':
            initializers.serialize(self.ensemble_bias_initializer),
        'alpha_regularizer':
            regularizers.serialize(self.alpha_regularizer),
        'gamma_regularizer':
            regularizers.serialize(self.gamma_regularizer),
        'ensemble_bias_regularizer':
            regularizers.serialize(self.ensemble_bias_regularizer),
        'alpha_constraint':
            constraints.serialize(self.alpha_constraint),
        'gamma_constraint':
            constraints.serialize(self.gamma_constraint),
        'ensemble_bias_constraint':
            constraints.serialize(self.ensemble_bias_constraint),
        'use_additive_perturbation':
            self.use_additive_perturbation,
        'ensemble_size':
            self.ensemble_size,
    }
    new_config = super().get_config()
    new_config.update(config)
    return new_config


@utils.add_weight
class Conv2DRank1(tf.keras.layers.Conv2D):
  """A rank-1 Bayesian NN 2D convolution layer (Dusenberry et al., 2020).

  The argument ensemble_size selects the number of mixture components over all
  weights, i.e., an ensemble of size `ensemble_size`. The layer performs a
  forward pass by enumeration, returning a forward pass under each mixture
  component. It takes an input tensor of shape
  [ensemble_size*examples_per_model,] + input_shape and returns an output tensor
  of shape [ensemble_size*examples_per_model,] + output_shape.

  To use a different batch for each mixture, take a minibatch of size
  ensemble_size*examples_per_model. To use the same batch for each mixture, get
  a minibatch of size examples_per_model and tile it by ensemble_size before
  applying any ensemble layers.
  """

  def __init__(self,
               filters,
               kernel_size,
               strides=(1, 1),
               padding='valid',
               data_format=None,
               dilation_rate=(1, 1),
               activation=None,
               use_bias=True,
               alpha_initializer='trainable_normal',
               gamma_initializer='trainable_normal',
               kernel_initializer='glorot_uniform',
               bias_initializer='zeros',
               alpha_regularizer='normal_kl_divergence',
               gamma_regularizer='normal_kl_divergence',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               alpha_constraint=None,
               gamma_constraint=None,
               kernel_constraint=None,
               bias_constraint=None,
               use_additive_perturbation=False,
               min_perturbation_value=-10,
               max_perturbation_value=10,
               ensemble_size=1,
               **kwargs):
    super().__init__(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        activation=None,
        use_bias=False,
        kernel_initializer=kernel_initializer,
        bias_initializer=None,
        kernel_regularizer=kernel_regularizer,
        bias_regularizer=None,
        activity_regularizer=activity_regularizer,
        kernel_constraint=kernel_constraint,
        bias_constraint=None,
        **kwargs)
    self.ensemble_activation = tf.keras.activations.get(activation)
    self.use_ensemble_bias = use_bias
    self.alpha_initializer = initializers.get(alpha_initializer)
    self.gamma_initializer = initializers.get(gamma_initializer)
    self.ensemble_bias_initializer = initializers.get(bias_initializer)
    self.alpha_regularizer = regularizers.get(alpha_regularizer)
    self.gamma_regularizer = regularizers.get(gamma_regularizer)
    self.ensemble_bias_regularizer = regularizers.get(bias_regularizer)
    self.alpha_constraint = constraints.get(alpha_constraint)
    self.gamma_constraint = constraints.get(gamma_constraint)
    self.ensemble_bias_constraint = constraints.get(bias_constraint)
    self.use_additive_perturbation = use_additive_perturbation
    self.min_perturbation_value = min_perturbation_value
    self.max_perturbation_value = max_perturbation_value
    self.ensemble_size = ensemble_size

  def build(self, input_shape):
    input_shape = tf.TensorShape(input_shape)
    super().build(input_shape)

    if self.data_format == 'channels_first':
      input_channel = input_shape[1]
    elif self.data_format == 'channels_last':
      input_channel = input_shape[-1]

    self.alpha = self.add_weight(
        'alpha',
        shape=[self.ensemble_size, input_channel],
        initializer=self.alpha_initializer,
        regularizer=self.alpha_regularizer,
        constraint=self.alpha_constraint,
        trainable=True,
        dtype=self.dtype)
    self.gamma = self.add_weight(
        'gamma',
        shape=[self.ensemble_size, self.filters],
        initializer=self.gamma_initializer,
        regularizer=self.gamma_regularizer,
        constraint=self.gamma_constraint,
        trainable=True,
        dtype=self.dtype)
    if self.use_ensemble_bias:
      self.ensemble_bias = self.add_weight(
          name='bias',
          shape=[self.ensemble_size, self.filters],
          initializer=self.ensemble_bias_initializer,
          regularizer=self.ensemble_bias_regularizer,
          constraint=self.ensemble_bias_constraint,
          trainable=True,
          dtype=self.dtype)
      self.bias_shape = self.ensemble_bias.shape
    else:
      self.ensemble_bias = None
      self.ensemble_bias_shape = None
    self.alpha_shape = self.alpha.shape
    self.gamma_shape = self.gamma.shape
    self.built = True

  def call(self, inputs):
    axis_change = -1 if self.data_format == 'channels_first' else 1
    batch_size = tf.shape(inputs)[0]
    input_dim = self.alpha.shape[-1]
    examples_per_model = batch_size // self.ensemble_size

    # Sample parameters for each example.
    if isinstance(self.alpha_initializer, tf.keras.layers.Layer):
      alpha = tf.clip_by_value(
          self.alpha_initializer(
              self.alpha_shape,
              self.dtype).distribution.sample(examples_per_model),
          self.min_perturbation_value,
          self.max_perturbation_value)
      alpha = tf.transpose(alpha, [1, 0, 2])
    else:
      alpha = tf.tile(self.alpha, [1, examples_per_model])
    if isinstance(self.gamma_initializer, tf.keras.layers.Layer):
      gamma = tf.clip_by_value(
          self.gamma_initializer(
              self.gamma_shape,
              self.dtype).distribution.sample(examples_per_model),
          self.min_perturbation_value,
          self.max_perturbation_value)
      gamma = tf.transpose(gamma, [1, 0, 2])
    else:
      gamma = tf.tile(self.gamma, [1, examples_per_model])

    alpha = tf.reshape(alpha, [batch_size, input_dim])
    alpha = tf.expand_dims(alpha, axis=axis_change)
    alpha = tf.expand_dims(alpha, axis=axis_change)
    gamma = tf.reshape(gamma, [batch_size, self.filters])
    gamma = tf.expand_dims(gamma, axis=axis_change)
    gamma = tf.expand_dims(gamma, axis=axis_change)

    if self.use_additive_perturbation:
      outputs = super().call(inputs + alpha) + gamma
    else:
      outputs = super().call(inputs * alpha) * gamma

    if self.use_ensemble_bias:
      if isinstance(self.ensemble_bias_initializer, tf.keras.layers.Layer):
        bias = self.ensemble_bias_initializer(
            self.ensemble_bias_shape,
            self.dtype).distribution.sample(examples_per_model)
        bias = tf.transpose(bias, [1, 0, 2])
      else:
        bias = tf.tile(self.ensemble_bias, [1, examples_per_model])
      bias = tf.reshape(bias, [batch_size, -1])
      bias = tf.expand_dims(bias, axis=axis_change)
      bias = tf.expand_dims(bias, axis=axis_change)
      outputs += bias

    if self.ensemble_activation is not None:
      outputs = self.ensemble_activation(outputs)
    return outputs

  def get_config(self):
    config = {
        'ensemble_activation':
            tf.keras.activations.serialize(self.ensemble_activation),
        'use_ensemble_bias':
            self.use_ensemble_bias,
        'alpha_initializer':
            initializers.serialize(self.alpha_initializer),
        'gamma_initializer':
            initializers.serialize(self.gamma_initializer),
        'ensemble_bias_initializer':
            initializers.serialize(self.ensemble_bias_initializer),
        'alpha_regularizer':
            regularizers.serialize(self.alpha_regularizer),
        'gamma_regularizer':
            regularizers.serialize(self.gamma_regularizer),
        'ensemble_bias_regularizer':
            regularizers.serialize(self.ensemble_bias_regularizer),
        'alpha_constraint':
            constraints.serialize(self.alpha_constraint),
        'gamma_constraint':
            constraints.serialize(self.gamma_constraint),
        'ensemble_bias_constraint':
            constraints.serialize(self.ensemble_bias_constraint),
        'use_additive_perturbation':
            self.use_additive_perturbation,
        'ensemble_size':
            self.ensemble_size,
    }
    new_config = super().get_config()
    new_config.update(config)
    return new_config
