# Face_recognition-in-Raspberry-Pi
All steps below are done in raspberry pi
1. Install the required dependencies:

sudo apt-get update
sudo apt-get install -y build-essential cmake gfortran git wget curl graphicsmagick libgraphicsmagick1-dev libatlas-base-dev libavcodec-dev libavformat-dev libboost-all-dev libgtk2.0-dev libjpeg-dev liblapack-dev libswscale-dev pkg-config python3-dev python3-numpy python3-pip zlib1g-dev

2.Install dlib:
wget --no-check-certificate https://dlib.net/files/dlib-19.22.tar.bz2
tar xvf dlib-19.22.tar.bz2
sudo pip3 install dlib
(Details please check on your own)

3.Install face_recognition:
sudo pip3 install face_recognition

4. Install some other required library e.g dumpy

5. Put a jpg under the same directory with 'faceRecognition.py' to register face

6. Edit codes in 'faceRecognition.py' for loading put image

7. Run 'faceRecognition.py' with 'python faceRecognition.py'