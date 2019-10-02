from argparse import ArgumentParser
import pandas as pd

def shrink_encoding(encoding):
    ncols = len(next(iter(encoding)))
    removed = []
    new_encodings = []
    for index in range(ncols):
        tmpencoding = encoding.copy()
        shrunkencoding = set()
        for x in tmpencoding:
            y = x[:index] + x[index+1:]
            shrunkencoding.add(y)
        if len(shrunkencoding) == len(encoding):
            removed.append(index)
            new_encodings.append(shrunkencoding)
    return removed, new_encodings

def removed_genes(removed, genes):
    newgenes = []
    for x in removed:
        y = genes[:x] + genes[x+1:]
        newgenes.append(y)
    return(newgenes)

def shrink_encodings(encodings, genes):
    newgenes = []
    newencodings = []
    for x, encoding in zip(genes, encodings):
        removed, shrunk = shrink_encoding(encoding)
        if removed:
            newencodings.extend(shrunk)
            removedgenes = removed_genes(removed, x)
            newgenes.extend(removedgenes)
    return newgenes, newencodings

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("markerfile", help="CSV of markers")
    args = parser.parse_args()

    encodings = {}
    data = pd.read_csv(args.markerfile)
    with open(args.markerfile) as in_handle:
        genes = in_handle.readline().strip().split(",")[1:]
        print(genes)
        for line in in_handle:
            tokens = line.strip().split(",")
            encodings[tokens[0]] = "".join(tokens[1:])

    minbits = 4
    bitlen = len(genes)
    startcodes = {y for x, y in encodings.items()}
    shrunk = [startcodes]
    newgenes = [genes]
    optimized = newgenes
    optimizedshrunk = shrunk
    while True:
        if len(newgenes) > 0 and len(newgenes[0]) == minbits:
            optimized = newgenes
            optimizedshrunk = shrunk
            break
        elif len(newgenes) == 0:
            break
        optimized = newgenes
        optimizedshrunk = shrunk
        newgenes, shrunk = shrink_encodings(shrunk, newgenes)
    # newgenes, shrunk = shrink_encodings([startcodes], [genes])
    # newgenes, shrunk = shrink_encodings(shrunk, newgenes)
    # newgenes, shrunk = shrink_encodings(shrunk, newgenes)
    # newgenes, shrunk = shrink_encodings(shrunk, newgenes)
    # newgenes, shrunk = shrink_encodings(shrunk, newgenes)
    print(len(optimized))
    for index, y in enumerate(set([tuple(x) for x in optimized])):
        cols = ["type"] + list(y)
        data[cols].to_csv(f"optimizedshrunk{index}.csv", index=False)
