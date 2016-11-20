def write_parameter(outfile, feats):
    """
    From https://github.com/baidu/Paddle/issues/490

    outfile: Output file name with string type. **Note**, it should be the same as it in the above config.
    feats: Parameter with float type.
    """
    version = 0
    value_size  = 4; # means float type
    ret = b""
    for feat in feats:
        ret += feat.tostring()
    size = len(ret) / 4
    fo = open(outfile, 'wb')
    fo.write(struct.pack('iIQ', version, value_size, size))
    fo.write(ret)


# config=trainer_config.py
# output=./model_output
# paddle train --config=$config \
#              --save_dir=$output \
#              --job=train \
#              --use_gpu=false \
#              --trainer_count=4 \
#              --num_passes=10 \
#              --log_period=20 \
#              --dot_period=20 \
#              --show_parameter_stats_period=100 \
#              --test_all_data_in_one_period=1 \
#              2>&1 | tee 'train.log'
