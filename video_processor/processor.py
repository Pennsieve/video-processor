#!/usr/bin/env python

import boto3
import ffmpy
import os
import shutil
import sys
import time

from base_processor import BaseProcessor
from botocore.client import Config

class VideoProcessor(BaseProcessor):
    required_inputs = ["file","convert"]

    def __init__(self, *args, **kwargs):
        super(VideoProcessor, self).__init__(*args, **kwargs)

        self.session     = boto3.session.Session()
        self.s3_client   = self.session.client('s3', config=Config(signature_version='s3v4'), endpoint_url=self.settings.s3_endpoint)

        self.file        = self.inputs.get('file')
        self.convert     = self.inputs.get('convert') == 'true'

        if self.convert:
            if os.path.splitext(self.file)[1] == '.mp4':
                self.output_file = os.path.splitext(self.file)[0]+'_out.mp4'
            else:
                self.output_file = os.path.splitext(self.file)[0]+'.mp4'
        else:
            self.output_file = self.file

        self.thumbnail_output = os.path.splitext(self.file)[0]+'.png'

        self.upload_key  = os.path.join(self.settings.storage_directory, self.output_file)
        self.thumbnail_upload_key  = os.path.join(self.settings.storage_directory, self.thumbnail_output)

    def execute(self):
        if self.convert:
            self.convert_video()
        self.get_thumbnail()

    def convert_video(self):
        '''Convert an .avi video to an .mp4 video'''

        self.LOGGER.info('Beginning video conversion.')

        # Logstash's multiline codec prevented the previous line from displaying in logstash. This line
        # allows logstash to add the previous event.

        _start = time.time()

        ff = ffmpy.FFmpeg(
            inputs={self.file: None},
            outputs={self.output_file: '-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -vcodec h264'}
        )

        ff.run()

        _dt = int((time.time() - _start) * 1000)
        self.LOGGER.info('Conversion complete. Conversion time in milliseconds: {}'.format(_dt))

    def get_thumbnail(self):
        self.LOGGER.info('Getting getting thumbnail')
        _start = time.time()

        ff = ffmpy.FFmpeg(
            inputs={self.file: None},
            outputs={self.thumbnail_output: '-vf "thumbnail,scale=640:360" -frames:v 1'}
        )

        ff.run()

        _dt = int((time.time() - _start) * 1000)
        self.LOGGER.info('Thumbnail complete. Elapsed time in milliseconds: {}'.format(_dt))
 
    def get_file_size(self,key):
        self.LOGGER.info('Getting file size')

        response = self.s3_client.head_object(
            Bucket=self.settings.storage_bucket, Key=key
        )

        file_size = response['ContentLength']

        self.LOGGER.info('File size in bytes: {}'.format(file_size))

        return file_size

    def cleanup(self):
        '''Remove local directory'''

        self.LOGGER.info('Cleaning up local directory')

        if os.path.exists(self.thumbnail_output):
            os.remove(self.thumbnail_output)

        if self.convert:
            if os.path.exists(self.output_file):
                os.remove(self.output_file)

    def task(self):

        self.execute()

        if self.convert:
            self._upload(self.output_file, self.upload_key)

        file_size = self.get_file_size(self.upload_key)
        asset = { 'bucket': self.settings.storage_bucket,
                  'key': self.upload_key,
                  'type': 'view',
                  'size': file_size
                }
        self.publish_outputs("asset", asset)

        self._upload(self.thumbnail_output, self.thumbnail_upload_key)
        thumbnail_size = self.get_file_size(self.thumbnail_upload_key)
        thumbnail_asset = { 'bucket': self.settings.storage_bucket,
                  'key': self.thumbnail_upload_key,
                  'type': 'view',
                  'size': thumbnail_size
                }

        self.publish_outputs("thumbnail_asset", thumbnail_asset)
        self.cleanup()
