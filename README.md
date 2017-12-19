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

Once the container is up and running, access the app on [localhost:8000](http://localhost:8000/)
(replace `localhost` with the Docker Machine IP, if using Docker Machine).

Wait for something similar to the following lines:

```
2017-12-18 18:04:07.558019: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
 * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

## Running Pre-built Images

To run pre-built images from [Docker Hub](https://hub.docker.com/r/itamarost/object-detection-app/):

```
docker run --rm -p 8000:8000 itamarost/object-detection-app:1.0-py3
# or, using nvidia-docker
docker run --runtime=nvidia --rm -p 8000:8000 itamarost/object-detection-app:1.0-py3-gpu
```
