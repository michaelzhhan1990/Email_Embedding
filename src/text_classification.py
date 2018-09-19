import argparse
import utils
import config
import os
from LSTM import LSTM
from cnn import CNN
from GRU import GRU
import data
import run_process
import logging
import config_train_files
import config_test_files
import tensorflow as tf

def main():
    # set up check points location
    utils.safe_mkdir('../checkpoints')
    utils.safe_mkdir(config.CPT_PATH)
    logging.basicConfig(filename=config.LOG_PATH,level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices={'train', 'inference'},
                        default='train', help="mode. if not specified, it's in the train mode")
    args = parser.parse_args()

    if config.MODEL_NAME=='GRU':
        compute_graph = GRU(config.MODEL_NAME)
    elif config.MODEL_NAME =='LSTM':
        compute_graph = LSTM(config.MODEL_NAME)
    elif config.MODEL_NAME =='CNN':
        compute_graph = CNN(config.MODEL_NAME)

    compute_graph.vocab_size = config.VOCAB_SIZE

    if args.mode == 'train':
        local_dest = config_train_files.TRAIN_DATA_NAME
        local_dest_label = config_train_files.TRAIN_LABEL_NAME
        validation_dest=config_train_files.VALIDATION_DATA_NAME
        validation_dest_label=config_train_files.VALIDATION_LABEL

        if config.PRETRAIN_EMBD_TAG:  # use start pretrain embd or not
            embd_dest = config.PRETRAIN_EMBD_PATH
            data.get_pretrain_embedding(compute_graph,embd_dest)

        iterator,training_init_op= data.get_data(local_dest,local_dest_label)
        next_element=iterator.get_next()
        _,validation_init_op =data.get_data(validation_dest,validation_dest_label,iterator)
        run_process.train(compute_graph,next_element,training_init_op,validation_init_op,config.EPOCH_NUM)

    elif args.mode == 'inference':
        if os.path.isdir(config.PROCESSED_PATH):
            local_dest = config.PROCESSED_PATH + config_test_files.INFERENCE_DATA_NAME_PROCESSED
            local_dest_label=None
            if hasattr(config_test_files,'INFERENCE_LABEL_NAME'):
                local_dest_label = config.PROCESSED_PATH + config_test_files.INFERENCE_LABEL_NAME

            if config.PRETRAIN_EMBD_TAG:  # use start pretrain embd or not
                embd_dest = config.PRETRAIN_EMBD_PATH
                data.get_pretrain_embedding(compute_graph,embd_dest)

            iterator,inference_init_op = data.get_data(local_dest, local_dest_label)
            next_element=iterator.get_next()
            run_process.inference(compute_graph,next_element,inference_init_op)


if __name__ == '__main__':
    main()
