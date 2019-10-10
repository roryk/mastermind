# mastermind
Given a celltype x gene matrix of 0 and 1 values, where 0 in a cell means that
celltype does not express the gene and 1 means the celltype expresses the gene,
reduce the matrix to include the smallest number of columns possible that still
uniquely identify each cell type. This also tries all combinations of genes. The
idea is that for each column in the minimized matrix, you would stain all genes
in the column with the same color. The resulting matrix is the minimium number
of colors you need to resolve the celltypes.
