import json

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
    
    def __str__(self):
        return str(self.to_json())

    def to_json(self):
        ret = {"name" : self.name,
               "default" : self.default,
               "type" : self.ftype
              }
        if self.value is not None:
            ret["value"] = self.value
        if self.ftype is not None:
            ret["type"] = self.ftype

        return ret
    
    def get_instance(self):
        return feature(self.to_json())

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

class int_feature(feature):
    def __init__(self, json):
        feature.__init__(self, json, 0)
    
    def get_instance(self):
        return int_feature(self.to_json())

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
    
    def to_json(self):
        ret = feature.to_json(self)
        ret["values"] = self.values
        return ret

class_by_name = {"bool": bool_feature,
                 "string": str_feature,
                 "int": int_feature,
                 "choice": choice_feature
                }

def get_class_by_type(t):
    return class_by_name.get(t, feature)

class annotation:
    
    def __init__(self, json):
        self.start = json.get("start", -1)
        self.end = json.get("end", -1)
        self.name = json.get("name", "")
        self.is_unique = json.get("is_unique", False)
        self.is_global = json.get("is_global", False)
        
        self.features = []
        for f in json.get("features",[]):
            self.features.append(get_class_by_type(f["type"])(f))
    
    def __str__(self):
        return str(self.to_json())
    
    def to_json(self):
        ret = { "name" : self.name,
                "is_unique" : self.is_unique,
                "is_global" : self.is_global,
                "features" : map(lambda x : x.to_json(), self.features)
              }
        if self.start != -1:
            ret["start"] = self.start
        if self.end != -1:
            ret["end"] = self.end
        
        return ret

    def get_instance(self):
        return annotation(self.to_json())
    
    def set_interval(self, a, b):
        self.start = a
        self.end = b

class annotation_manager:
    
    def __init__(self, domain_filename=None, instance_filename=None):
        self.domain = {}
        self.labels = []
        self.name = ""
        
        if domain_filename is not None:
            f = open(domain_filename).read()
            d = json.loads(f)
            self.name = d["name"]
            for l in d["labels"]:
                self.domain[l["name"]] = annotation(l)
            
            for l in self.domain:
                print self.domain[l]
                print
    
    def add_label(s):
        self.domain[s.name] = s
