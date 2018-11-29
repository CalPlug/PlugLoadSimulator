'''
contains functions that convenient math stuff, usually involving operations that are not
defined in normal mathematics but could be useful

@author: Klint
'''

# matrix stuff, collapse matrix in interesting ways

def collapse_matrix_cols(matrix: [list])-> list:
    '''flatten a matrix by m by n into a array of size m by adding columns together
    ie
        | a_00 a_10 ... a_m0 |
        | a_01 ............. |
        |  ................. |  = [a_00 + a_01 + .. + a_0n, a_10 + a_11 + ... + a_1n, a_m0 + a_m1 + ... + a_mn]
        | a_0n ........ a_mn |
    '''
    
    to_return = []
    size = len(matrix[0])
    
    for j in range(size):
        to_append = 0
        for i in range(len(matrix)):
            assert(len(matrix[i]) == size)
            to_append += matrix[i][j]
        to_return.append(to_append)
        
    return to_return

def collapse_matrix_rows(matrix: [list])-> list:
    '''flatten a matrix by adding rows
    '''
    to_return = []
    
    for row in matrix:
        to_return = sum(row)
        
    return to_return


# 
