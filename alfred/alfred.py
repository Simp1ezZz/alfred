#!/usr/bin/env python3
#
# Copyright (c) 2020 JinTian.
#
# This file is part of alfred
# (see http://jinfagang.github.io).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
"""
main entrance of Alfred
"""
import os
import sys
import argparse
from colorama import Fore, Back, Style

from .modules.vision.video_extractor import VideoExtractor
from .modules.scrap.image_scraper import ImageScraper
from .modules.vision.to_video import VideoCombiner
from .modules.vision.video_reducer import VideoReducer

from .modules.data.view_voc import vis_voc
from .modules.data.view_coco import vis_coco
from .modules.data.view_txt import vis_det_txt
from .modules.data.gather_voclabels import gather_labels
from .modules.data.voc2coco import convert
from .modules.data.eval_voc import eval_voc

from .modules.cabinet.count_file import count_file
from .modules.cabinet.split_txt import split_txt_file
from .modules.cabinet.license import apply_license
from .modules.cabinet.stack_imgs import stack_imgs

from alfred.utils.log import logger as logging

__VERSION__ = '2.7.1'
__AUTHOR__ = 'Lucas Jin'
__DATE__ = '20202.10.01, since 2019.11.11'
__LOC__ = 'Shenzhen, China'
__git__ = 'http://github.com/jinfagang/alfred'


def arg_parse():
    """
    parse arguments
    :return:
    """
    parser = argparse.ArgumentParser(prog="alfred")
    parser.add_argument('--version', '-v', action="store_true", help='show version info.')

    # vision, text, scrap
    main_sub_parser = parser.add_subparsers()

    # =============== vision part ================
    vision_parser = main_sub_parser.add_parser('vision', help='vision related commands.')
    vision_sub_parser = vision_parser.add_subparsers()

    vision_extract_parser = vision_sub_parser.add_parser('extract', help='extract image from video: alfred vision '
                                                                         'extract -v tt.mp4')
    vision_extract_parser.set_defaults(which='vision-extract')
    vision_extract_parser.add_argument('--video', '-v', help='video to extract')
    vision_extract_parser.add_argument('--jumps', '-j', help='jump frames for wide extract')

    vision_reduce_parser = vision_sub_parser.add_parser('reduce', help='reduce video by drop frames'
                                                                       '\nalfred vision reduce -v a.mp4 -j 10')
    vision_reduce_parser.set_defaults(which='vision-reduce')
    vision_reduce_parser.add_argument('--video', '-v', help='video to extract')
    vision_reduce_parser.add_argument('--jumps', '-j', help='jump frames for wide extract')

    vision_2video_parser = vision_sub_parser.add_parser('2video', help='combine into a video: alfred vision '
                                                                       '2video  -d ./images')
    vision_2video_parser.set_defaults(which='vision-2video')
    vision_2video_parser.add_argument('--dir', '-d', help='dir contains image sequences.')

    vision_clean_parser = vision_sub_parser.add_parser('clean', help='clean images in a dir.')
    vision_clean_parser.set_defaults(which='vision-clean')
    vision_clean_parser.add_argument('--dir', '-d', help='dir contains images.')

    vision_getface_parser = vision_sub_parser.add_parser('getface', help='get all faces inside an image and save it.')
    vision_getface_parser.set_defaults(which='vision-getface')
    vision_getface_parser.add_argument('--dir', '-d', help='dir contains images to extract faces.')

    # =============== text part ================
    text_parser = main_sub_parser.add_parser('text', help='text related commands.')
    text_sub_parser = text_parser.add_subparsers()

    text_clean_parser = text_sub_parser.add_parser('clean', help='clean text.')
    text_clean_parser.set_defaults(which='text-clean')
    text_clean_parser.add_argument('--file', '-f', help='file to clean')

    text_translate_parser = text_sub_parser.add_parser('translate', help='translate')
    text_translate_parser.set_defaults(which='text-translate')
    text_translate_parser.add_argument('--file', '-f', help='translate a words to target language')

    # =============== scrap part ================
    scrap_parser = main_sub_parser.add_parser('scrap', help='scrap related commands.')
    scrap_sub_parser = scrap_parser.add_subparsers()

    scrap_image_parser = scrap_sub_parser.add_parser('image', help='scrap images.')
    scrap_image_parser.set_defaults(which='scrap-image')
    scrap_image_parser.add_argument('--query', '-q', help='query words.')

    # =============== cabinet part ================
    cabinet_parser = main_sub_parser.add_parser('cab', help='cabinet related commands.')
    cabinet_sub_parser = cabinet_parser.add_subparsers()

    count_file_parser = cabinet_sub_parser.add_parser('count', help='scrap images.')
    count_file_parser.set_defaults(which='cab-count')
    count_file_parser.add_argument('--dir', '-d', default='./', help='dir to count.')
    count_file_parser.add_argument('--type', '-t', help='dir to count.')

    split_txt_parser = cabinet_sub_parser.add_parser('split', help='split txt file.')
    split_txt_parser.set_defaults(which='cab-split')
    split_txt_parser.add_argument('--file', '-f', required=True, help='file to split.')
    split_txt_parser.add_argument('--ratios', '-r', help='ratios.')
    split_txt_parser.add_argument('--names', '-n', help='names.')

    stackimgs_parser = cabinet_sub_parser.add_parser('stackimgs', help='stack images into one')
    stackimgs_parser.set_defaults(which='cab-stackimgs')
    stackimgs_parser.add_argument('--imgs', '-i', required=True, nargs='+', help='images list.')
    stackimgs_parser.add_argument('--dim', '-d', help='dims like 2x3.')

    apply_license_parser = cabinet_sub_parser.add_parser('license', help='automatically add/update license.')
    apply_license_parser.set_defaults(which='cab-license')
    apply_license_parser.add_argument('--owner', '-o', required=True, help='owner of license.')
    apply_license_parser.add_argument('--name', '-n', help='project name.')
    apply_license_parser.add_argument('--year', '-y', help='project year: 2016-2020.')
    apply_license_parser.add_argument('--url', '-u', default='manaai.cn', help='your website url.')
    apply_license_parser.add_argument('--dir', '-d', default='./', help='to apply license dir.')
    apply_license_parser.add_argument('--except', '-e', help='except extensions: xml,cc,h')

    # =============== data part ================
    data_parser = main_sub_parser.add_parser('data', help='data related commands.')
    data_sub_parser = data_parser.add_subparsers()

    view_voc_parser = data_sub_parser.add_parser('vocview', help='view voc.')
    view_voc_parser.set_defaults(which='data-vocview')
    view_voc_parser.add_argument('--image_dir', '-i', help='Root path of VOC image.')
    view_voc_parser.add_argument('--label_dir', '-l', help='Root path of VOC label.')

    view_txt_parser = data_sub_parser.add_parser('txtview', help='view voc.')
    view_txt_parser.set_defaults(which='data-txtview')
    view_txt_parser.add_argument('--image_dir', '-i', help='Root path of VOC image.')
    view_txt_parser.add_argument('--label_dir', '-l', help='Root path of VOC label.')

    view_coco_parser = data_sub_parser.add_parser('cocoview', help='view voc.')
    view_coco_parser.set_defaults(which='data-cocoview')
    view_coco_parser.add_argument('--image_dir', '-i', help='Root path of COCO images.')
    view_coco_parser.add_argument('--json', '-j', help='Root path of COCO annotations.json .')

    voc_label_parser = data_sub_parser.add_parser('voclabel', help='gather labels from annotations dir.')
    voc_label_parser.set_defaults(which='data-voclabel')
    voc_label_parser.add_argument('--anno_dir', '-d', help='dir to annotations.')

    split_voc_parser = data_sub_parser.add_parser('splitvoc', help='split VOC to train and val.')
    split_voc_parser.set_defaults(which='data-splitvoc')
    split_voc_parser.add_argument('--image_dir', '-i', help='Root path of VOC image.')
    split_voc_parser.add_argument('--label_dir', '-l', help='Root path of VOC label.')

    labelone2voc_parser = data_sub_parser.add_parser('labelone2voc', help='convert labelone to VOC.')
    labelone2voc_parser.set_defaults(which='data-labelone2voc')
    labelone2voc_parser.add_argument('--json_dir', '-j', help='Root of labelone json dir.')

    voc2coco_parser = data_sub_parser.add_parser('voc2coco', help='convert VOC to coco.')
    voc2coco_parser.set_defaults(which='data-voc2coco')
    voc2coco_parser.add_argument('--xml_dir', '-d', help='Root of xmls dir (Annotations/).')

    evalvoc_parser = data_sub_parser.add_parser('evalvoc', help='evaluation on VOC.')
    evalvoc_parser.set_defaults(which='data-evalvoc')
    evalvoc_parser.add_argument('-g', '--gt_dir', type=str, required=True, help="Ground truth path (can be xml dir or txt dir, coco json will support soon)")
    evalvoc_parser.add_argument('-d', '--det_dir', type=str, required=True, help="Detection result (should saved into txt format)")
    evalvoc_parser.add_argument('-im', '--images_dir', type=str, default='images', help="Raw images dir for animation.")
    evalvoc_parser.add_argument('-na', '--no-animation', help="no animation is shown.", action="store_true")
    evalvoc_parser.add_argument('-np', '--no-plot', help="no plot is shown.", action="store_true")
    evalvoc_parser.add_argument('-q', '--quiet', help="minimalistic console output.", action="store_true")
    evalvoc_parser.add_argument('-i', '--ignore', nargs='+', type=str, help="ignore a list of classes.")
    evalvoc_parser.add_argument('--set-class-iou', nargs='+', type=str, help="set IoU for a specific class.")

    return parser.parse_args()


def print_welcome_msg():
    print(Fore.BLUE + Style.BRIGHT + 'Alfred ' + Style.RESET_ALL +
          Fore.WHITE + '- Valet of Artificial Intelligence.' + Style.RESET_ALL)
    print('Author: ' + Fore.RED + Style.BRIGHT + __AUTHOR__ + Style.RESET_ALL)
    print('At    : ' + Fore.RED + Style.BRIGHT + __DATE__ + Style.RESET_ALL)
    print('Loc   : ' + Fore.RED + Style.BRIGHT + __LOC__ + Style.RESET_ALL)
    print('Star  : ' + Fore.RED + Style.BRIGHT + __git__ + Style.RESET_ALL)
    print('Ver.  : ' + Fore.RED + Style.BRIGHT + __VERSION__ + Style.RESET_ALL)


def main(args=None):
    args = arg_parse()
    if args.version:
        print(print_welcome_msg())
        exit(0)
    else:
        args_dict = vars(args)
        print_welcome_msg()
        try:
            module = args_dict['which'].split('-')[0]
            action = args_dict['which'].split('-')[1]
            print(Fore.GREEN + Style.BRIGHT)
            print('=> Module: ' + Fore.WHITE + Style.BRIGHT + module + Fore.GREEN + Style.BRIGHT)
            print('=> Action: ' + Fore.WHITE + Style.BRIGHT + action)
            if module == 'vision':
                if action == 'extract':
                    v_f = args_dict['video']
                    j = args_dict['jumps']
                    print(Fore.BLUE + Style.BRIGHT + 'Extracting from {}'.format(v_f))
                    video_extractor = VideoExtractor(jump_frames=j)
                    video_extractor.extract(v_f)
                elif action == 'reduce':
                    v_f = args_dict['video']
                    j = args_dict['jumps']
                    print(Fore.BLUE + Style.BRIGHT + 'Reduce from {}, jumps: {}'.format(v_f, j))
                    video_reducer = VideoReducer(jump_frames=j)
                    video_reducer.act(v_f)
                elif action == '2video':
                    d = args_dict['dir']
                    combiner = VideoCombiner(img_dir=d)
                    print(Fore.BLUE + Style.BRIGHT + 'Combine video from {}'.format(d))
                    print(Fore.BLUE + Style.BRIGHT + 'What the hell.. {}'.format(d))
                    combiner.combine()

                elif action == 'clean':
                    d = args_dict['dir']
                    print(Fore.BLUE + Style.BRIGHT + 'Cleaning from {}'.format(d))

                elif action == 'getface':
                    try:
                        from .modules.vision.face_extractor import FaceExtractor
                        import dlib

                        d = args_dict['dir']
                        print(Fore.BLUE + Style.BRIGHT + 'Extract faces from {}'.format(d))

                        face_extractor = FaceExtractor()
                        face_extractor.get_faces(d)
                    except ImportError:
                        print('This action needs to install dlib first. http://dlib.net')

            elif module == 'text':
                if action == 'clean':
                    f = args_dict['file']
                    print(Fore.BLUE + Style.BRIGHT + 'Cleaning from {}'.format(f))
                elif action == 'translate':
                    f = args.v
                    print(Fore.BLUE + Style.BRIGHT + 'Translate from {}'.format(f))
            elif module == 'scrap':
                if action == 'image':
                    q = args_dict['query']
                    q_list = q.split(',')
                    q_list = [i.replace(' ', '') for i in q_list]
                    image_scraper = ImageScraper()
                    image_scraper.scrap(q_list)
            elif module == 'cab':
                if action == 'count':
                    d = args_dict['dir']
                    t = args_dict['type']
                    logging.info('dir: {}, types: {}'.format(d, t))
                    count_file(d, t)
                elif action == 'split':
                    f = args_dict['file']
                    r = args_dict['ratios']
                    n = args_dict['names']
                    logging.info('files: {}, ratios: {}, names: {}'.format(f, r, n))
                    split_txt_file(f, r, n)
                elif action == 'stackimgs':
                    f = args_dict['imgs']
                    r = args_dict['dim']
                    logging.info('files: {}, dim: {}'.format(f, r))
                    stack_imgs(f, r)
                elif action == 'license':
                    owner = args_dict['owner']
                    project_name = args_dict['name']
                    year = args_dict['year']
                    url = args_dict['url']
                    d = args_dict['dir']
                    apply_license(owner, project_name, year, url, d)
            elif module == 'data':
                if action == 'vocview':
                    image_dir = args_dict['image_dir']
                    label_dir = args_dict['label_dir']
                    vis_voc(img_root=image_dir, label_root=label_dir)
                elif action == 'cocoview':
                    img_d = args_dict['image_dir']
                    json_f = args_dict['json']
                    vis_coco(img_d, json_f)
                elif action == 'txtview':
                    image_dir = args_dict['image_dir']
                    label_dir = args_dict['label_dir']
                    vis_det_txt(img_root=image_dir, label_root=label_dir)
                elif action == 'voclabel':
                    anno_dir = args_dict['anno_dir']
                    gather_labels(anno_dir)
                elif action == 'splitvoc':
                    logging.info('split VOC to train and val not implement yet.')
                    pass
                elif action == 'labelone2voc':
                    logging.info('labelone2voc not implement yet.')
                    pass
                elif action == 'voc2coco':
                    logging.info('start convert VOC to coco... Annotations root: {}'.format(args_dict['xml_dir']))
                    convert(args_dict['xml_dir'])
                elif action == 'evalvoc':
                    logging.info('start eval on VOC dataset..')
                    eval_voc(args)

        except Exception as e:
            print(Fore.RED, 'parse args error, type -h to see help. msg: {}'.format(e))


if __name__ == '__main__':
    main()
