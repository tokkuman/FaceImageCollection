# -*- coding: utf-8 -*-

import sys
import os
import commands as cmd
import cv2
import time
import copy
from argparse import ArgumentParser

def getHtml(query):
    return cmd.getstatusoutput("wget -O - https://www.bing.com/images/search?q=" + query)[1]

def extractImageURL(html, suffix):
    url = []
    snum, lnum = 0, 0
    text = html.split('\n')
    for sen in text:
        if sen.find('<div class="item">') >= 0:
            element = sen.split('<div class="item">')
            for num in range(len(element)):
                for suf in suffix:
                    snum = element[num].find("href") + 6
                    lnum = element[num].find(suf) + len(suf)
                    if lnum > 0:
                        url.append(element[num][snum:lnum])
                        break
    return url

def saveImg(opbase, url):
    dir = opbase + '/Original/'
    if not (os.path.exists(dir)):
        os.mkdir(dir)
    for u in url:
        try:
            os.system('wget -P ' + dir + ' '  + u)
        except:
            continue

def cropFace(opbase, path, imsize, method):
    dir = opbase + '/Crop/'
    if not (os.path.exists(dir)):
        os.mkdir(dir)
    for p in path:
        img = cv2.imread(opbase + '/Original/' + p)
        gImg = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        if method == 1:
            face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
        elif method == 2:
            face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_alt.xml')
        elif method == 3:
            face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_alt2.xml')
        else:
            face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_alt_tree.xml')
        faces = face_cascade.detectMultiScale(gImg, 1.3, 5)
        for num in range(len(faces)):
            cropImg = copy.deepcopy(img[faces[num][1]:faces[num][1]+faces[num][3], faces[num][0]:faces[num][0]+faces[num][2]])
            resizeImg = cv2.resize(cropImg, (imsize, imsize))
            filename = dir + p[:-4] + '_' + str(num + 1) + '.tif'
            cv2.imwrite(filename, resizeImg)
    
        
if __name__ == "__main__":
    
    ap = ArgumentParser(description='ImageCollenction.py')
    ap.add_argument('--query', '-q', nargs='*', default='hoge', help='Specify Query of Image Collection ')
    ap.add_argument('--suffix', '-s', nargs='*', default='jpg', help='Specify Image Suffix')
    ap.add_argument('--imsize', '-i', type=int, default=100, help='Specify Image Size of Crop Face Image')
    ap.add_argument('--method', '-m', type=int, default=1, help='Specify Method Flag (1 : Haarcascades Frontalface Default, 2 : Haarcascades Frontalface Alt1, 3 : Haarcascades Frontalface Alt2, Without : Haarcascades Frontalface Alt Tree)')
    args = ap.parse_args()

    t = time.ctime().split(' ')
    if t.count('') == 1:
        t.pop(t.index(''))
    # Path Separator
    psep = '/'
    for q in args.query:
        opbase = q
        # Delite File Sepaeator   
        if (opbase[len(opbase) - 1] == psep):
            opbase = opbase[:len(opbase) - 1]
        # Add Current Directory (Exept for Absolute Path)
        if not (opbase[0] == psep):
            if (opbase.find('./') == -1):
                opbase = './' + opbase
        # Create Opbase
        opbase = opbase + '_' + t[1] + t[2] + t[0] + '_' + t[4] + '_' + t[3].split(':')[0] + t[3].split(':')[1] + t[3].split(':')[2]
        if not (os.path.exists(opbase)):
            os.mkdir(opbase)
            print 'Output Directory not exist! Create...'
        print 'Output Directory:', opbase

        html = getHtml(q)
        url = extractImageURL(html, args.suffix)
        saveImg(opbase, url)
        cropFace(opbase, os.listdir(opbase + '/Original'), args.imsize, args.method)
