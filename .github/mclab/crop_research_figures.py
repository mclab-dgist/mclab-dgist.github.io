#!/usr/bin/env python3
"""Conservatively crop margins and isolated title strips from research figures.

Originals remain recoverable through Git history. Only research/figure.webp files
are edited; the large featured integrated-control framework is untouched.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
import io

ROOT = Path("mclab/content/research")
for path in sorted(ROOT.glob("*/figure.webp")):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if w < 200 or h < 160:
        continue
    # Estimate paper/canvas background using corners; do not assume pure white.
    corners = [im.getpixel(p) for p in ((0, 0), (w-1, 0), (0, h-1), (w-1, h-1))]
    bg = tuple(sorted(c[k] for c in corners)[2] for k in range(3))
    sample = im.resize((min(720,w), min(720,h)))
    sw, sh = sample.size
    pix = sample.load()
    occupancy = []
    for y in range(sh):
        count = 0
        for x in range(sw):
            c = pix[x,y]
            if max(abs(c[k]-bg[k]) for k in range(3)) > 30:
                count += 1
        occupancy.append(count/sw)
    active = [i for i,v in enumerate(occupancy) if v > .012]
    if not active:
        continue
    top, bottom = active[0], active[-1]
    # Remove an isolated header/title only when a clear blank horizontal gap exists
    # near the top and the main figure below is substantially larger.
    gaps=[]
    for y in range(top+1, min(int(sh*.34),bottom-2)):
        if occupancy[y] < .006:
            z=y
            while z < sh and occupancy[z] < .006:
                z+=1
            if z-y >= max(7,int(sh*.025)):
                gaps.append((y,z))
    for y,z in gaps:
        if y < sh*.27 and bottom-z > sh*.48 and z-top < sh*.34:
            top=z
            break
    # Trim left/right using the remaining content area.
    ys=int(top*h/sh); ye=min(h,int((bottom+1)*h/sh))
    bbox=ImageChops.difference(im.crop((0,ys,w,ye)), Image.new("RGB",(w,ye-ys),bg)).convert("L").point(lambda v:255 if v>32 else 0).getbbox()
    if not bbox:
        continue
    x0,x1=bbox[0],bbox[2]
    pad=max(8,int(min(w,h)*.018))
    box=(max(0,x0-pad),max(0,ys-pad),min(w,x1+pad),min(h,ye+pad))
    nw,nh=box[2]-box[0],box[3]-box[1]
    # Avoid aggressive cropping or nearly invisible changes.
    if nw < w*.55 or nh < h*.48 or (nw>w*.975 and nh>h*.975):
        print("SKIP",path,"unsafe/minimal",box)
        continue
    out=im.crop(box)
    out.save(path,"WEBP",quality=94,method=6)
    print("CROPPED",path,f"{w}x{h} -> {out.width}x{out.height}",box)
