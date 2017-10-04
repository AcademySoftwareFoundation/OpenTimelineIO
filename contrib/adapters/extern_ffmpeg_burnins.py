# MIT License
#
# Copyright (c) 2017 Ed Caspersen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# allcopies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
This module provides an interface to allow users to easily
build out an FFMPEG command with all the correct filters
for applying text (with a background) to the rendered media.
"""
import os
import sys
import json
from subprocess import Popen, PIPE
from PIL import ImageFont


def _system_font():
    """
    attempts to determine a default system font

    :rtype: str
    """
    if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts')
        fonts = ('arial.ttf', 'calibri.ttf', 'times.ttf')
    elif sys.platform.startswith('darwin'):
        font_path = '/System/Library/Fonts'
        fonts = ('Menlo.ttc',)
    else:
        # assuming linux
        font_path = 'usr/share/fonts/msttcorefonts'
        fonts = ('arial.ttf', 'times.ttf', 'couri.ttf')

    system_font = None
    for font in fonts:
        font = os.path.join(font_path, font)
        if os.path.exists(font):
            system_font = font
            break
    else:
        raise OSError("Could not determine system font.")
    return system_font


# Default valuues
FONT = _system_font()
FONT_SIZE = 16
FONT_COLOR = 'white'
BG_COLOR = 'black'
BG_PADDING = 5

# FFMPEG command strings
FFMPEG = ('ffmpeg -loglevel panic -i %(input)s '
          '%(filters)s %(args)s%(output)s')
FFPROBE = ('ffprobe -v quiet -print_format json -show_format '
           '-show_streams %(source)s')
DRAWBOX = 'drawbox=%(x)d:%(y)d:%(w)d:%(h)d:%(color)s@%(opacity).1f:t=max'
DRAWTEXT = ("drawtext=text='%(text)s':x=%(x)s:y=%(y)s:fontcolor="
            "%(color)s@%(opacity).1f:fontsize=%(size)d:fontfile=%(font)s")

# Valid aligment parameters.
TOP_CENTERED = 'top_centered'
BOTTOM_CENTERED = 'bottom_centered'
TOP_LEFT = 'top_left'
BOTTOM_LEFT = 'bottom_left'
TOP_RIGHT = 'top_right'
BOTTOM_RIGHT = 'bottom_right'


class Options(dict):
    """
    Base options class.
    """
    _params = {
        'opacity': 1,
        'x_offset': 0,
        'y_offset': 0,
        'font': FONT,
        'font_size': FONT_SIZE,
        'bg_color': BG_COLOR,
        'bg_padding': BG_PADDING,
        'font_color': FONT_COLOR
    }

    def __init__(self, **kwargs):
        super(Options, self).__init__()
        params = self._params.copy()
        params.update(kwargs)
        super(Options, self).update(**params)

    def __setitem__(self, key, value):
        if key not in self._params:
            raise KeyError("Not a valid option key '%s'" % key)
        super(Options, self).update({key: value})


class FrameNumberOptions(Options):
    """
    :key int frame_offset: offset the frame numbers
    :key float opacity: opacity value (0-1)
    :key str expression: expression that would be used instead of text
    :key bool x_offset: X position offset
                         (does not apply to centered alignments)
    :key bool y_offset: Y position offset
    :key str font: path to the font file
    :key int font_size: size to render the font in
    :key str bg_color: background color of the box
    :key int bg_padding: padding between the font and box
    :key str font_color: color to render
    """

    def __init__(self, **kwargs):
        self._params.update({
            'frame_offset': 0,
            'expression': None
        })
        super(FrameNumberOptions, self).__init__(**kwargs)


class TextOptions(Options):
    """
    :key float opacity: opacity value (0-1)
    :key str expression: expression that would be used instead of text
    :key bool x_offset: X position offset
                        (does not apply to centered alignments)
    :key bool y_offset: Y position offset
    :key str font: path to the font file
    :key int font_size: size to render the font in
    :key str bg_color: background color of the box
    :key int bg_padding: padding between the font and box
    :key str font_color: color to render
    """


class Burnins(object):
    """
    Class that provides convenience API for building filter
    flags for the FFMPEG command.
    """

    def __init__(self, source, streams=None):
        """
        :param str source: source media file
        :param [] streams: ffprobe stream data if parsed as a pre-process
        """
        self.source = source
        self.filters = {
            'drawbox': [],
            'drawtext': []
        }
        self._streams = streams or _streams(self.source)

    def __repr__(self):
        return '<Overlayout - %s>' % os.path.basename(self.source)

    @property
    def start_frame(self):
        """
        :rtype: int
        """
        start_time = float(self._video_stream['start_time'])
        return round(start_time * self.frame_rate)

    @property
    def end_frame(self):
        """
        :rtype: int
        """
        end_time = float(self._video_stream['duration'])
        return round(end_time * self.frame_rate)

    @property
    def frame_rate(self):
        """
        :rtype: int
        """
        data = self._video_stream
        return int(data['r_frame_rate'].split('/')[0])

    @property
    def _video_stream(self):
        video_stream = None
        for each in self._streams:
            if each.get('codec_type') == 'video':
                video_stream = each
                break
        else:
            raise RuntimeError("Failed to locate video stream "
                               "from '%s'" % self.source)
        return video_stream

    @property
    def resolution(self):
        """
        :rtype: (int, int)
        """
        data = self._video_stream
        return data['width'], data['height']

    @property
    def filter_string(self):
        """
        Generates the filter string that would be applied
        to the `-vf` argument

        :rtype: str
        """
        return ','.join(self.filters['drawbox'] +
                        self.filters['drawtext'])

    def add_frame_numbers(self, align, options=None):
        """
        Convenience method to create the frame number expression.

        :param enum align: alignment, must use provided enum flags
        :param dict options: recommended to use FrameNumberOptions
        """
        options = options or FrameNumberOptions()
        options['expression'] = r'%%{eif\:n+%d\:d}' % options['frame_offset']
        text = str(int(self.end_frame + options['frame_offset']))
        self._add_burnin(text, align, options)

    def add_text(self, text, align, options=None):
        """
        Adding static text to a filter.

        :param str text: text to apply to the drawtext
        :param enum align: alignment, must use provided enum flags
        :param dict options: recommended to use TextOptions
        """
        options = options or TextOptions()
        self._add_burnin(text, align, options)

    def _add_burnin(self, text, align, options):
        """
        Generic method for building the filter flags.

        :param str text: text to apply to the drawtext
        :param enum align: alignment, must use provided enum flags
        :param dict options:
        """
        ifont = ImageFont.truetype(options['font'],
                                   options['font_size'])
        bg_size = ifont.getsize(text)
        data = {
            'w': bg_size[0]+options['bg_padding'],
            'h': bg_size[1]+(options['bg_padding']/2),
            'color': options['bg_color'],
            'opacity': options['opacity']
        }
        resolution = self.resolution
        data.update(_drawbox(align, resolution,
                             bg_size,
                             [options['x_offset'],
                              options['y_offset']]))
        self.filters['drawbox'].append(DRAWBOX % data)

        data = {
            'text': options.get('expression') or text,
            'color': options['font_color'],
            'size': options['font_size'],
            'font': options['font'],
            'opacity': options['opacity']
        }
        data.update(_drawtext(align, resolution,
                              bg_size,
                              [options['x_offset'],
                               options['y_offset']],
                              options['bg_padding']))
        self.filters['drawtext'].append(DRAWTEXT % data)

    def command(self, output=None, args=None, overwrite=False):
        """
        Generate the entire FFMPEG command.

        :param str output: output file
        :param str args: additional FFMPEG arguments
        :param bool overwrite: overwrite the output if it exists
        :returns: completed command
        :rtype: str
        """
        output = output or ''
        if overwrite:
            output = '-y %s' % output
        return (FFMPEG % {
            'input': self.source,
            'output': output,
            'args': '%s ' % args if args else '',
            'filters': '-vf "%s"' % self.filter_string
        }).strip()

    def render(self, output, args=None, overwrite=False):
        """
        Render the media to a specified destination.

        :param str output: output file
        :param str args: additional FFMPEG arguments
        :param bool overwrite: overwrite the output if it exists
        """
        if not overwrite and os.path.exists(output):
            raise RuntimeError("Destination '%s' exists, please "
                               "use overwrite" % output)
        command = self.command(output=output,
                               args=args,
                               overwrite=overwrite)
        proc = Popen(command, shell=True)
        proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("Failed to render '%s': %s'"
                               % (output, command))
        if not os.path.exists(output):
            raise RuntimeError("Failed to generate '%s'" % output)


def _streams(source):
    """
    :param str source: source media file
    :rtype: [{}, ...]
    """
    command = FFPROBE % {'source': source}
    proc = Popen(command, shell=True, stdout=PIPE)
    out = proc.communicate()[0]
    if proc.returncode != 0:
        raise RuntimeError("Failed to run: %s" % command)
    return json.loads(out)['streams']


def _drawbox(align, resolution, bg_size, offset):
    """
    :rtype: {'x': int, 'y': int}
    """
    x_pos = 0
    if align in (TOP_CENTERED, BOTTOM_CENTERED):
        x_pos = (resolution[0] - bg_size[0]) / 2
    elif align in (TOP_LEFT, BOTTOM_LEFT):
        x_pos = offset[0]
    elif align in (TOP_RIGHT, BOTTOM_RIGHT):
        x_pos = resolution[0] - (bg_size[0] + offset[0])
    else:
        raise RuntimeError("Unknown alignment '%s'" % str(align))

    y_pos = 0
    if align in (BOTTOM_CENTERED,
                 BOTTOM_LEFT,
                 BOTTOM_RIGHT):
        y_pos = resolution[1] - bg_size[1]
        offset[1] *= -1
    return {'x': x_pos, 'y': y_pos + offset[1]}


def _drawtext(align, resolution, bg_size, offset, padding):
    """
    :rtype: {'x': int, 'y': int}
    """
    x_pos = '0'
    if align in (TOP_CENTERED, BOTTOM_CENTERED):
        x_pos = 'w/2-tw/2+%d' % (padding/2)
    elif align in (TOP_RIGHT, BOTTOM_RIGHT):
        x_pos = resolution[0] - (bg_size[0] + offset[0])
        x_pos += (padding/2)
    elif align in (TOP_LEFT, BOTTOM_LEFT):
        x_pos = offset[0]
        x_pos += (padding/2)

    if align in (TOP_CENTERED,
                 TOP_RIGHT,
                 TOP_LEFT):
        y_pos = '%d' % (offset[1] + padding)
    else:
        y_pos = 'h-text_h-%d' % (offset[1] + padding)
    return {'x': x_pos, 'y': y_pos}
