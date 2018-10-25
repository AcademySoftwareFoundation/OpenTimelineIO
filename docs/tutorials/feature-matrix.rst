Feature Matrix
===============

Adapters may or may not support all of the features of OpenTimelineIO or the format they convert to/from. Here is a list of features and which adapters do/don't support those features.


+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Feature                   | OTIO     | EDL            | FCPXML  | AAF       | RV         | ALE       |
+==========================+==========+================+=========+===========+============+===========+
|Single Track of Clips     | yes      | yes            | yes     | read-only | write-only | yes       |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Multiple Video Tracks     | yes      | no             | yes     | read-only | write-only | flattened |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Audio Tracks & Clips      | yes      | needs testing  | yes     | read-only | ?          | yes       |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Gap/Filler                | yes      | yes            | yes     | read-only | yes        | skipped   |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Markers                   | yes      | yes            | yes     | planned   | planned    | no        |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Nesting                   | yes      | no             | yes     | read-only | write-only | flattened |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Transitions               | yes      | yes            | planned | read-only | write-only | no        |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Audio/Video Effects       | planned  | needs research | planned | planned   | planned    | no        |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Speed Effects             | yes      | yes            | planned | read-only | planned    | no        |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+
|Color Decision List (CDL) | metadata | yes            | planned | planned   | planned    | planned   |
+--------------------------+----------+----------------+---------+-----------+------------+-----------+