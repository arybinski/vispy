# -*- coding: utf-8 -*-

import json
import tempfile

from vispy import config
from vispy.app import Canvas
from vispy.gloo import glir
from vispy.testing import requires_application, run_tests_if_main


def test_queue():
    q = glir.GlirQueue()
    parser = glir.GlirParser()
    
    # Test adding commands and clear
    N = 5
    for i in range(N):
        q.command('FOO', 'BAR', i)
    cmds = q.clear()
    for i in range(N):
        assert cmds[i] == ('FOO', 'BAR', i)
    
    # Test filter 1
    cmds1 = [('DATA', 1), ('SIZE', 1), ('FOO', 1), ('SIZE', 1), ('FOO', 1), 
             ('DATA', 1), ('DATA', 1)]
    cmds2 = [c[0] for c in q._filter(cmds1, parser)]
    assert cmds2 == ['FOO', 'SIZE', 'FOO', 'DATA', 'DATA']
    
    # Test filter 2
    cmds1 = [('DATA', 1), ('SIZE', 1), ('FOO', 1), ('SIZE', 2), ('SIZE', 2), 
             ('DATA', 2), ('SIZE', 1), ('FOO', 1), ('DATA', 1), ('DATA', 1)]
    cmds2 = q._filter(cmds1, parser)
    assert cmds2 == [('FOO', 1), ('SIZE', 2), ('DATA', 2), ('SIZE', 1), 
                     ('FOO', 1), ('DATA', 1), ('DATA', 1)]

    # Define shader
    shader1 = """
        precision highp float;uniform mediump vec4 u_foo;uniform vec4 u_bar;
        """.strip().replace(';', ';\n')
    # Convert for desktop
    shader2 = q._convert_shaders('desktop', ['', shader1])[1]
    assert 'highp' not in shader2
    assert 'mediump' not in shader2
    assert 'precision' not in shader2
    
    # Convert for es2
    shader3 = q._convert_shaders('es2', ['', shader2])[1]
    assert 'precision highp float;' in shader3


@requires_application()
def test_log_parser():
    glir_file = tempfile.TemporaryFile(mode='r+')

    config.update(glir_file=glir_file)
    with Canvas() as c:
        c.context.set_clear_color('white')
        c.context.clear()

    glir_file.seek(0)
    lines = glir_file.read().splitlines()
    i = 0

    assert lines[i] == json.dumps(['CURRENT', 0])
    i += 1
    # The 'CURRENT' command may have been called multiple times
    while lines[i] == lines[i - 1]:
        i += 1
    assert lines[i] == json.dumps(['FUNC', 'glClearColor', 1.0, 1.0, 1.0, 1.0])
    i += 1
    assert lines[i] == json.dumps(['FUNC', 'glClear', 17664])
    i += 1
    assert lines[i] == json.dumps(['FUNC', 'glFinish'])
    i += 1

    config.update(glir_file='')


# The rest is basically tested via our examples
    
run_tests_if_main()
