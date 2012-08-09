from patchwork import info
import unittest
from unittest import TestCase

import mock
from patchwork.info import lsb_release_info


ubuntu1104_lsb_info = lsb_release_info('No LSB modules are available.',
                    'Ubuntu',
                    'Ubuntu 11.04',
                    '11.04',
                    'natty')
amazon2012_03_lsb_info = lsb_release_info(':core-4.0-amd64:core-4.0-noarch:printing-4.0-amd64:printing-4.0-noarch',
                    'AmazonAMI',
                    'Amazon Linux AMI release 2012.03',
                    '2012.03',
                    'n/a')

class DistroNameDetection(TestCase):
    @mock.patch('patchwork.info.lsb_release')
    @mock.patch('patchwork.info.run')
    def test_ubuntu_detection_via_lsb_release(self, run, lsb_release):
        lsb_release.return_value = ubuntu1104_lsb_info
        self.assertEqual(info.distro_name(), 'ubuntu')
        lsb_release.assert_called()
        self.assertFalse(run.called)

    @mock.patch('patchwork.info.lsb_release')
    @mock.patch('patchwork.info.run')
    def test_amazon_detection_via_lsb_release(self, run, lsb_release):
        lsb_release.return_value = amazon2012_03_lsb_info
        self.assertEqual(info.distro_name(), 'amazon')
        lsb_release.assert_called()
        self.assertFalse(run.called)

class DistroFamilyDetection(TestCase):
    @mock.patch('patchwork.info.distro_name')
    @mock.patch('patchwork.info.run')
    def test_debian_family(self, run, distro_name_fxn):
        for d in ('ubuntu', 'debian'):
            distro_name_fxn.return_value = d
            self.assertEqual('debian', info.distro_family())
            self.assertFalse(run.called)

    @mock.patch('patchwork.info.distro_name')
    @mock.patch('patchwork.info.run')
    def test_redhat_family(self, run, distro_name_fxn):
        for d in ('redhat', 'centos', 'fedora', 'amazon'):
            distro_name_fxn.return_value = d
            self.assertEqual('redhat', info.distro_family())
            self.assertFalse(run.called)

    @mock.patch('patchwork.info.exists')
    @mock.patch('patchwork.info.distro_name')
    @mock.patch('patchwork.info.run')
    def test_family_inference(self, run, distro_name_fxn, file_exists):
        """If debian_version exists, then it should be picked up as debian-family,
        even if exact type couldn't be worked out."""
        distro_name_fxn.return_value = 'other'
        file_exists.side_effect = lambda s: s == '/etc/debian_version'
        self.assertEqual('debian', info.distro_family())

