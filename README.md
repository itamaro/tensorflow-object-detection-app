# TensorFlow Object Detection web app

Based on [a demo app by GoogleCloudPlatform](https://github.com/GoogleCloudPlatform/tensorflow-object-detection-example), using TensorFlow with pre-trained models to implement a dockerized general object detection service.

See also the [Google Solution](https://cloud.google.com/solutions/creating-object-detection-application-tensorflow).

## Build & Run

The default version (non-GPU):

```
docker build -t object-detection-app:latest .
docker run --rm -p 8000:8000 object-detection-app:latest
```

The GPU version (requires [NVIDIA-Docker](https://github.com/NVIDIA/nvidia-docker)):

```
docker build -t object-detection-app:gpu .
docker run --runtime=nvidia --rm -p 8000:8000 object-detection-app:gpu
```
