#!/usr/bin/env python
def gridquare2latlng(gridsquare):
    from_lat, from_lng, stop_lat, stop_lng = 0,0,0,0

    ONE = gridsquare[0:1]
    TWO = gridsquare[1:2]
    THREE = gridsquare[2:3]
    FOUR = gridsquare[3:4]
    FIVE = gridsquare[4:5]
    SIX = gridsquare[5:6]
   
    # lon
    Field = ((ord(ONE.lower()) - 97.0) * 20.0) 
    Square = int(THREE) * 2
    SubSquareLow = (ord(FIVE.lower()) - 97.0) * (2.0/24.0)
    SubSquareHigh = SubSquareLow + (2.0/24.0)

    from_lng = Field + Square + SubSquareLow - 180
    to_lng = Field + Square + SubSquareHigh - 180

    # lat
    Field = ((ord(TWO.lower()) - 97.0) * 10.0) 
    Square = int(FOUR)
    SubSquareLow = (ord(SIX.lower()) - 97) * (1.0/24.0)
    SubSquareHigh = SubSquareLow + (1.0/24.0)

    from_lat = Field + Square + SubSquareLow - 90.0
    to_lat = Field + Square + SubSquareHigh - 90.0

    center_lng = from_lng + (to_lng - from_lng)/2
    center_lat = from_lat + (to_lat - from_lat)/2
    
    #return (from_lat, from_lng, to_lat, to_lng)
    return (center_lat, center_lng)

def gridquare2latlng2(gridsquare):
    from_lat, from_lng, stop_lat, stop_lng = 0,0,0,0

    ONE,TWO,THREE,FOUR,FIVE,SIX = list(gridsquare.lower())
   
    # lon
    Field = ((ord(ONE.lower()) - 97.0) * 20.0) 
    Square = int(THREE) * 2
    SubSquareLow = (ord(FIVE.lower()) - 97.0) * (2.0/24.0)
    SubSquareHigh = SubSquareLow + (2.0/24.0)

    from_lng = Field + Square + SubSquareLow - 180
    to_lng = Field + Square + SubSquareHigh - 180

    # lat
    Field = ((ord(TWO.lower()) - 97.0) * 10.0) 
    Square = int(FOUR)
    SubSquareLow = (ord(SIX.lower()) - 97) * (1.0/24.0)
    SubSquareHigh = SubSquareLow + (1.0/24.0)

    from_lat = Field + Square + SubSquareLow - 90.0
    to_lat = Field + Square + SubSquareHigh - 90.0

    center_lng = from_lng + (to_lng - from_lng)/2
    center_lat = from_lat + (to_lat - from_lat)/2
    
    #return (from_lat, from_lng, to_lat, to_lng)
    return (center_lat, center_lng)

if __name__ == '__main__':
    print gridquare2latlng('JN88oj')
    print gridquare2latlng2('JN88oj')
