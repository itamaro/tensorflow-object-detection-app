#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2017 Google Inc.
# Copyright 2017 Itamar Ostricher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import base64
import io
import os
import sys
import tempfile

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_wtf.file import FileField
import numpy as np
from PIL import Image
from PIL import ImageDraw
import tensorflow as tf
from utils import label_map_util
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form
from wtforms import ValidationError

from decorator import requires_auth


app = Flask(__name__)


@app.before_request
@requires_auth
def before_request():
  pass


GRAPH_DEF_BASE = '/opt/graph_def'
MODEL = os.environ.get(
    'MODEL', 'faster_rcnn_inception_resnet_v2_atrous_coco_11_06_2017')
PATH_TO_LABELS = (
    '/opt/models/research/object_detection/data/mscoco_label_map.pbtxt')

CONTENT_TYPES = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}
EXTENSIONS = sorted(CONTENT_TYPES.keys())


def is_image():
  def _is_image(form, field):
    if not field.data:
      raise ValidationError()
    elif field.data.filename.split('.')[-1].lower() not in EXTENSIONS:
      raise ValidationError()

  return _is_image


class PhotoForm(Form):
  input_photo = FileField(
      'File extension should be: %s (case-insensitive)' % ', '.join(EXTENSIONS),
      validators=[is_image()])


class ObjectDetector():

  def __init__(self):
    self.detection_graph = self._build_graph()
    self.sess = tf.Session(graph=self.detection_graph)

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True)
    self.category_index = label_map_util.create_category_index(categories)

  def _build_graph(self):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(
          os.path.join(GRAPH_DEF_BASE, MODEL, 'frozen_inference_graph.pb'),
          'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    return detection_graph

  def _load_image_into_numpy_array(self, image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

  def detect(self, image):
    image_np = self._load_image_into_numpy_array(image)
    image_np_expanded = np.expand_dims(image_np, axis=0)
    graph = self.detection_graph
    image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
    boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
    scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
    classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
    boxes, scores, classes = self.sess.run(
        [boxes, scores, classes],
        feed_dict={image_tensor: image_np_expanded})
    boxes, scores, classes = map(np.squeeze, [boxes, scores, classes])
    return boxes, scores, classes.astype(int)


def draw_bounding_box_on_image(image, box, color='red', thickness=4):
  draw = ImageDraw.Draw(image)
  im_width, im_height = image.size
  ymin, xmin, ymax, xmax = box
  (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                ymin * im_height, ymax * im_height)
  draw.line([(left, top), (left, bottom), (right, bottom),
             (right, top), (left, top)], width=thickness, fill=color)


def encode_image(image):
  image_buffer = io.BytesIO()
  image.save(image_buffer, format='PNG')
  imgstr = 'data:image/png;base64,{:s}'.format(
      base64.b64encode(image_buffer.getvalue()).decode('utf-8'))
  return imgstr


def detect_objects(image_path):
  image = Image.open(image_path).convert('RGB')
  boxes, scores, classes = client.detect(image)
  image.thumbnail((480, 480), Image.ANTIALIAS)

  new_images = {}
  for box, score, obj_class in zip(boxes, scores, classes):
    if score < 0.7:
      continue
    if obj_class not in new_images.keys():
      new_images[obj_class] = image.copy()
    draw_bounding_box_on_image(new_images[obj_class], box,
                               thickness=int(score * 10) - 4)

  result = {}
  result['original'] = encode_image(image.copy())

  for obj_class, new_image in new_images.items():
    category = client.category_index[obj_class]['name']
    result[category] = encode_image(new_image)

  return result


@app.route('/')
def upload():
  photo_form = PhotoForm(request.form)
  return render_template('upload.html', photo_form=photo_form, result={})


@app.route('/post', methods=['GET', 'POST'])
def post():
  form = PhotoForm(CombinedMultiDict((request.files, request.form)))
  if request.method == 'POST' and form.validate():
    with tempfile.NamedTemporaryFile() as temp:
      form.input_photo.data.save(temp)
      temp.flush()
      result = detect_objects(temp.name)

    photo_form = PhotoForm(request.form)
    return render_template('upload.html',
                           photo_form=photo_form, result=result)
  else:
    return redirect(url_for('upload'))


client = ObjectDetector()


if __name__ == '__main__':
  debug = os.environ.get('DEBUG', 'no').lower() in ('y', 'yes', 'true', '1')
  port = int(os.environ.get('PORT', '8000'))
  app.run(host='0.0.0.0', port=port, debug=debug)
