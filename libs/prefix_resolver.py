import string

chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def fromto(a, b):
    # generate a sequence of multiple characters
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
    


