import urllib
import os

from lib.flickr import Flickr
#print f.getFlickrSets()

class Download:
    def __init__(self,):
        self.page = 1
        self.photoset_id = '72157672366020112'
        self.file_name_counter = 0
        self.dir = 'static/time_laps'
        self.flick = Flickr()
        self.ffpmeg = 'ffmpeg -r 15 -start_number 1 -i %010d.jpg -s 1920x1080 -vcodec libx264 test.mp4'

    def run(self,):
        photos = self.flick.getPhotos(self.photoset_id, self.page)
        for photo in photos['photoset']['photo']:
            url = photo['url_o']
            image = urllib.URLopener()
            self.file_name_counter += 1
            filename = self.dir + "/" + os.path.basename("%010d" % (self.file_name_counter, ) + '.jpg')
            if os.path.isfile(filename) is False:
                image.retrieve(url, filename)
                print 'downloading:['+str(self.page)+']', url

        if photos['photoset']['pages'] > self.page:
            print "next page"
            self.page += 1
            self.run()


d = Download()
d.run()

#ffmpeg -r 15 -start_number 1 -i %010d.jpg -s 1920x1080 -vcodec libx264 test.mp4
