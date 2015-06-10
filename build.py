from pybuilder.core import use_plugin, init, Author

use_plugin('python.core')
use_plugin('python.install_dependencies')
use_plugin('python.distutils')
use_plugin('python.flake8')

use_plugin('python.unittest')

use_plugin('copy_resources')

default_task = ['analyze', 'publish']

name = 'yadtbroadcast-client-wamp2'
version = '0.0.2'
summary = 'YADT - an Augmented Deployment Tool - The Broadcast Client Part'
description = """Yet Another Deployment Tool - The Broadcast Client Part
- sends state information to a Yadt Broadcast Server instance
- sends information on start/stop/status/update
- using the Wamp v2 protocol
"""
authors = [Author('Arne Hilmann', 'arne.hilmann@gmail.com'),
           Author('Maximilien Riehl', 'max@riehl.io'),
           Author('Marcel Wolf', 'marcel.wolf@immobilienscout24.de')]
url = 'http://github.com/yadt/yadtbroadcast-client-wamp2'
license = 'GNU GPL v3'


@init
def set_properties(project):
    project.build_depends_on('mock')
    project.build_depends_on('requests')

    project.depends_on('Twisted')
    project.depends_on('autobahn')

    project.set_property("verbose", True)

    project.set_property("flake8_include_test_sources", True)
    project.set_property('coverage_break_build', False)

    project.set_property("install_dependencies_upgrade", True)

    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').append('setup.cfg')
    project.set_property('dir_dist_scripts', 'scripts')

    project.set_property('distutils_classifiers', [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: System :: Networking',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration'
    ])


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.version = '%s-%s' % (
        project.version, os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['install_build_dependencies', 'publish']
    project.get_property('distutils_commands').append('bdist_rpm')
    project.set_property(
        'install_dependencies_index_url', os.environ.get('PYPIPROXY_URL'))
    project.set_property('install_dependencies_use_mirrors', False)
    project.set_property('teamcity_output', True)
