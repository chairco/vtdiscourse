# -*- coding: utf-8 -*-
import pytest

from vtdiscourse import vtdiscourse


def test_sumary():
    parm = vtdiscourse.Parser(name='directors-election-gitbook', githubfile='SUMMARY.md')
    summary_data = parm.get_summary
    assert len(summary_data) == 4

