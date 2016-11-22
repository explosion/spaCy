config=config.py
output=./model_output
paddle train --config=$config \
              --save_dir=$output \
              --job=train \
              --use_gpu=false \
              --trainer_count=4 \
              --num_passes=10 \
              --log_period=20 \
              --dot_period=20 \
              --show_parameter_stats_period=100 \
              --test_all_data_in_one_period=1 \
              --config_args=batch_size=100 \
              2>&1 | tee 'train.log'_
