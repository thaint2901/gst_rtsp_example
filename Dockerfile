# docker run -d --name gstreamer \
#     -p 8554:8554 \
#     -v /mnt/sda2/ExternalHardrive/research/video_streaming/rtsp:/workspace \
#     -it thaint2901/own_repo:gstreamer-0.1-base

FROM ubuntu:18.04 as base

ARG PORT=8554

# Install dependence
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3 \
    python3-pip python3-dev wget curl \
    libcurl4-openssl-dev libb64-dev \
    iputils-ping libsm6 libxext6 libxrender-dev \
    libgl1-mesa-glx unzip build-essential cmake

# Install gstreamer
RUN apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudi

ENV PORT=${PORT}

EXPOSE ${PORT}
RUN mkdir /workspace
WORKDIR /workspace
