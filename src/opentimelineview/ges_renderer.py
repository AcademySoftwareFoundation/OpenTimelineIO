import sys

from PySide2 import QtWidgets
from PySide2.QtCore import QTimer, QUrl
from PySide2.QtGui import QDesktopServices

try:
    import gi

    gi.require_version('GObject', '2.0')
    gi.require_version('Gst', '1.0')
    gi.require_version('GstPbutils', '1.0')
    gi.require_version('GES', '1.0')

    from gi.repository import GObject
    from gi.repository import Gst
    from gi.repository import GstPbutils
    from gi.repository import GES
    Gst.init(sys.argv)
    GES.init()
except ImportError:
    GES = None


class Renderer(QtWidgets.QProgressDialog):
    def __init__(self, project_file, output_file, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)

        self.pipeline = GES.Pipeline()
        self.output_uri = Gst.filename_to_uri(output_file)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_position_callback)

        project = GES.Project(uri=Gst.filename_to_uri(project_file))
        timeline = project.extract()
        self.pipeline.set_timeline(timeline)
        self.pipeline.set_render_settings(self.output_uri,
                                          self.get_encoding_profile())
        self.pipeline.set_mode(GES.PipelineFlags.RENDER)
        self.pipeline.set_state(Gst.State.PLAYING)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._bus_message_callback)

        self.setWindowTitle('OpenTimelineIO renderer')
        self.show()
        self.raise_()

    def get_encoding_profile(self):
        v = GObject.Value()
        v.init(GObject.TYPE_STRING)
        v.set_string('video/x-matroska:image/jpeg:audio/x-opus')
        ov = GObject.Value()
        ov.init(GstPbutils.EncodingProfile)
        v.transform(ov)

        return ov.get_object()

    def _bus_message_callback(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            self.timer.stop()
            self.setValue(self.maximum())
            QDesktopServices.openUrl(QUrl(self.output_uri))
        elif message.type == Gst.MessageType.ERROR:
            self.pipeline.set_state(Gst.State.NULL)
            gerror, debug = message.parse_error()

            error = QtWidgets.QErrorMessage(parent=self)
            error.showMessage("ERROR: {}\n\n{}".format(gerror.message, debug))
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if message.src != self.pipeline:
                return

            _, new_state, _ = message.parse_state_changed()
            if new_state == Gst.State.PLAYING:
                duration = self.pipeline.query_duration(Gst.Format.TIME)[1]
                self.setMinimum(0)
                self.setMaximum(duration / Gst.SECOND)
                self.timer.start()

    def _update_position_callback(self):
        self.setValue(self.pipeline.query_position(Gst.Format.TIME)[1] / Gst.SECOND)


if not GES:
    Renderer = None  # noqa