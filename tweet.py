
import urllib
import pygame, sys, json, threading, logging
import pygame.font as font#You might have errors with this. If you do, you can change it to pygame.font, and change the calles to Font.render() a bit
from StringIO import StringIO

nameFont = font.SysFont('helvetica', 20)#Helvetica is the closest to twitter's special font
textFont = font.SysFont('helvetica', config.getint('font', 'size'))
class Tweet():
    def __init__(self, json):
        self.json = json
        self.text, self.imgs = self._expandLinks(json)
        self.surface = self._getTweetSurface()

    #Helper method that takes a tweet, and returns the tweet text with all urls expanded (and image urls removed), along with a list of all the images
    def _expandLinks(self, json):
            text = json['text']
            imgList = []
            entities = []#List of all urls and media urls in tweet
            if 'urls' in json['entities']:#adds urls to entities
                    entities.extend([(entity, 'url') for entity in json['entities']['urls']])
            if 'media' in json['entities']:#adds mediau urls to entities
                    for entity in json['entities']['media']:
                            entities.append((entity, 'media'))
                            if entity['type'] == 'photo':
                                    imgList.append(entity)
            entities = reversed(sorted(entities, key = lambda (entity, eType): entity['indices']))
            for (entity, eType) in entities:#Removes media urls, and lengthens normal urls
                    if eType == 'url':
                            text = text[0:entity['indices'][0]] + entity['expanded_url'] + text[entity['indices'][1]:]
                    if eType == 'media':
                            text = text[0:entity['indices'][0]] + text[entity['indices'][1]:]
            return unicode(xml.unescape(text)), imgList

    ### New tweet surface generator ###
    def _getTweetSurface(self):
            surfList = []
            logging.debug('downloading profile pic')
            try:
                    userImage = pygame.image.load(StringIO(urllib.urlopen(self.json['user']['profile_image_url']).read()))
                    imageSurf = pygame.transform.scale(userImage,(70,70))
                    surfList.append(imageSurf)
            except:
                    logging.debug('failed to download profile pic!')
            logging.debug('done')
            userName = self.json['user']['name']
            userScreenName = self.json['user']['screen_name']
            lines = self.text.split('\n')
            nameSurf = textFont.render('@' + userScreenName, 1, black)
            surfList.append(nameSurf)
            contentList = []
            for line in lines:
                    words = [Word(word) for word in line.split()]
                    wordSurfs = []
                    for word in words:
                            try:
                                    wordSurf = textFont.render(word.text + '  ', 1, word.color)
                                    wordSurfs.append(wordSurf)
                            except:
                                    logging.debug(word.text)
                    if wordSurfs == []:
                            continue
                    width = sum([wordSurf.get_width() for wordSurf in wordSurfs])
                    height = max([wordSurf.get_height() for wordSurf in wordSurfs])
                    lineSurf = pygame.Surface((width, height))
                    lineSurf.fill(twitter_bg_blue)
                    blitList(lineSurf, wordSurfs)
                    contentList.append(lineSurf)
            contentList.extend(self.imgs)
            width = max([x.get_width() for x in contentList])
            height = sum([x.get_height() for x in contentList])
            contentSurf = pygame.Surface((width, height))
            contentSurf.fill(twitter_bg_blue)
            blitList(contentSurf, contentList)
            tailLength = width / 5
            width += BORDER_WIDTH + tailLength
            height += 2* BORDER_HEIGHT
            bubbleSurf = pygame.Surface((width, height))
            bubbleSurf.fill(twitter_bg_blue)
            bubbleSurf.blit(pygame.transform.scale(speechBubble,(width, height)),[0, 0])
            bubbleSurf.blit(contentSurf, [tailLength, BORDER_HEIGHT])
            surfList.append(bubbleSurf)
            width = max([x.get_width() for x in surfList])
            height = sum([x.get_height() for x in surfList])
            tweetSurf = pygame.Surface((width, height))
            tweetSurf.fill(twitter_bg_blue)
            blitList(tweetSurf, surfList)
            return tweetSurf
### For use by tweet surface method ###
class Word():
	def __init__(self,text):
		self.text = text
		ttext = text[0:1]
		if ttext == '#' or ttext == '@':
			self.color = blue
		elif len(text) > 4 and text[0:4] == 'http':
			self.color = blue
		else:
			self.color = black
