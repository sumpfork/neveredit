"""Utilities for processing arrays of vectors"""
import numarray
numarray.Error.setMode(dividebyzero="raise")

def crossProduct( set1, set2):
    """Compute element-wise cross-product of two arrays of vectors.
    
       I{set1, set2} -- sequence objects with 1 or more
       3-item vector values.  If both sets are
       longer than 1 vector, they must be the same
       length.
    
       returns a double array with x elements,
       where x is the number of 3-element vectors
       in the longer set
    """
    set1 = numarray.asarray( set1, 'd')
    set1 = numarray.reshape( set1, (-1, 3))
    set2 = numarray.asarray( set2, 'd')
    set2 = numarray.reshape( set2, (-1, 3))
    ux = set1[:,0]
    uy = set1[:,1]
    uz = set1[:,2]
    vx = set2[:,0]
    vy = set2[:,1]
    vz = set2[:,2]
    result = numarray.zeros( (len(set1),3), set1.typecode())
    result[:,0] = (uy*vz)-(uz*vy)
    result[:,1] = (uz*vx)-(ux*vz)
    result[:,2] = (ux*vy)-(uy*vx)
    return result

def crossProduct4( set1, set2 ):
    """Cross-product of 3D vectors stored in 4D arrays

    Identical to crossProduct otherwise.
    """
    set1 = numarray.asarray( set1, 'd')
    set1 = numarray.reshape( set1, (-1, 4))
    set2 = numarray.asarray( set2, 'd')
    set2 = numarray.reshape( set2, (-1, 4))
    ux = set1[:,0]
    uy = set1[:,1]
    uz = set1[:,2]
    vx = set2[:,0]
    vy = set2[:,1]
    vz = set2[:,2]
    result = numarray.zeros( (len(set1),4), set1.typecode())
    result[:,0] = (uy*vz)-(uz*vy)
    result[:,1] = (uz*vx)-(ux*vz)
    result[:,2] = (ux*vy)-(uy*vx)
    return result
        

def magnitude( vectors ):
    """Calculate the magnitudes of the given vectors
    
    I{vectors} -- sequence object with 1 or more
    3-item vector values.
    
    @return: a double array with x elements,
             where x is the number of 3-element vectors
    """
    vectors = numarray.asarray( vectors,'d')
    if not (len(numarray.shape(vectors))==2 and numarray.shape(vectors)[1] in (3,4)):
        vectors = numarray.reshape( vectors, (-1,3))
    vectors = vectors*vectors
    # should just use sum?
    result = vectors[:,0]
    numarray.add( result, vectors[:,1], result )
    numarray.add( result, vectors[:,2], result )
    numarray.sqrt( result, result )
    return result
    
def normalise( vectors ):
    """Get normalised versions of the vectors.
    
    I{vectors} -- sequence object with 1 or more
    3-item vector values.
    
    Will raise ZeroDivisionError if there are 0-magnitude
    vectors in the set.

    @return: a double array with x 3-element vectors,
             where x is the number of 3-element vectors in "vectors"
    """
    vectors = numarray.asarray( vectors, 'd')
    vectors = numarray.reshape( vectors, (-1,3))
    mags = numarray.reshape( magnitude( vectors ), (-1, 1))
        
    return numarray.divide( vectors, mags)


if __name__ == "__main__":
    def test():
        data = numarray.array( [
                [0,0,0],[1,0,0],[0,1,0],
                [1,0,0],[0,0,0],[0,1,0],
        ],'d')
        print magnitude( data )
        try:
            normalise( data )
        except ZeroDivisionError:
            print 'got zero div'
        data = numarray.array( [
                [1,1,0],[1,0,0],[0,1,0],
                [1,0,1],[0,1,1],[1,1,0],
        ],'d')
        print normalise( data )
        print normalise( [2.0,2.0,0.0] )
        print crossProduct( data, [-1,0,0])
        print crossProduct( [0,0,1], [-1,0,0])
    test()

