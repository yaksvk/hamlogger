import string
import xml.etree.ElementTree as et

chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def fromto(a, b):
    """
    Generates a list of combinations from a to b, for example:
    fromto('6', 'C') = [6, 7, 8, 9, A, B, C]
    fromto('AX', 'BC') = [AX, AY, AZ, BA, BB, BC]
    """
    
    if len(a) != len(b):
        raise ValueError('Unable to compare, parameters are not equally long.')
        return None

    sequence = [ chars[i] for i in range(chars.find(a[0]), chars.find(b[0])+1) ]
    
    if len(a) > 1:

         result_sequence = fromto(a[1:], b[1:])
         sequence2 = []
         for i in sequence:
             for j in result_sequence:
                 sequence2.append(''.join((i, j)))
         return sequence2
    else:
         return sequence
    
class Resolver(object):
    
    def __init__(self, db_file):
        """
        Loads a list of DXCC entities and their ITU and other ham radio prefixes. Excpects a db_file, which
        is an XML file containing a set "record" elements with details
        """
        
        tree = et.parse(db_file)
        root = tree.getroot()
        
        self.countries = []
        self.prefixes = {}
        self.max_prefix = 0
        
        for i, record in enumerate(root.findall('record')):
            
            country = {
                'name': record.find('country').text,
                'lat': record.find('lat').text, 
                'long': record.find('long').text,
                'itu_zone': record.find('itu_zone').text,
                'cq_zone': record.find('cq_zone').text,
                'utc': record.find('utc').text,
            }
            
            total_prefixes = []
            
            # first prefix
            if record.find('prefix').text:
                total_prefixes.append(record.find('prefix').text)
            
            # ITU prefixes
            p = record.find('itu_prefixes').text
            if p:
                prefs = p.replace(' ', '').split(',')
                for pref in prefs:
                    if '-' in pref:
                        ft = pref.split('-')
                        total_prefixes.extend(fromto(ft[0], ft[1]))
                    elif pref:
                        total_prefixes.append(pref)
                        
            # other prefixes
            p = record.find('other_prefixes').text
            if p:
                prefs = p.replace(' ', '').split(',')
                for pref in prefs:
                    if '-' in pref:
                        ft = pref.split('-')
                        total_prefixes.extend(fromto(ft[0], ft[1]))
                    elif pref:
                        total_prefixes.append(pref)
            
            #print total_prefixes
            self.countries.append(country)
            
            for prefix in total_prefixes:
                if len(prefix) > self.max_prefix:
                    self.max_prefix = len(prefix)
                
                self.prefixes[prefix] = i
                
    def get_entity_for_call(self, call):
        """
        get a full call and then shorten it (start from the point of the longest prefix that we have) until we
        find a matching prefix (longest possible leftmost substring of the callsign that matches)
        """
        if call:
            for i in range(self.max_prefix,0,-1):
                if call[:i] in self.prefixes:
                    return self.countries[self.prefixes[call[:i]]]
            return None
        else:
            return None
       
        
