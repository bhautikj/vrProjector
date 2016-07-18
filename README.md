# vrProjector

vrProjector is a python library and command-line tool to convert from one type of spherical projection to another. Currently it supports converting between Equirectangular, Cubemaps and Side-by-Side fisheye projections.

### Prerequisites

You'll need the python imaging library; I've found it's best to get it via Pillow:

```sh
$ pip install Pillow
```

### Running vrProjector on the command line

You can run vrProjector simply by running the ```vrProjectorCmd``` shell script on the command-line. You'll need to specify the source and output projection types as well as the source/output images and paramaters themselves. For example, use this to turn an equirectangular image into a set of 128x128 pixel cubemap faces:

```sh
$ ./vrProjectorCmd --sourceProjection Equirectangular --sourceImage images\equirectangular.jpg --sourceProjection Equirectangular --outProjection CubeMap --outImage "front.png right.png back.png left.png top.png bottom.png" --outWidth 128 --outHeight 128
```

This converts an input equirectangular image into a 2048x1024 pixel side-by-side fisheye projection:

```sh
$ ./vrProjectorCmd --sourceProjection Equirectangular --sourceImage images\equirectangular.jpg --sourceProjection Equirectangular --outProjection SideBySideFisheye --outImage foo.png --outWidth 2048 --outHeight 1024
```

You can access the full set of available commands via the ```-h``` switch:

```sh
$ ./vrProjectorCmd -h
usage: vrProjectorWrapper.py [-h] --sourceProjection SOURCEPROJECTION
                             --sourceImage SOURCEIMAGE
                             [--useBilnear USEBILNEAR] --outProjection
                             OUTPROJECTION --outImage OUTIMAGE --outWidth
                             OUTWIDTH --outHeight OUTHEIGHT

Reproject photospheres

optional arguments:
  -h, --help            show this help message and exit
  --sourceProjection SOURCEPROJECTION
                        Type of source projection. Valid values are:
                        Equirectangular, Cubemap, SideBySideFisheye
  --sourceImage SOURCEIMAGE
                        Source image[s]. List multiple images in double quotes
                        like so "front.png right.png back.png left.png top.png
                        bottom.png"
  --useBilnear USEBILNEAR
                        Use bilinear interpolation when reprojecting. Valid
                        values are true and false.
  --outProjection OUTPROJECTION
                        Type of output projection. Valid values are:
                        Equirectangular, Cubemap, SideBySideFisheye
  --outImage OUTIMAGE   output image[s]. List multiple images in double quotes
                        like so "front.png right.png back.png left.png top.png
                        bottom.png"
  --outWidth OUTWIDTH   output image[s] width in pixels
  --outHeight OUTHEIGHT
                        output image[s] height in pixels
```

### Running vrProjector in python
