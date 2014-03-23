import json
from sys import stderr

class feature:
    def __init__(self):
        self.name = ""
        self.default = None
        self.ftype = None
        self.value = None
    
    def __init__(self, json, default=None):
        self.name = json.get("name", "")
        self.default = json.get("default", default)
        self.ftype = json.get("type", None)
        self.value = json.get("value", None)
    
    def parse_value(self, json):
        pass
    
    def __str__(self):
        return str(self.to_json())

    def to_json(self, verbose=True):
        ret = {"name" : self.name}
        if verbose:
            ret["default"] = self.default
            
            if self.ftype is not None:
                ret["type"] = self.ftype
        
        if self.value is not None:
            ret["value"] = self.value
        
        return ret
    
    def get_instance(self):
        return feature(self.to_json())

    def set_values(self, json):
        self.value = json.get("value", self.default)

    def merge(self, a, l, i, r):
        if i > (l+r)/2:
            self.value = a.value

class bool_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json, True)
    
    def get_instance(self):
        return bool_feature(self.to_json())

class str_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json, "")
    
    def get_instance(self):
        return str_feature(self.to_json())

class float_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json, 0)

    def get_instance(self):
        return float_feature(self.to_json())
    
    def merge(self, a, l, i, r):
        right_rate = float(i - l)/float(r - l)
        left_rate = 1.0 - right_rate
        
        self.value = left_rate * self.value + right_rate * a.value

class int_feature(float_feature):
    def __init__(self, json):
        feature.__init__(self, json, 0)

    def get_instance(self):
        return int_feature(self.to_json())

    def merge(self, a, l, i, r):
        float_feature.merge(self, a, l, i, r)
        self.value = int(self.value)

class choice_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json)
        self.values = []
        
        for v in json.get("values",[]):
            self.values.append(v)
        self.value = json.get("value", None)

        if not self.value in self.values:
            self.value = None
        if not self.default in self.values:
            self.default = None
    
    def to_json(self, verbose=True):
        ret = feature.to_json(self, verbose)
        if verbose:
            ret["values"] = self.values
        return ret

    def get_instance(self):
        return choice_feature(self.to_json())

class bbox_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json, [[0,0],[0,0]])
    
    def get_instance(self):
        return bbox_feature(self.to_json())

    def merge(self, a, l, i, r):
        if self.value is None:
            self.value = self.default
        if a.value is None:
            a.value = a.default
        
        right_rate = float(i - l)/float(r - l)
        left_rate = 1.0 - right_rate
        
        ret = [[0,0],[0,0]]
        for x in range(2):
            for y in range(2):
                ret[x][y] = int( left_rate * self.value[x][y] + \
                                        right_rate * a.value[x][y] )
        self.value = ret

class vector_feature(bbox_feature):
    def __init__(self, json):
        bbox_feature.__init__(self, json)
    
    def get_instance(self):
        return vector_feature(self.to_json())

class point_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json, [0,0])

    def get_instance(self):
        return point_feature(self.to_json())

    def merge(self, a, l, i, r):
        if self.value is None:
            self.value = self.default
        if a.value is None:
            a.value = a.default

        right_rate = float(i - l)/float(r - l)
        left_rate = 1.0 - right_rate

        ret = [0,0]
        for x in range(2):
            ret[x] = int( left_rate * self.value[x] + \
                          right_rate * a.value[x] )
        self.value = ret

class_by_name = {"bool": bool_feature,
                 "string": str_feature,
                 "float": float_feature,
                 "int": int_feature,
                 "choice": choice_feature,
                 "bbox": bbox_feature,
                 "vector": vector_feature,
                 "point": point_feature
                }

def get_class_by_type(t):
    return class_by_name.get(t, feature)

class annotation:
    def __init__(self, json):
        self.frame = json.get("frame", -1)
        self.name = json.get("name", "")
        self.is_unique = json.get("is_unique", False)
        self.is_global = json.get("is_global", False)
        
        self.features = []
        for f in json.get("features",[]):
            self.features.append(get_class_by_type(f["type"])(f))
    
    def __str__(self):
        return str(self.to_json())
    
    def to_json(self, verbose=True):
        ret = { "name" : self.name,
                "features" : map(lambda x : x.to_json(verbose), self.features)
              }
        if self.frame != -1:
            ret["frame"] = self.frame
        if verbose:
            ret["is_unique"] = self.is_unique
            ret["is_global"] = self.is_global
        if self.frame != -1:
            ret["frame"] = self.frame
        
        return ret
    
    def set_values(self, json):
        self.frame = json.get("frame", -1)
        for f in json["features"]:
            for my_f in self.features:
                if my_f.name == f["name"]:
                    my_f.set_values(f)
    
    def get_instance(self):
        return annotation(self.to_json())

    def merge_features(self, b, l, i, r):
        ret = self.get_instance()
        for idx, f in enumerate(ret.features):
            ret.features[idx].merge(b.features[idx], l, i, r)
        ret.frame = i
        return ret
    
    def interpolate(self, b):
        if self.name != b.name:
            stderr.write("Invalid interpolation\n")
            return []
        
        start = self.frame
        end = b.frame
        
        ret = []
        for x in xrange(start, end+1):
            ret.append(self.merge_features(b, start, x, end))
        
        return ret

class annotation_manager:
    
    def __init__(self, domain_filename=None):
        self.domain = {}
        self.labels = []
        self.domain_name = ""
        self.domain_filename = None
        self.instance_name = ""
        self.instance_filename = None
        
        self.video_filename = None
        self.sequence_filename = None
        
        self.sequence = []
        
        if domain_filename is not None:
            self.parse_domain(domain_filename)
    
    def parse_domain(self, domain_filename):

        f = open(domain_filename).read()
        d = json.loads(f)

        self.domain = {}
        self.labels = []
        self.domain_name = d["name"]
        self.domain_filename = domain_filename
        
        for l in d["labels"]:
            self.domain[l["name"]] = annotation(l)
    
    def parse_instance(self, instance_filename):
        self.labels = []
        
        f = open(instance_filename).read()
        i = json.loads(f)
        
        if self.domain_filename is not None and \
           self.domain_filename != i["domain"]:
            return
        elif self.domain_filename is None:
            self.parse_domain(i["domain"])
        
        self.instance_name = i["name"]
        self.domain_filename = i["domain"]
        self.sequence = []
        
        self.video_filename = i["video_filename"]
        self.sequence_filename = i["sequence_filename"]
        
        for s in i["sequence"]:
            labels = map(lambda x : x["name"], s)

            frames = map(lambda x : x["frame"], s)
            ordered_frames = list(frames)
            ordered_frames.sort()
            
            if len(filter(lambda x: x not in self.domain, labels)) > 0:
                stderr.write("Invalid labels\n")
            elif len(set(labels)) > 1:
                stderr.write("Different labels within the same annotation\n")
            elif frames != ordered_frames or len(set(frames)) != len(frames) :
                stderr.write("Invalid sort of annotations\n")
            else:
                next_annotation = []
                for ss in s:
                    next_instance = self.domain[ss["name"]].get_instance()
                    next_instance.set_values(ss)
                    next_annotation.append(next_instance)
                self.sequence.append(next_annotation)
                
                #for i in xrange(len(next_annotation)-1):
                    #for x in map(lambda x: x.to_json(False),
                                 #next_annotation[i].interpolate(
                                                         #next_annotation[i+1])
                                 #):
                        #print x
                    #print
                #print
    
    def domain_to_json(self):
        return { "name" : self.domain_name,
                 "labels" : map(lambda x : self.domain[x].to_json(),
                                self.domain)
               }
    
    def instance_to_json(self):
        return { "domain" : self.domain_filename,
                 "name" : self.instance_name,
                 "video_filename" : self.video_filename,
                 "sequence_filename" : self.sequence_filename,
                 "sequence" : map(lambda x :
                                  map(lambda y: y.to_json(False), x),
                              self.sequence)
               }
    
    def add_label(s):
        self.domain[s.name] = s
    
    def sort_annotations(self):
        self.sequence.sort(key=(lambda x : x[0].frame))
    
    def add_annotation(self, annotation):
        self.sequence.append([annotation])
        self.sort_annotations()
    
    def add_point_to_annotation(self, index, frame):
        seq = self.sequence[index]
        nearest_left = seq[0]
        dist = abs(frame - seq[0].frame)
        ret = self.sequence[index]
        
        for x in seq:
            if x.frame <= frame:
                new_dist = abs(frame - x.frame)
                if new_dist < dist:
                    nearest_left = x
                    dist = new_dist
        
        if nearest_left.frame == frame:
            return ret
        
        new_instance = nearest_left.get_instance()
        new_instance.frame = frame
        ret = seq
        
        self.sequence[index].append(new_instance)
        self.sequence[index].sort(key=(lambda x : x.frame))
        self.sort_annotations()
        
        return ret
    
    def rm_point_from_annotation(self, index, frame):
        
        seq = self.sequence[index]
        nearest_left = seq[0]
        dist = abs(frame - seq[0].frame)
        inner_index = -1
        ret = self.sequence[index]
        
        for idx, x in enumerate(seq):
            if frame == x.frame:
                inner_index = idx
                break
        
        if inner_index != -1 and len(self.sequence[index]) > 1:
            self.sequence[index] = self.sequence[index][:inner_index] + \
                                   self.sequence[index][inner_index+1:]
        
        self.sequence[index].sort(key=(lambda x : x.frame))
        self.sort_annotations()
        
        return self.sequence[index]
    
    def get_annotation(self, index):
        return self.sequence[index]
    
    def get_annotation_index(self, annotation):
        an = annotation
        
        for idx, x in enumerate(self.sequence):
            if an in x:
                return idx
        
        return 0
