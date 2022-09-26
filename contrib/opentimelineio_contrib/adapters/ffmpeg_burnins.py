# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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


def _is_windows():
    """
    queries if the current operating system is Windows

    :rtype: bool
    """
    return sys.platform.startswith('win') or \
        sys.platform.startswith('cygwin')


def _system_font():
    """
    attempts to determine a default system font

    :rtype: str
    """
    if _is_windows():
        font_path = os.path.join(os.environ['WINDIR'], 'Fonts')
        fonts = ('arial.ttf', 'calibri.ttf', 'times.ttf')
    elif sys.platform.startswith('darwin'):
        font_path = '/System/Library/Fonts'
        fonts = ('Menlo.ttc',)
    else:
        # assuming linux
        font_path = '/usr/share/fonts/msttcorefonts'
        fonts = ('arial.ttf', 'times.ttf', 'couri.ttf')

    system_font = None
    backup = None
    for font in fonts:
        font = os.path.join(font_path, font)
        if os.path.exists(font):
            system_font = font
            break
    else:
        if os.path.exists(font_path):
            for each in os.listdir(font_path):
                ext = os.path.splitext(each)[-1]
                if ext[1:].startswith('tt'):
                    system_font = os.path.join(font_path, each)
    return system_font or backup


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
BOX = 'box=1:boxborderw=%(border)d:boxcolor=%(color)s@%(opacity).1f'
DRAWTEXT = ("drawtext=text='%(text)s':x=%(x)s:y=%(y)s:fontcolor="
            "%(color)s@%(opacity).1f:fontsize=%(size)d:fontfile='%(font)s'")
TIMECODE = ("drawtext=timecode='%(text)s':timecode_rate=%(fps).2f"
            ":x=%(x)s:y=%(y)s:fontcolor="
            "%(color)s@%(opacity).1f:fontsize=%(size)d:fontfile='%(font)s'")


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
        super().__init__()
        params = self._params.copy()
        params.update(kwargs)
        super().update(**params)

    def __setitem__(self, key, value):
        if key not in self._params:
            raise KeyError("Not a valid option key '%s'" % key)
        super().update({key: value})


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
        super().__init__(**kwargs)


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


class TimeCodeOptions(Options):
    """
    :key int frame_offset: offset the frame numbers
    :key float fps: frame rate to calculate the timecode by
    :key float opacity: opacity value (0-1)
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
            'fps': 24
        })
        super().__init__(**kwargs)


class Burnins:
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
        tokens = data['r_frame_rate'].split('/')
        return int(tokens[0]) / int(tokens[1])

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
        return ','.join(self.filters['drawtext'])

    def add_timecode(self, align, options=None):
        """
        Convenience method to create the frame number expression.

        :param enum align: alignment, must use provided enum flags
        :param dict options: recommended to use TimeCodeOptions
        """
        options = options or TimeCodeOptions()
        timecode = _frames_to_timecode(options['frame_offset'],
                                       self.frame_rate)
        options = options.copy()
        if not options.get('fps'):
            options['fps'] = self.frame_rate
        self._add_burnin(timecode.replace(':', r'\:'),
                         align,
                         options,
                         TIMECODE)

    def add_frame_numbers(self, align, options=None):
        """
        Convenience method to create the frame number expression.

        :param enum align: alignment, must use provided enum flags
        :param dict options: recommended to use FrameNumberOptions
        """
        options = options or FrameNumberOptions()
        options['expression'] = r'%%{eif\:n+%d\:d}' % options['frame_offset']
        text = str(int(self.end_frame + options['frame_offset']))
        self._add_burnin(text, align, options, DRAWTEXT)

    def add_text(self, text, align, options=None):
        """
        Adding static text to a filter.

        :param str text: text to apply to the drawtext
        :param enum align: alignment, must use provided enum flags
        :param dict options: recommended to use TextOptions
        """
        options = options or TextOptions()
        self._add_burnin(text, align, options, DRAWTEXT)

    def _add_burnin(self, text, align, options, draw):
        """
        Generic method for building the filter flags.

        :param str text: text to apply to the drawtext
        :param enum align: alignment, must use provided enum flags
        :param dict options:
        """
        resolution = self.resolution
        data = {
            'text': options.get('expression') or text,
            'color': options['font_color'],
            'size': options['font_size']
        }
        data.update(options)
        data.update(_drawtext(align, resolution, text, options))
        if 'font' in data and _is_windows():
            data['font'] = data['font'].replace(os.sep, r'\\' + os.sep)
            data['font'] = data['font'].replace(':', r'\:')
        self.filters['drawtext'].append(draw % data)

        if options.get('bg_color') is not None:
            box = BOX % {
                'border': options['bg_padding'],
                'color': options['bg_color'],
                'opacity': options['opacity']
            }
            self.filters['drawtext'][-1] += ':%s' % box

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


def _drawtext(align, resolution, text, options):
    """
    :rtype: {'x': int, 'y': int}
    """
    x_pos = '0'
    if align in (TOP_CENTERED, BOTTOM_CENTERED):
        x_pos = 'w/2-tw/2'
    elif align in (TOP_RIGHT, BOTTOM_RIGHT):
        ifont = ImageFont.truetype(options['font'],
                                   options['font_size'])
        box_size = ifont.getsize(text)
        x_pos = resolution[0] - (box_size[0] + options['x_offset'])
    elif align in (TOP_LEFT, BOTTOM_LEFT):
        x_pos = options['x_offset']

    if align in (TOP_CENTERED,
                 TOP_RIGHT,
                 TOP_LEFT):
        y_pos = '%d' % options['y_offset']
    else:
        y_pos = 'h-text_h-%d' % (options['y_offset'])
    return {'x': x_pos, 'y': y_pos}


def _frames_to_timecode(frames, framerate):
    return '{:02d}:{:02d}:{:02d}:{:02d}'.format(
        int(frames / (3600 * framerate)),
        int(frames / (60 * framerate) % 60),
        int(frames / framerate % 60),
        int(frames % framerate))
