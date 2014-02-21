class annotation:

    def __init__(self, name):
        self.start = 0
        self.end = -1
        self.name = name
    
    def set_interval(self, a, b):
        self.start = a
        self.end = b

    def from_json(json):
        return annotation("")
    
    def draw(self, screen):
        pass

class bool_annotation(annotation):

    def __init__(self, name):
        annotation.__init__(self, name)
        self.value = None

    def from_json(json):
        return annotation("")
    
    def set_value(self,v):
        self.value = v
    
    def draw(self,screen):
        pass

class point_annotation(annotation):

    def __init__(self, name):
        pass

class bounding_box_annotation(annotation):

    def __init__(self, name):
        pass

class polygon_annotation(annotation):

    def __init__(self, name, default=[]):
        pass

class text_annotation(annotation):

    def __init__(self, name, default=""):
        pass

class float_annotation(annotation):

    def __init__(self, name, default=0.0):
        pass

class annotation_manager:

    def __init__(self, domain_filename=None, instance_filename=None):
        self.domain = {}
    
    def add_label(s):
        self.domain[s.name] = s
