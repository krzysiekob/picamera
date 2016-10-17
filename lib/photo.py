# -*- coding: utf-8 -*-

import gevent
# test
#import picamera
from lib.settings import Settings
from datetime import datetime
from gevent import subprocess
from PIL import Image
import os
import logging
# test
#from picamera import Color
from email.utils import formatdate
from lib.flickr import Flickr

class Photo:

    def __init__(self, path=None):
        settings = Settings()
        s = settings.get("email")

        if path is None:
            self.path = s['path_files']
        else:
            self.path = path

        try:
            self.start_photo = int(s['start_photo'].replace(':', ''))
            self.stop_photo = int(s['stop_photo'].replace(':', ''))
            self.step_photo = int(s['step_photo'])
            self.photo_sharpness = int(s['photo_sharpness'])
            self.photo_contrast = int(s['photo_contrast'])
            self.photo_brightness = int(s['photo_brightness'])
            self.photo_saturation = int(s['photo_saturation'])
            self.photo_iso = int(s['photo_iso'])
            self.photo_exposure_compensation = int(s['photo_exposure_compensation'])
            self.photo_awb_gains = (float(s['photo_awb_gains_red']), float(s['photo_awb_gains_blue']))
            self.photo_rotation = int(s['photo_rotation'])

            self.photo_color_effects = None
            if (s['photo_color_effects_u'] != '' and s['photo_color_effects_v'] != ''):
                self.photo_color_effects = (int(s['photo_color_effects_u']), int(s['photo_color_effects_v']))

            self.photo_zoom = (float(s['photo_zoom_x']), float(s['photo_zoom_y']), float(s['photo_zoom_w']), float(s['photo_zoom_h']))
            self.photo_annotate_size = int(s['photo_annotate_size'])
        except ValueError:
            pass

        self.photo_exposure_mode = s['photo_exposure_mode']
        self.photo_meter_mode = s['photo_meter_mode']
        self.photo_awb_mode = s['photo_awb_mode']
        self.photo_image_effect = s['photo_image_effect']
        #self.photo_annotate_background = Color(s['photo_annotate_background'])
        self.photo_annotate_text = s['photo_annotate_text']
        if (s['photo_annotate_add_date'] == '1'):
            self.photo_annotate_text = '%s %s' % (self.photo_annotate_text,formatdate(localtime=True))

        self.photo_resolution = s['photo_resolution']
        self.log = logging.getLogger("app")

    def create_image(self, path_photo):
        with picamera.PiCamera() as camera:
            self.log.debug("create image: %s" % path_photo)

            # http://picamera.readthedocs.io/en/release-1.12/api_camera.html
            
            camera.sharpness = self.photo_sharpness
            camera.contrast = self.photo_contrast
            camera.brightness = self.photo_brightness
            camera.saturation = self.photo_saturation
            camera.iso = self.photo_iso
            camera.exposure_compensation = self.photo_exposure_compensation
            camera.exposure_mode = self.photo_exposure_mode
            camera.meter_mode = self.photo_meter_mode
            camera.awb_mode = self.photo_awb_mode
            camera.awb_gains = self.photo_awb_gains
            camera.rotation = self.photo_rotation
            camera.image_effect = self.photo_image_effect
            camera.color_effects = self.photo_color_effects
            camera.zoom = self.photo_zoom
            camera.annotate_background = self.photo_annotate_background
            camera.annotate_text = self.photo_annotate_text
            camera.annotate_text_size = self.photo_annotate_size
            camera.resolution = self.photo_resolution
            
            camera.start_preview()
            # Camera warm-up time
            gevent.sleep(2)
            camera.capture(path_photo)
            return True

        return False

    def create_thumb(self, path_photo, path_to_thumb, width=350, height=350):
        size = (width, height)
        try:
            with Image.open(path_photo) as im:
                im.thumbnail(size)
                im.save(path_to_thumb, "JPEG")
                self.log.debug(
                    "create thumb: %s" % path_to_thumb)
                return path_to_thumb
        except IOError:
            self.log.error("cannot create thumbnail for", path_photo)

        return None

    def _run(self,):
        path_photo = "%s/%s.jpg" % (self.path,
                                    datetime.now().strftime('%H_%M'))

        if self.create_image(path_photo):
            path_to_thumb = self.path + '/thumb/' + \
                os.path.basename(path_photo)
            self.create_thumb(path_photo, path_to_thumb)

            gevent.spawn(self.flickr, path_photo)

    def flickr(self, path_photo):
        flickr = Flickr()
        if flickr.isPower():
            flickr.uploadFile(path_photo)
                
    def run(self,):
        sleep = 60
        while True:
            try:
                if int(datetime.now().strftime('%M')) % self.step_photo == 0 and int(datetime.now().strftime('%H%M')) >= self.start_photo and int(datetime.now().strftime('%H%M')) <= self.stop_photo:
                    try:
                        subprocess.check_output(["pidof", 'raspivid'])
                        sleep = 1
                    except:
                        self._run()
                        sleep = 60

                self.__init__()
                gevent.sleep(sleep)
            except Exception as e:
                self.log.error(str(e))
