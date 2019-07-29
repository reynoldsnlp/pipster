from pip_inside import _build_install_cmd

"""
TODO(RJR) implement the following tests

install("pip install --target /tmp//target_dir_without_spaces ''")
install("pip install --target '/tmp//target dir with spaces' ''")
install("<full-path-to-v1.0-sample-wheel>", target="/tmp//") followed by install("<full-path-to-v2.0-sample-wheel>", target="/tmp//", upgrade=True)  # noqa: E501
"""


def test_build_install_cmd():
    assert _build_install_cmd('pip install it') == ['pip', 'install', 'it']
    assert _build_install_cmd('it') == ['pip', 'install', 'it']
