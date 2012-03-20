from datetime import date, timedelta
import urllib2
import re

from bs4 import BeautifulSoup

base_url = 'http://apod.nasa.gov/apod/'

# returns the image data of for a given date, and the filename
def date_image_data(d):
    img, filename = date_image(d)
    size = int(img.info()['content-length'])
    return img.read(size + 1), filename

# returns a "file-like object" of the image for a given date,
# and the image filename
def date_image(d):
    i_url = image_url(d)
    print "OK, URL found. Downloading image.."
    img = urllib2.urlopen(i_url)
    return img, i_url.split('/')[-1]

# get the url for the large image for a given date.
# gets the page and tries to parse it.
# if anything goes bad, raise hell
def image_url(d):
    p_url = page_url(d)
    p = urllib2.urlopen(p_url)
    soup = BeautifulSoup(p.read())
    img_a = soup.find(lambda t: image_href_filter(t, d))
    if img_a == None:
        # if this happens, url structure/etc has changed and
        # script won't work at all anymore. should perhaps raise a more
        # noticeable error, but for now.. structure has been constant for
        # 15 years anyway.
        raise Exception
    else:
        return base_url + img_a.get('href')

def page_url(d):
    page = 'ap' + d.strftime('%y%m%d') + '.html'
    return base_url + page

# images are in e.g. image/1203/ for march 2012
def image_href_filter(tag, d):
    pattern = 'image/' + d.strftime('%y%m') + '/'
    return tag.has_attr('href') and re.search(pattern, tag['href']) != None


# if run on its own, download today's image into current folder.
# try yesterday if today doesn't work (timezones etc)
# figuring out at which time images are uploaded would be better..
if __name__ == "__main__":
    today = date.today()
    print "Attempting to download today's image.."
    try:
        img_data, filename = date_image_data(today)
    except:
        print "Oops! Did not work very well. Trying yesterday.."
        try:
            img_data, filename = date_image_data(today - timedelta(1))
        except:
            print "Something goofed up. Exiting."
            exit()

    local_file = open(filename, "wb")
    local_file.write(img_data)
    local_file.close()
    print "Success! Today's image is " + filename
