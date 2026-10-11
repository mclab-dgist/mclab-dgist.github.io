#!/usr/bin/env python3
"""Crop the 11 research-topic images: remove outer margins and detached title strips.

Keeps diagrams, axes and legends when connected to the main artwork. Originals
remain recoverable in Git history. This deliberately excludes the featured figure.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter
import numpy as np

ROOT = Path("mclab/content/research")
for path in sorted(ROOT.glob("*/figure.webp")):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if w < 200 or h < 160:
        continue
    # Downsample for robust layout detection, keeping the original for output.
    sample = im.copy()
    sample.thumbnail((1000, 1000))
    a = np.asarray(sample, dtype=np.int16)
    sh, sw = a.shape[:2]
    # Estimate neutral canvas from edge/corner pixels.
    edge = np.concatenate((a[:max(2,sh//70)].reshape(-1,3),
                           a[-max(2,sh//70):].reshape(-1,3),
                           a[:, :max(2,sw//70)].reshape(-1,3),
                           a[:, -max(2,sw//70):].reshape(-1,3)))
    bg = np.median(edge, axis=0)
    deviation = np.max(np.abs(a-bg), axis=2)
    ink = deviation > 25
    # Ignore isolated speckles, but retain diagram lines and small labels.
    row = ink.mean(axis=1)
    col = ink.mean(axis=0)
    active_y = np.flatnonzero(row > .004)
    active_x = np.flatnonzero(col > .004)
    if not len(active_y) or not len(active_x):
        print("SKIP blank",path)
        continue
    top, bottom = int(active_y[0]), int(active_y[-1]+1)
    # Locate a blank band separating a short heading from the actual diagram.
    # Never remove more than 30% from the top or trim title without a gap.
    runs = []
    isblank = row < .003
    k = top
    while k < min(bottom, int(sh*.40)):
        if isblank[k]:
            z=k
            while z < sh and isblank[z]: z+=1
            if z-k >= max(6,int(sh*.012)): runs.append((k,z))
            k=z
        else:k+=1
    for y,z in runs:
        if y-top < sh*.29 and z < bottom-sh*.38 and z > top+sh*.025:
            # Content after the gap must be substantial compared with heading.
            if ink[z:bottom].sum() > ink[top:y].sum()*2.5:
                top=z
                print("TITLE STRIP",path.name,"removed",z,"of",sh,"sample rows")
                break
    # Recalculate horizontal extent after title removal.
    sub=ink[top:bottom]
    xc=np.flatnonzero(sub.mean(axis=0)>.003)
    if not len(xc):continue
    left,right=int(xc[0]),int(xc[-1]+1)
    # Minimal safety padding to prevent cropping border strokes.
    pad=max(3,int(min(sw,sh)*.009))
    left=max(0,left-pad);right=min(sw,right+pad)
    top=max(0,top-pad);bottom=min(sh,bottom+pad)
    box=(int(left*w/sw),int(top*h/sh),int(right*w/sw),int(bottom*h/sh))
    if box[2]-box[0]<w*.42 or box[3]-box[1]<h*.35:
        print("SKIP risky",path,box);continue
    if box[0]<3 and box[1]<3 and box[2]>w-3 and box[3]>h-3:
        print("SKIP already tight",path);continue
    out=im.crop(box)
    out.save(path,"WEBP",quality=94,method=6)
    print("CROPPED",path,im.size,"->",out.size,"box",box)
