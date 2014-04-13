#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2014
#

from PIL import Image
import shellpic

class Animation(object):
    """
    Helper class for managing images, it have the following
    properties:

    * frames - a list of PIL.Images
    * partial_frames - a list of PIL.Images, where the pixels that are
      unchanged from the previus frame are transparent.
    * bg_color - the background color
    * delay in ms between each frame


    Non-animated images are treated as animations consisting of a
    single frame.
    """
    def __init__(self, image):
        super(Animation, self).__init__()

        self.partial_frames = [] # used to redraw pixels that have changed since the last frame
        self.frames = [] # used to redraw all pixels
        self.delay = 0 # ms between each frame
        self.bg_color = [0, 0, 0, 255]
        self.transparency = None
        self.image = image
        self.mode = image.mode


        if 'background' in image.info:
            self.bg_color = shellpic.ensure_rgba(image.palette, image.info['background'])
        if 'duration' in image.info:
            self.delay = float(image.info['duration']) / 1000
        if 'transparency' in image.info:
            self.transparency = shellpic.ensure_rgba(image.palette, image.info['transparency'])

        self._raw_frames = []
        self._raw_disposes = []
        while True:
            try:
                if hasattr(image, 'dispose') and image.dispose:
                    self._raw_disposes.append(image.dispose)
                else:
                    self._raw_disposes.append(None)
                self._raw_frames.append(image.copy())
                image.seek(image.tell() + 1)
            except EOFError:
                break

    def load(self):
        """
        Load the image and store the resulting frames in the frames
        property.
        """
        background = Image.new('RGBA', self._raw_frames[0].size, self.bg_color)
        for raw_frame, dispose in zip(self._raw_frames, self._raw_disposes):

            frame = Image.new('RGBA', raw_frame.size)
            width, height = raw_frame.size
            for x in range(width):
                for y in range(height):
                    pixel = raw_frame.getpixel((x, y))
                    if not pixel[3]:
                        if not dispose:
                            pixel = background.getpixel((x, y))
                        else:
                            pixel = self.bg_color

                    frame.putpixel((x, y), pixel)
                    background.putpixel((x, y), pixel)
            self.frames.append(frame)


    def resize(self, size):
        """
        Resise the animation.
        """
        for i in range(len(self._raw_frames)):
            try:
                self._raw_frames[i] = self._raw_frames[i].resize(size, Image.ANTIALIAS)
                if self._raw_disposes[i]:
                    self._raw_disposes[i] = self._raw_disposes[i].resize(size, Image.ANTIALIAS)
            except ValueError:
                # the above fails seemingly at random with ValueError: unknown filter
                self._raw_frames[i] = self._raw_frames[i].resize(size)
                if self._raw_disposes[i]:
                    self._raw_disposes[i] = self._raw_disposes[i].resize(size)

    def convert(self, mode):
        """
        Change the color mode of the animation.
        """
        if self.mode != mode:
            for i in range(len(self._raw_frames)):
                self._raw_frames[i] = self._raw_frames[i].convert(mode)
                if self._raw_disposes[i]:
                    self._raw_disposes[i] = self._raw_disposes[i].convert(mode)

            self.mode = mode




class Formatter(object):
    """
    A Formatter creates a string of unicode characters and escape
    codes that it shows a picture when viewed in the correct context,
    usually a terminal emulator.

    This is an abstract class.
    """

    def __init__(self):
        super(Formatter, self).__init__()
        self._origin = None # cursor position where we put the upper left pixel

    def format(self, image, dispose=None):
        """
        Convert image to a string and return it. Get background color
        from dispose for transparent pixels.
        """
        raise NotImplementedError()

    @staticmethod
    def dimensions():
        """
        Return a hint to the maximum image size suitable for this
        formatter.
        """
        raise NotImplementedError()

    def move_cursor(self, pos_x, pos_y):
        """
        Return a string containing the command to move the cursor to a
        position.
        """
        raise NotImplementedError()

    @staticmethod
    def save_cursor():
        """
        Return a string containing a command to save the cursor
        position.
        """
        raise NotImplementedError()

    @staticmethod
    def restore_cursor():
        """
        Return a string containing a command to restore the cursor
        position.
        """
        raise NotImplementedError()

    @staticmethod
    def clear_screen():
        """
        Return a string containing a command to clear the drawing
        area.
        """
        raise NotImplementedError()
