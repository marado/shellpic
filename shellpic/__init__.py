#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2014
#

from formatter import *
from shell import *
from irc import *

import PIL
import collections

VERSION = "1.3"

def scale(anim, width, height):
    """
    Scale an Animation while preserving the aspect ratio
    """
    imgwidth, imgheight = anim.image.size

    scalewidth = 1
    scaleheight = 1

    if imgwidth > width:
        scalewidth = float(width) / (imgwidth + 2)
    if imgheight > height * 2:
        scaleheight = float((height - 1) * 2) / imgheight
    scale = min(scaleheight, scalewidth)

    return anim.resize((int(imgwidth * scale), int(imgheight * scale)))


def ensure_rgb(palette, pixel):
    """
    Return the an rgb tuple for pixel, look it up in palette if
    necessary.
    """
    if isinstance(pixel, collections.Sequence):
        return pixel[:3]
    else:
        return palette_lookup(palette, pixel)

def ensure_rgba(palette, pixel):
    """
    Return the an rgba tuple for pixel, look it up in palette if
    necessary.
    """
    if isinstance(pixel, collections.Sequence):
        if len(pixel) == 3:
            return [pixel[0], pixel[1], pixel[2], 255]
        else:
            return pixel
    else:
        return palette_lookup(palette, pixel)


def palette_lookup(palette, index):
    """
    Return the rgb value stored in the palette at the supplied index.
    """
    return ord(palette.palette[3 * index]), ord(palette.palette[(3 * index) + 1]), ord(palette.palette[(3 * index) + 2])


def pixels(image):
    """
    Return the pixel values from an Image as a two-dimentional list.
    """
    width, height = image.size
    data = list(image.getdata())
    return [[data[(y * width) + x] for y in range(height)] for x in range(width)]

def pixel_copy(src):
    """
    Return a copy of src by copying each pixel using getpixel()
    getpixel().

    This is slow, but it seems to be the only way to get Image from an
    ImagingCore object.
    """
    width, height = src.size
    dst = PIL.Image.new(src.mode, src.size)
    for x in range(width):
        for y in range(height):
            dst.putpixel((x, y), src.getpixel((x, y)))
    return dst
