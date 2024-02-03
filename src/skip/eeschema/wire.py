'''
Created on Feb 2, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''
import math
from skip.container import ElementContainer
from skip.sexp.parser import ParsedValue, ParsedValueWrapper
# from skip.at_location import AtValue

class WireWrapper(ParsedValueWrapper):
    def __init__(self,v:ParsedValue):
        super().__init__(v)
        self._slope = None 
        self._unit_vector = None 
        self._wire_mag = None
        
    def translation(self, by_x:float, by_y:float):
        self._unit_vector = None 
        self._slope = None 
        for p in self.points:
            p.value = [round(p.value[0] + by_x, 6), round(p.value[1] + by_y, 6)]
            
    
    @property 
    def points(self):
        return self.pts.xy
    
    @property 
    def start(self):
        return self.pts.xy[0]
    
    @property 
    def end(self):
        return self.pts.xy[1]
    
    @property 
    def length(self):
        if self._wire_mag is None:
            self._calculate_specs()
        
        return round(self._wire_mag, 4)
    
    def list_labels(self, recursive_crawl:bool=False):
        all_labels = []
        if recursive_crawl:
            all_wires = self.list_all_connected()
            for w in all_wires:
                for lbl in w.list_labels(False):
                    if lbl not in all_labels:
                        all_labels.append(lbl)
        else:
            for p in self.list_points(1):
                lbls = self.parent.label.within_circle(p[0], p[1], 0.6)
                for lb in lbls:
                    if lb not in all_labels:
                        all_labels.append(lb)
        
        return all_labels
    
    
    def list_global_labels(self, recursive_crawl:bool=False):
        all_labels = []
        
        if recursive_crawl:
            all_wires = self.list_all_connected()
            for w in all_wires:
                for lbl in w.list_global_labels(False):
                    if lbl not in all_labels:
                        all_labels.append(lbl)
        else:
            for p in self.list_points(1):
                lbls = self.parent.global_label.within_circle(p[0], p[1], 0.6)
                for lb in lbls:
                    if lb not in all_labels:
                        all_labels.append(lb)
        
        return all_labels
    
    def list_all_connected(self, into_list:list = None):
        
        if into_list is None:
            into_list = []
        for p in [self.start, self.end]:
            found_wires = self.parent.wire.all_at(p[0], p[1])
            for w in found_wires:
                if w not in into_list:
                    into_list.append(w)
                    if w != self:
                        w.list_all_connected(into_list)
                        
        return into_list
            
    
    def list_points(self, step:float=1):
        uv = self.unit_vector
        max_len = self.length
        start_point = self.start.value
        
        if step <= 0:
            raise ValueError('Step must be positive')
        
        points_list = []
        cur_len = 0
        while cur_len < max_len:
            cur_point = [ round((start_point[0] + (uv[0]*cur_len)), 5), 
                          round((start_point[1] + (uv[1]*cur_len)), 5)]
            points_list.append(cur_point)
            
            cur_len += step
            
        points_list.append(self.end.value)
        
        return points_list
    
    @property 
    def unit_vector(self):
        if self._unit_vector is not None:
            return self._unit_vector
        self._calculate_specs()
        return self._unit_vector
        
    
    def _calculate_specs(self):
        start_x = self.start.value[0]
        start_y = self.start.value[1]
        
        end_x = self.end.value[0]
        end_y = self.end.value[1]
        
        dx = end_x - start_x
        dy = end_y - start_y 
        
        wire_mag = math.sqrt( (dx*dx) + (dy*dy))
        
        if dx == 0:
            slope = 1e9
            vect_mag = dy
            self._unit_vector = (0, 1.0)
        else:
            slope = dy/dx
            vect_mag = math.sqrt(  (1) + (slope**2))
            normalizer = 1/vect_mag
            self._unit_vector = (normalizer, slope/normalizer) 
        
        self._wire_mag = wire_mag
        
        self._slope = slope
        
        
    def __repr__(self):
        start = self.start.value 
        end = self.end.value 
        return f'<Wire {start} - {end}>'
        

class WireContainer(ElementContainer):
    def __init__(self, elements:list):
        super().__init__(elements)
        
    def all_at(self, x:float, y:float):
        ret_val = []
        
        for w in self:
            for p in w.points:
                if p.value[0] == x and p.value[1] == y:
                    ret_val.append(w)
        
        return ret_val
    
    
    def within_circle(self, xcoord:float, ycoord:float, radius:float):
        '''    
            Find all elements of this container that are within the 
            circle of radius radius, centered on xcoord, ycoord.
            
            @note: only works for elements that have a
            suitable 'at' or 'location' attribute
        
        '''
        retvals = []
        if not len(self._elements):
            return retvals
        
        
        target_coords = [xcoord, ycoord]
        for el in self:
            append = False
            for p in el.points:
                if self._distance_between(target_coords, p.value) <= radius:
                    append = True
                    
            if append:
                retvals.append(el)
            
        return retvals
        
    def __repr__(self):
        return f'<WireContainer ({len(self)} wires)>'