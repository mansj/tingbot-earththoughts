import tingbot
from tingbot import *
from urlparse import urlparse
import urllib2, json
import os, sys
import hashlib

# Debug sys to stdout
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# Set Debug on/off
debug = 1

gdata = {
    'background_image': None,
    'index': 0
    }
    
# Define text X/Y default values
textx = 22
texty = 30

# Init ticker to count loops for text animation purposes
ticker = 0

# setup code here

earthporn_url = 'https://api.flickr.com/services/feeds/groups_pool.gne?id=1828266@N24&format=json&nojsoncallback=?'
showerthoughts_url = 'https://www.reddit.com/r/showerthoughts/.json'

earthporn_images = []
showerthoughts = []

print 'refreshing...'

def filename_for_url(url):
    m = hashlib.md5()
    m.update(os.path.dirname(urlparse(url).path))
    thishash = m.hexdigest()
    return '/tmp/earththoughts-' + thishash + '_' + os.path.basename(urlparse(url).path)

def get_earthporn():
    global earthporn_images, gdata
    earthporn_images = []
    
    if debug: 
        print "Getting earthporn..."

    response = urllib2.urlopen(earthporn_url)
    data = response.read()
    
    jsondata = data
    jsondata = jsondata.replace("Reddit\\'s", "")
    
    earthporn_data = json.loads(jsondata)
    
    
    for value in earthporn_data['items']:
         earthporn_images.append(value['media']['m'])
         
    # Load all images in the image_urls list to files
    ## DEBUG: Ladda bara tre
    count = 0
    for image_url in earthporn_images:
        count = count + 1
        if count >= 3: 
            continue
        
        filename = filename_for_url(image_url)

        # Get file from URL if it's not already downloaded
        if not os.path.exists(filename):
            gif = urllib2.urlopen(image_url)
            with open(filename,'wb') as output:
                  output.write(gif.read())

            if debug:
                print('urlretrieve: ' + str(image_url))
         
    gdata['background_image'] = earthporn_images[0]

def get_showerthoughts(): 
    global showerthoughts
    showerthoughts = []
    
    if debug: print "Getting showerthoughts..."
    

    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(showerthoughts_url, None, headers)
    data = urllib2.urlopen(req).read()

    jsondata = data

    data = json.loads(jsondata)
    
    c = 0
    
    for value in data['data']['children']:
        c = c + 1
        if c < 4:
            continue
        
        showerthoughts.append(value['data']['title'])
    
    gdata['showerthought'] = showerthoughts[0]

get_earthporn()

get_showerthoughts()

@every(seconds=5)
def next_slide():
    global gdata, ticker
    gdata['index'] += 1
    
    if gdata['index'] >= len(earthporn_images):
        gdata['index'] = 0
        
    gdata['background_image'] = earthporn_images[gdata['index']]
    gdata['showerthought'] = showerthoughts[gdata['index']]
    
    ticker = 0
    

def loop():
    global ticker
    ticker = ticker + 0.2
    
    if gdata['background_image']:
        image_url = gdata['background_image']

        filename = filename_for_url(image_url)
        image = Image.load(filename)
        
        width_sf = 320.0 / image.size[0]
        height_sf = 240.0 / image.size[1]
        sf = max(width_sf, height_sf)
        screen.image(Image.load(filename), scale=sf)
    
    if gdata['showerthought']:
        
        # Split text into words
        thistext = gdata['showerthought']
        thistext = thistext.split()
        
        # Step through words and split by line
        wordcount = 0
        linecount = 0
        y_offset = 0
        lines = []
        outwords = ''
        
        for word in thistext:
            wordcount += 1
            outwords = outwords + ' ' + word
            if wordcount >= 4:
                wordcount = 0
                lines.append(outwords)
                outwords = ''
                linecount += 1
        
        # Add remaining words (if any)
        if len(outwords): 
            lines.append(outwords)
        
        linecount = 0
        for line in lines:
            linecount += 1
            screen.text (
                line,
                xy=(ticker+30,29 + (25 * linecount)),
                align='left',
                color='black',
                font='birds.ttf',
                font_size=24,
            )
    
            screen.text (
                line,
                xy=(ticker+29,28 + (25 * linecount)),
                align='left',
                color='white',
                font='birds.ttf',
                font_size=24,
            )    
        
       # screen.fill(color=(255, 0, 0, 50))
    
        screen.update()

    else:
        screen.fill(color='blue')
        screen.text("Loading...")

    screen.update()

# run the app

tingbot.run(loop)
