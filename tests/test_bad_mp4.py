import boto3
import os
import unittest
import pytest

from moto import mock_s3, mock_ssm
from video_processor.processor import VideoProcessor
from test_base import init_ssm

class VideoTestCase(unittest.TestCase):
    @mock_s3
    @mock_ssm
    def setUp(self):
        mock_ssm().start()
        mock_s3().start()
        init_ssm()

        self.file = "./tests/resources/jobId/bad.mp4"
        self.vp = VideoProcessor(inputs={'file': self.file, 'convert':'true'})

    @mock_s3
    @mock_ssm
    def tearDown(self):
        if os.path.exists(self.vp.output_file):
            os.remove(self.vp.output_file)
        if os.path.exists(self.vp.thumbnail_output):
            os.remove(self.vp.thumbnail_output)
        mock_s3().stop()
        mock_ssm().stop()


class VideoProcessorTests(VideoTestCase):
    @mock_s3
    @mock_ssm
    def runTest(self):
        print('\n\n*********** Testing \'Convert\' ***********')
        self.vp.execute()
        assert (os.path.exists(self.vp.output_file))
        assert (os.path.exists(self.vp.thumbnail_output))
        print('Video converted successfully.')
