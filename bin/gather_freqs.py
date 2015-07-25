import plac

def main(in_loc, out_loc):
    out_file = open(out_loc, 'w')
    this_key = None
    this_freq = 0
    df = 0
    for line in open(in_loc):
        line = line.strip()
        if not line:
            continue
        freq, key = line.split('\t', 1)
        freq = int(freq)
        if this_key is not None and key != this_key:
            out_file.write('%d\t%d\t%s\n' % (this_freq, df, this_key))
            this_key = key
            this_freq = freq
            df = 1
        else:
            this_freq += freq
            df += 1
    out_file.write('%d\t%d\t%s\n' % (this_freq, df, this_key))
    out_file.close()


if __name__ == '__main__':
    plac.call(main)
