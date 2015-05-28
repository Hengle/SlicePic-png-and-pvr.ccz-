#!-*- coding:utf-8 -*-

import os,sys,shutil
from xml.etree import ElementTree
from PIL import Image
from biplist import *

global output 
output= "output_UI"
global res_input
res_input = "res"

def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index+1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index+1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index+1])
    return d

def gen_png_from_plist(plist_filename, png_filename):
    # global output

    if not ( (os.path.exists(plist_filename) and os.path.exists(png_filename)) ):
        print "%s is not a big map" % png_filename
        return

    file_path = plist_filename.replace('.plist', '')
    big_image = Image.open(png_filename)

    out_path = output+"/"+os.path.basename(file_path)

    plist_dict = readPlist(plist_filename)
    print type(plist_dict)

    to_list = lambda x: x.replace('{','').replace('}','').split(',')
    for k,v in plist_dict['frames'].items():
        # print v
        rectlist = to_list(v['frame'])
        width = int( rectlist[3] if v['rotated'] else rectlist[2] )
        height = int( rectlist[2] if v['rotated'] else rectlist[3] )
        box=( 
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0]) + width,
            int(rectlist[1]) + height,
            )
        sizelist = [ int(x) for x in to_list(v['sourceSize'])]
        # print box,big_image
        rect_on_big = big_image.crop(box)

        if v['rotated']:
            rect_on_big = rect_on_big.rotate(90)

        result_image = Image.new('RGBA', sizelist, (0,0,0,0))
        if v['rotated']:
            result_box=(
                ( sizelist[0] - height )/2,
                ( sizelist[1] - width )/2,
                ( sizelist[0] + height )/2,
                ( sizelist[1] + width )/2
                )
        else:
            result_box=(
                ( sizelist[0] - width )/2,
                ( sizelist[1] - height )/2,
                ( sizelist[0] + width )/2,
                ( sizelist[1] + height )/2
                )
        result_image.paste(rect_on_big, result_box, mask=0)

        
        if not os.path.isdir(out_path):
            os.mkdir(out_path)
        outfile = (out_path+'/' + k).replace('gift_', '')
        print outfile, "generated"
        result_image.save(outfile)

def convert(path):
    path = os.path.normpath(path)
    print path
    if os.path.isdir(path):
        for _file in os.listdir(path):
            convert(os.path.join(path,_file))
    elif os.path.isfile(path):
         # ext = os.path.splitext(path)
         ext = path.split(".",1)
         if not ext or len(ext)<2:
             return
         if ext[1] in ["png"]:
            # 装换png大图到小图
            gen_png_from_plist(ext[0]+'.plist',path)
            pass
         elif ext[1] in ['pvr.ccz']:
            #  用texture转换
            os.system("TexturePacker --sheet %s.png %s --opt RGBA8888 --algorithm Basic --dither-fs" % (ext[0],path) )
            gen_png_from_plist(ext[0]+'.plist',ext[0]+'.png')
            os.remove(ext[0]+'.png')
            pass
    pass

if __name__ == '__main__':
    if not os.path.exists(output):
        os.mkdir(output)
        pass
    convert(res_input)
    os.remove("out.plist")