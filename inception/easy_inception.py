import tensorflow as tf
import numpy as np
import urllib
import sys
import os


id_to_name_path = 'models/imagenet_synset_to_human_label_map.txt'
path_id_to_class = 'models/imagenet_2012_challenge_label_map_proto.pbtxt'


def imagenetToName(path):
    id_to_name = {}
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            elements = line.replace('\n',"").split('\t')
            uid = elements[0]
            name = elements[1]
            id_to_name[uid] = name
    return id_to_name

def imagenetLookUp(path):
    id_to_class = {} 
    class_to_id = {} 
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("  target_class: "):
                elements = line.split(": ")
                cls = int(elements[1])
            elif line.startswith("  target_class_string: "):
                elements = line.split(": ")
                uid = elements[1]
                uid = uid[1:-2]
                id_to_class[uid] = cls
                class_to_id[cls] = uid
    return id_to_class, class_to_id

# Just Build these damn Lookup tables. You want to put it into the Inception class? Go ahead. 
id_to_name = imagenetToName(id_to_name_path)
id_to_class, class_to_id = imagenetLookUp(path_id_to_class)


def idToClass(uid):
    return id_to_class[uid]

def idToName(uid, only_first_name=False):
    name = id_to_name[uid]
    if only_first_name:
        name = name.split(",")[0]
    return name

def classToName(class_label, only_first_name=False):
    uid = class_to_id[class_label]
    name = idToName(uid=uid, only_first_name=only_first_name)
    return name

class Inception:
    
    def __init__(self):
        graph_path = 'models/classify_image_graph_def.pb'
        self.graph = tf.Graph()
        with self.graph.as_default():
            with tf.gfile.FastGFile(graph_path, 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                _ = tf.import_graph_def(graph_def, name='')
            self.y_pred = self.graph.get_tensor_by_name('softmax:0')
            self.session = tf.Session(graph=self.graph)
    
    def predict(self, pred, only_first_name=True):
        idx = pred.argsort()
        top_k = idx[-1:]
        for cls in reversed(top_k):
            name = classToName(class_label=cls, only_first_name=only_first_name)
            return str(name)

    def close(self):
        self.session.close()
        
    def classify(self, image_path=None, image=None):
        image_data = tf.gfile.FastGFile(image_path, 'rb').read()
        pred = self.session.run(self.y_pred, {'DecodeJpeg/contents:0': image_data})
        pred = np.squeeze(pred)
        pred = self.predict(pred, 1)
        os.system("flite -voice slt -t 'Let me think. I think this is a " + pred + "'")



