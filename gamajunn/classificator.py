import configparser
from keras.layers.core import Dense
from keras.optimizers import SGD
import numpy as np
from keras.models import Sequential, model_from_json
from gamajunn import utils, config

def load_config():
    config = configparser.ConfigParser()
    config.read('config_last_files.ini')
    path_to_bag = config['last_address']['path_to_bag']
    path_to_architech_nn = config['last_address']['path_to_architech_nn']
    path_to_weights_nn = config['last_address']['path_to_weights_nn']
    return path_to_bag, path_to_architech_nn, path_to_weights_nn

def load_nn(path_to_architech_nn, path_to_weights_nn):
    json_file = open(path_to_architech_nn, 'r')
    load_model_json = json_file.read()
    json_file.close()

    loaded_model = model_from_json(load_model_json)
    loaded_model.load_weights(path_to_weights_nn)
    return loaded_model


def fill_fight_vec():
    theme_inp_arr = []
    theme_out_arr = []
    for expert_art in utils.get_list_test():
        inp_arr_iter = []
        out_arr_iter = []
        learn_vectors, n = utils.fill_vec(expert_art, load_config()[0], utils.get_val_doc(), config.num_word)
        for learn_vector in learn_vectors:
            inp_arr_iter.append(learn_vector)
        for j in range(n):
            out_arr_i = []
            for num in range(1, utils.get_num_class() + 1):
                if expert_art.expert_themes.id == num:
                    out_arr_i.append(1)
                else:
                    out_arr_i.append(0)
            out_arr_iter.append(out_arr_i)
        theme_inp_arr.append(np.asarray(inp_arr_iter))
        theme_out_arr.append(np.asarray(out_arr_iter))
    return theme_inp_arr, theme_out_arr


load_nn().compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='rmsprop')
l = 1
    for k in theme_inp_arr:
        print('theme = ', l)
        pred_k = model.predict(k)
        print(pred_k)
        mean_pred_k = utils.result_predict(pred_k)
        print('res: ', mean_pred_k)
        l += 1
