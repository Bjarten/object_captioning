# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths
from model.config import cfg
from model.test import im_detect, im_detect_caption
from model.nms_wrapper import nms

from utils.timer import Timer
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os, cv2
import argparse

from nets.vgg16 import vgg16
from nets.resnet_v1 import resnetv1

np.set_printoptions(suppress=True)


CLASSES = ('__background__',  # always index 0
            'people', 'instruments', 
            'animals', 'vehicles')

NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt',),'res101': ('res101_faster_rcnn_iter_110000.ckpt',)}
DATASETS= {'pascal_voc': ('voc_2007_trainval',),'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}



ixtoword = np.load(cfg.IXTOWORD_PATH).item() ## LOAD AS DICT



# def vis_detections(im, class_name, dets, thresh=0.5):
#     """Draw detected bounding boxes."""
#     inds = np.where(dets[:, -1] >= thresh)[0]
#     if len(inds) == 0:
#         return
# 
#     im = im[:, :, (2, 1, 0)]
#     fig, ax = plt.subplots(figsize=(12, 12))
#     ax.imshow(im, aspect='equal')
#     for i in inds:
#         bbox = dets[i, :4]
#         score = dets[i, -1]
# 
#         ax.add_patch(
#             plt.Rectangle((bbox[0], bbox[1]),
#                           bbox[2] - bbox[0],
#                           bbox[3] - bbox[1], fill=False,
#                           edgecolor='red', linewidth=3.5)
#             )
#         ax.text(bbox[0], bbox[1] - 2,
#                 '{:s} {:.3f}'.format(class_name, score),
#                 bbox=dict(facecolor='blue', alpha=0.5),
#                 fontsize=14, color='white')
# 
#     ax.set_title(('{} detections with '
#                   'p({} | box) >= {:.1f}').format(class_name, class_name,
#                                                   thresh),
#                   fontsize=14)
#     plt.axis('off')
#     plt.tight_layout()
#     plt.draw()



def vis_detections_with_caption(im, class_name, dets, selected_answers, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        
        curr_answer = selected_answers[i,:]
        print ('------- Current selected bbox   : {:s}'.format(bbox))
        print ('------- Current bbox score      : {:f}'.format(score))
        print ('------- Current selected answers id       : {:s}'.format(curr_answer))
        str_answer = ' '.join(ixtoword[wid] for wid in curr_answer)
        print ('------- Current selected answers string   : {:s}'.format(str_answer))
        
        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=3.5)
            )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                  fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()


## original code
def demo(sess, net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        vis_detections(im, cls, dets, thresh=CONF_THRESH)


# Anh them vo        
def demo_img_caption(sess, net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    #scores, boxes = im_detect(sess, net, im)
    scores, boxes, answers = im_detect_caption(sess, net, im)
    timer.toc()
    
    
    
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))
    print('------ Output answers: {:s}'.format(answers))
    print('------ Out boxes shape     : {:s}'.format(boxes.shape))
    print('------ Out score shape     : {:s}'.format(scores.shape))   # IF rois = x --> shape = (x, 5) --> 5 object class, each has a score 
    #print('------ Out boxes     : {:s}'.format(boxes))
    #print('------ Out score     : {:s}'.format(scores))
    
    
    
    #print('Output answers shape: {}'.format(np.asarray(answers).shape))  ## e.g. (1, 300, 5)
    #answers = np.squeeze(answers, 0) ## fix problem when use 2 sees.run  ## ---> (300, 5)

    # Visualize detections for each class
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        
        #print ('dets shape: {:s}'.format(dets.shape))
        selected_answers = answers[keep, :]
        #print ('Selected answers: {:s}'.format(selected_answers))
        
        # Anh them vo --> select out answers
        #generated_sentences
        
        #vis_detections(im, cls, dets, thresh=CONF_THRESH)        
        vis_detections_with_caption(im, cls, dets, selected_answers, thresh=CONF_THRESH)

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='vgg16')
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        choices=DATASETS.keys(), default='pascal_voc_0712')
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    args = parse_args()

    # model path
    
    #main_path = ''
    
    demonet = args.demo_net
    dataset = args.dataset
    #tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default', NETS[demonet][0])
    #tfmodel = '/home/anguyen/workspace/paper_src/2018.iros.tod.source/main/tf-faster-rcnn/data/voc_2007_trainval+voc_2012_trainval/res101_faster_rcnn_iter_110000.ckpt'
    #tfmodel = '/home/anguyen/workspace/paper_src/2018.iros.ood.source/main/tf-faster-rcnn/data/voc_2007_trainval+voc_2012_trainval/res101_faster_rcnn_iter_110000.ckpt'
    #tfmodel = '/home/anguyen/workspace/paper_src/2018.iros.ood.source/main/tf-faster-rcnn/output/vgg16/voc_2007_trainval/default/backup/1st_ok_weight/vgg16_faster_rcnn_iter_5000.ckpt' ## weight with caption
    tfmodel = '/home/anguyen/workspace/paper_src/2018.iros.ood.source/main/tf-faster-rcnn/output/vgg16/voc_2007_trainval/default/vgg16_faster_rcnn_iter_5000.ckpt'
    #tfmodel = '/home/anguyen/workspace/paper_src/2018.iros.ood.source/main/tf-faster-rcnn/output/vgg16/voc_2007_trainval/default/vgg16_faster_rcnn_iter_28000.ckpt'

    if not os.path.isfile(tfmodel + '.meta'):
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth=True

    # init session
    sess = tf.Session(config=tfconfig)
    # load network
    if demonet == 'vgg16':
        net = vgg16()
    elif demonet == 'res101':
        net = resnetv1(num_layers=101)
    else:
        raise NotImplementedError
    net.create_architecture("TEST", 5, # 5 classes
                          tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))

    #im_names = ['1021442086.jpg', '100207720.jpg', '101654506.jpg', '1019604187.jpg']
    im_names = ['100207720.jpg', '101654506.jpg', '1019604187.jpg']
    #im_names = ['1019604187.jpg']
    #im_names = ['1029450589.jpg']
    
    for im_name in im_names:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Demo for data/demo/{}'.format(im_name))
        
        # Anh them vo
        demo_img_caption(sess, net, im_name)

    plt.show()
    
    print ('ALL DONE!')
