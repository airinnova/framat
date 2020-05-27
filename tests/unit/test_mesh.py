#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mesh test
"""

from mframework._log import disable_logger, enable_logger
# disable_logger()
enable_logger()

import pytest

import framat._meshing as m


def test_point():
    """Test Point()"""

    # UID must be string
    with pytest.raises(AssertionError):
        m.Point([0, 1, 2], uid=42)

    # Point must have three coordinates
    with pytest.raises(AssertionError):
        m.Point([0, 1], uid='a')

    # OK
    p = m.Point([0, 1, 2], uid='a')
    assert p.uid == 'a'
    assert p.coord.tolist() == [0, 1, 2]


def test_line_segment():
    p1 = m.Point([0, 2, 5], uid='a')
    p2 = m.Point([3, 2, 5], uid='b')
    ls = m.LineSegment(p1, p2)

    # Initally, there are only a start and end point
    assert len(ls.all_points) == 2

    # Length of segment
    assert ls.len == pytest.approx(3.0, rel=1e-3)

    # Direction of segment
    assert ls.dir.tolist() == [3, 0, 0]

    # UIDs
    assert ls.from_uid == 'a'
    assert ls.to_uid == 'b'

    all_points = ls.split_into(3)
    assert len(all_points) == 4
    assert all_points[0].coord.tolist() == [0, 2, 5]
    assert all_points[1].coord.tolist() == [1, 2, 5]
    assert all_points[2].coord.tolist() == [2, 2, 5]
    assert all_points[3].coord.tolist() == [3, 2, 5]
