# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""RV External Adapter component.

Because the rv adapter requires being run from within the RV py-interp to take
advantage of modules inside of RV, this script gets shelled out to from the
RV OTIO adapter.

Requires that you set the environment variables:
    OTIO_RV_PYTHON_LIB - should point at the parent directory of rvSession
    OTIO_RV_PYTHON_BIN - should point at py-interp from within rv
"""

# python
import sys
import os
import json

# rv import
sys.path += [os.path.join(os.environ["OTIO_RV_PYTHON_LIB"], "rvSession")]
import rvSession  # noqa


_RV_TYPE_MAP = {
    "rvSession.gto.FLOAT": rvSession.gto.FLOAT,
    "rvSession.gto.STRING": rvSession.gto.STRING,
}


# because json.loads returns a unicode type
_UNICODE_TYPE = str


def main():
    """ entry point, should be called from the rv adapter in otio """

    session_file = rvSession.Session()

    output_fname = sys.argv[1]

    simplified_data = json.loads(sys.stdin.read())
    if sys.version_info.major <= 2:
        simplified_data = _remove_unicode(simplified_data)

    result = execute_rv_commands(simplified_data, session_file)

    session_file.setViewNode(result)
    session_file.write(output_fname)


def execute_rv_commands(simplified_data, to_session):
    rv_nodes = []
    for node in simplified_data["nodes"]:
        new_node = to_session.newNode(str(node["kind"]), str(node["name"]))
        rv_node_index = len(rv_nodes)

        # make sure that node order lines up
        assert rv_node_index == node["node_index"]

        rv_nodes.append(new_node)
        node["rv_node"] = new_node

        for prop in node["properties"]:
            args = prop
            # the fourth argument is the type
            args[4] = _RV_TYPE_MAP[args[4]]

            new_node.setProperty(*args)

        for (fn, args) in node["commands"]:
            getattr(new_node, fn)(args)

    # inputs done as a second pass now that all nodes are created
    for node in simplified_data["nodes"]:
        for input in node["inputs"]:
            node["rv_node"].addInput(rv_nodes[input])

    # return the first node created.
    return rv_nodes[0]


def _remove_unicode(blob):
    if _UNICODE_TYPE == type(blob):
        return blob.encode('utf-8')

    if isinstance(blob, dict):
        result = {}
        for key, val in blob.items():
            result[_remove_unicode(key)] = _remove_unicode(val)
        return result

    if isinstance(blob, list):
        return [_remove_unicode(i) for i in blob]

    return blob


if __name__ == "__main__":
    main()
