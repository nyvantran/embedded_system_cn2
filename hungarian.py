import numpy as np

def hungary(cost_matrix: np.ndarray):
    cost_matrix = np.atleast_2d(cost_matrix)
    n_rows, n_cols = cost_matrix.shape
    n = max(n_rows, n_cols)
    
    matrix = np.zeros((n, n))
    matrix[:n_rows, :n_cols] = cost_matrix
    
    matrix -= matrix.min(axis=1, keepdims=True)
    matrix -= matrix.min(axis=0, keepdims=True)
    
    while True:
        # Tìm số đường thẳng tối thiểu che phủ tất cả số 0
        marked_rows, marked_cols = min_cover(matrix)
        
        # Nếu số đường bằng n, đã tìm thấy lời giải tối ưu
        if (len(marked_rows) + len(marked_cols)) == n:
            break
            
        # Cập nhật ma trận 
        mask = np.ones((n, n), dtype=bool)
        mask[marked_rows, :] = False
        mask[:, marked_cols] = False
        
        min_uncovered = matrix[mask].min()
        matrix[mask] -= min_uncovered
        # Cộng vào các điểm giao nhau của 2 đường thẳng
        matrix[np.ix_(marked_rows, marked_cols)] += min_uncovered

    # Trích xuất kết quả 
    row_ind, col_ind = find_matching(matrix)
    
    # Lọc lại kết quả để loại bỏ phần pad
    final_rows, final_cols = [], []
    for r, c in zip(row_ind, col_ind):
        if r < n_rows and c < n_cols:
            final_rows.append(r)
            final_cols.append(c)
            
    row_ind = np.array(final_rows)
    col_ind = np.array(final_cols)
    return row_ind, col_ind, cost_matrix[row_ind, col_ind].sum()

def min_cover(matrix):
    n = matrix.shape[0]
    # Tìm matching cực đại trên các số 0
    row_match, col_match = find_matching(matrix)
    
    marked_rows = set(range(n)) - set(row_match)
    marked_cols = set()
    
    new_marks = True
    while new_marks:
        new_marks = False
        # Đánh dấu cột có số 0 nằm trên hàng đã đánh dấu
        for r in list(marked_rows):
            zeros = np.where(matrix[r] == 0)[0]
            for c in zeros:
                if c not in marked_cols:
                    marked_cols.add(c)
                    new_marks = True
                    # Đánh dấu hàng có matching nằm trên cột vừa đánh dấu
                    for r_match, c_match in zip(row_match, col_match):
                        if c_match == c and r_match not in marked_rows:
                            marked_rows.add(r_match)
    
    # Đường thẳng che phủ = (Hàng không đánh dấu) + (Cột được đánh dấu)
    cover_rows = list(set(range(n)) - marked_rows)
    cover_cols = list(marked_cols)
    return cover_rows, cover_cols

def find_matching(matrix):
    n = matrix.shape[0]
    row_match = []
    col_match = []
    used_cols = set()
    
    for r in range(n):
        zeros = np.where(matrix[r] == 0)[0]
        for c in zeros:
            if c not in used_cols:
                row_match.append(r)
                col_match.append(c)
                used_cols.add(c)
                break
    return np.array(row_match), np.array(col_match)