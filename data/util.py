def n_largest_indices(lst, n):

    
    lst_copy = lst.copy()
    
    for i in range(n):
        max_index = lst_copy.index(max(lst_copy))
        yield max_index
        lst_copy.pop(max_index)