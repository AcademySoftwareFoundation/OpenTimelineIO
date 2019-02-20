Feature Matrix
===============

Adapters may or may not support all of the features of OpenTimelineIO or the format they convert to/from. Here is a list of features and which adapters do/don't support those features.


+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Feature                   | OTIO     | EDL            | FCP7 XML | AAF       | RV         | ALE       | FCPX XML  |
+==========================+==========+================+==========+===========+============+===========+===========+
|Single Track of Clips     | yes      | yes            | yes      | read-only | write-only | yes       | yes       |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Multiple Video Tracks     | yes      | no             | yes      | read-only | write-only | flattened | yes       |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Audio Tracks & Clips      | yes      | needs testing  | yes      | read-only | ?          | yes       | yes       |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Gap/Filler                | yes      | yes            | yes      | read-only | yes        | skipped   | yes       |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Markers                   | yes      | yes            | yes      | planned   | planned    | no        | yes       |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Nesting                   | yes      | no             | yes      | read-only | write-only | flattened | yes       |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Transitions               | yes      | yes            | planned  | read-only | write-only | no        | planned   |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Audio/Video Effects       | planned  | needs research | planned  | planned   | planned    | no        | planned   |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Speed Effects             | yes      | yes            | planned  | read-only | planned    | no        | planned   |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+
|Color Decision List (CDL) | metadata | yes            | planned  | planned   | planned    | planned   | no        |
+--------------------------+----------+----------------+----------+-----------+------------+-----------+-----------+