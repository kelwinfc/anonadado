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
    
    def to_json(self, verbose=True):
        ret = feature.to_json(self, verbose)
        if verbose:
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
    
    def to_json(self, verbose=True):
        ret = { "name" : self.name,
                "features" : map(lambda x : x.to_json(verbose), self.features)
              }
        if verbose:
            ret["is_unique"] = self.is_unique
            ret["is_global"] = self.is_global
        if self.start != -1:
            ret["start"] = self.start
        if self.end != -1:
            ret["end"] = self.end
        
        return ret
    
    def set_values(self, json):
        self.set_interval(json["start"], json["end"])
        for f in json["features"]:
            for my_f in self.features:
                if my_f.name == f["name"]:
                    my_f.set_values(f)
    
    def get_instance(self):
        return annotation(self.to_json())
    
    def set_interval(self, a, b):
        self.start = a
        self.end = b

class annotation_manager:
    
    def __init__(self, domain_filename=None):
        self.domain = {}
        self.labels = []
        self.domain_name = ""
        self.domain_filename = ""
        self.instance_name = ""
        self.instance_filename = ""
        self.itype = None
        
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
        
        if self.domain_filename != i["domain"]:
            return
        self.instance_name = i["name"]
        self.itype = i["type"]
        self.instance_filename = i["filename"]
        self.sequence = []
        
        for s in i["sequence"]:
            if not s["name"] in self.domain:
                continue
            else:
                next_instance = self.domain[s["name"]].get_instance()
                next_instance.set_values(s)
                self.sequence.append(next_instance)
    
    def domain_to_json(self):
        return { "name" : self.domain_name,
                 "labels" : map(lambda x : self.domain[x].to_json(),
                                self.domain)
               }
    
    def instance_to_json(self):
        return { "domain" : self.domain_filename,
                 "name" : self.instance_name,
                 "type" : self.itype,
                 "filename" : self.instance_filename,
                 "sequence" : map(lambda x : x.to_json(False), self.sequence)
               }
    
    def add_label(s):
        self.domain[s.name] = s
