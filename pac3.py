#!/usr/bin/env python

import csv
import json


class YearData:
    def __init__(self, *args, **kwargs):
        self.year = kwargs.get('year', None)
        self.methods = []
        self.aggregate_method = None
    
    def to_dict(self):
        l = []
        for elem in self.methods:
            l.append(elem.to_dict())
        
        d = {
            str(self.year): l
        }
        
        return d
    
    def get_method(self, method_name):
        try:
            md = MethodData(name=method_name)
            return self.methods[self.methods.index(md)]
        except:
            return MethodData(name=method_name, recstolen=0, reclost=0)
    
    def add_method(self, method, aggregate_method=None):
        if aggregate_method:
            if not self.aggregate_method:
                self.aggregate_method = aggregate_method

            if method.name != aggregate_method:
                method.name = 'others'

        if not method in self.methods:
            self.methods.append(method)
            return
            
        m = self.methods[self.methods.index(method)]
        m.add(method)
    
    def __eq__(self, other):
        return self.year == other.year

    def __str__(self):
        s = "<MethodYear: {}>".format(self.year)
        for item in self.methods:
            s += "\n\t{}".format(item)
        return s


class MethodData:
    def __init__(self, *args, **kwargs):
        self.name = None
        n = kwargs.get('name', None)
        if n:
            n = n.replace(',', '/')
            n = n.split('/')
            if len(n) > 1:
                self.name = n[1].strip()
            else:
                self.name = n[0].strip()
            
        self.total = 1
        try:
            self.recstolen = int(kwargs.get('recstolen'))
        except:
            self.recstolen = 0
        try:
            self.reclost = int(kwargs.get('reclost'))
        except:
            self.reclost = 0

    def add(self, other):
        self.__add__(other)

    def __eq__(self, other):
        return self.name == other.name
    
    def __add__(self, other):
        self.total += 1
        self.recstolen += other.recstolen
        self.reclost += other.reclost

    def to_dict(self):
        d = {
            self.name: {
                'total': self.total,
                'recstolen': self.recstolen,
                'reclost': self.reclost
            }
        }
        
        return d
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<MethodData: {}> [total: {}, recstolen: {}, reclost: {}]".format(
            self.name,
            self.total,
            self.recstolen,
            self.reclost
        )


class Pac3:
    def __init__(self, filename):
        self.filename = filename
        self.data = None

    def load_file(self):
        l = []
        with open(self.filename) as csvfile:
            databreachreader = csv.DictReader(csvfile)
            for row in databreachreader:
                l.append(row)
        self.data = l
        return l

    def methods_per_year(self, aggregate_method=None):
        l = []
        for item in self.data:
            year_data = YearData(year=item['year'])
            method_data = MethodData(
                name=item['method'],
                recstolen=item['recstolen'],
                reclost=item['reclost']
            )
            if year_data not in l:
                l.append(year_data)
            else:
                year_data = l[l.index(year_data)]

            year_data.add_method(method_data, aggregate_method=aggregate_method)
                
        d = {}
        for year in l:
            d.update(year.to_dict())
            
        return d, l


def save_json(data, filename):
    s = json.dumps(data, sort_keys=True, indent=2)
    with open(filename, 'w') as f:
        f.write(s)

    
def save_csv_hacked(data, filename):
    fields = ['year', 'hacked_total', 'hacked_reclost', 'hacked_recstolen', 'others_total', 'others_reclost', 'others_recstolen', 'total_total', 'total_reclost', 'total_recstolen']
    l = []
    for year in data:
        y = year.year
        hacked = year.get_method('hacked')
        others = year.get_method('others')
        l.append([y, hacked.total, hacked.reclost, hacked.recstolen, others.total, others.reclost, others.recstolen, (hacked.total+others.total), (hacked.reclost+others.reclost), (hacked.recstolen+others.recstolen)])
    
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for elem in l:
            csvwriter.writerow(elem)


def run():
    filename = 'Book1.csv'
    pac3 = Pac3(filename)
    pac3.load_file()
    years_dict, years_list = pac3.methods_per_year(aggregate_method='hacked')
    save_json(years_dict, 'hacked_year.json')
    save_csv_hacked(years_list, 'hacked_year.csv')
        

if __name__ == '__main__':
    run()