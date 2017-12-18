ARG TF_TAG="1.4.1-py3"
# ARG TF_TAG="1.4.1-gpu-py3"
FROM tensorflow/tensorflow:${TF_TAG}

# Install apt-level dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y protobuf-compiler && \
    rm -rf /var/lib/apt/lists/*

# Get the TensorFlow models repo and install the object detection API library
RUN cd /tmp && \
    curl -o models.tar.gz https://codeload.github.com/tensorflow/models/tar.gz/edb6ed22a801665946c63d650ab9a0b23d98e1b1 && \
    tar -zxf models.tar.gz && \
    mv models-edb6ed22a801665946c63d650ab9a0b23d98e1b1 /opt/models && \
    rm models.tar.gz && \
    cd /opt/models/research && \
    protoc object_detection/protos/*.proto --python_out=.

# Get pre-trained models
RUN mkdir -p /opt/graph_def && \
    cd /tmp && \
    for model in \
      ssd_mobilenet_v1_coco_11_06_2017 \
      ssd_inception_v2_coco_11_06_2017 \
      rfcn_resnet101_coco_11_06_2017 \
      faster_rcnn_resnet101_coco_11_06_2017 \
      faster_rcnn_inception_resnet_v2_atrous_coco_11_06_2017; \
    do \
      curl -OL http://download.tensorflow.org/models/object_detection/${model}.tar.gz && \
      tar -xzf ${model}.tar.gz ${model}/frozen_inference_graph.pb && \
      mv $model /opt/graph_def/ && \
      rm ${model}.tar.gz; \
    done

# Install Python dependencies
COPY requirements.txt /app/
RUN cd /app && pip install --no-cache-dir -r requirements.txt

env PYTHONPATH=/opt/models/research:/opt/models/research/object_detection:/opt/models/research/slim

ADD object-detection-app /app/object-detection-app
WORKDIR /app/object-detection-app
CMD ["python", "app.py"]
