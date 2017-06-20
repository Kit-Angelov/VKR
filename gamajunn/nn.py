"""
Частоту терминов среди документов берем в процентах от общего числа документов.
Классификацию и обучение проводим по 300 слов из документа, после обучения всего документа результат усредняем
"""
import tensorflow as tf
from keras.layers.core import Dense
from keras.optimizers import SGD
import numpy as np
from keras.models import Sequential
from gamajunn import utils, config, wikilib, classificator, model_utils
import time
import configparser
from math import sqrt
from django.utils import timezone


def get_init_config():
    path_to_logs = config.path_to_logs
    path_to_bag = config.path_to_bag
    #path_to_architech_nn = config.path_to_architech_nn
    path_to_weights_nn = config.path_to_weights_nn
    input_learn_arr = config.input_learn_arr
    output_learn_arr = config.output_learn_arr
    input_test_arr = config.input_test_arr
    output_test_arr = config.output_test_arr
    num_word = config.num_word

    config_parser = configparser.ConfigParser()
    config_parser['last_address'] = {}
    config_parser['last_address']['path_to_bag'] = path_to_bag
    #config_parser['last_address']['path_to_architech_nn'] = path_to_architech_nn
    #config_parser['last_address']['path_to_weights_nn'] = path_to_weights_nn
    with open('config_last_files.ini', 'w') as config_last_files:
        config_parser.write(config_last_files)
    return path_to_logs, path_to_bag, path_to_weights_nn


# получаем обучающую и тестовую выборку
def get_list_fit_and_test():
    expert_list_fit, expert_list_test = utils.get_list_fit_and_test()
    return expert_list_fit, expert_list_test


# заполняем мешок слов
def fill_bag(expert_list, path_to_bag):
    for expert_art in expert_list:
        utils.fill_bag(expert_art.expert_art_text, path_to_bag)


# заполняем входящий и выходящий вектор обучающей выборки
def fill_fit_vec(expert_list_fit, path_to_bag):
    input_learn_arr = config.input_learn_arr
    output_learn_arr = config.output_learn_arr
    num_word = config.num_word
    for expert_art in expert_list_fit:
        learn_vectors, n = utils.fill_vec(expert_art.expert_art_text, path_to_bag, utils.get_val_doc(), num_word)
        for learn_vector in learn_vectors:
            input_learn_arr.append(learn_vector)
        for i in range(n):
            out_arr_i = []
            for num in range(1, utils.get_num_class() + 1):
                if expert_art.expert_themes.id == num:
                    out_arr_i.append(1)
                else:
                    out_arr_i.append(0)
            output_learn_arr.append(out_arr_i)

    X = np.asarray(input_learn_arr)
    Y = np.asarray(output_learn_arr)
    return X, Y


# заполняем входящей и выходящий вектор тестовой выборки
def fill_test_vec(expert_list_test, path_to_bag):
    input_test_arr = config.input_test_arr
    output_test_arr = config.output_test_arr
    num_word = config.num_word
    for expert_art in expert_list_test:
        learn_vectors, n = utils.fill_vec(expert_art.expert_art_text, path_to_bag, utils.get_val_doc(), num_word)
        for learn_vector in learn_vectors:
            input_test_arr.append(learn_vector)
        for j in range(n):
            out_arr_i = []
            for num in range(1, utils.get_num_class() + 1):
                if expert_art.expert_themes.id == num:
                    out_arr_i.append(1)
                else:
                    out_arr_i.append(0)
            output_test_arr.append(out_arr_i)

    Z = np.asarray(input_test_arr)
    L = np.asarray(output_test_arr)
    return Z, L


def fill_fight_vec(expert_list_test, path_to_bag):
    num_word = config.num_word
    theme_inp_arr = []
    theme_out_arr = []
    for expert_art in expert_list_test:
        inp_arr_iter = []
        out_arr_iter = []
        learn_vectors, n = utils.fill_vec(expert_art.expert_art_text, path_to_bag, utils.get_val_doc(), num_word)
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


# сама сеть
def neural_netword(expert_list_fit, expert_list_test, path_to_logs, path_to_bag, path_to_weights_nn):
    # обучающая и тестовая выборки
    X, Y = fill_fit_vec(expert_list_fit, path_to_bag)
    Z, L = fill_test_vec(expert_list_test, path_to_bag)
    #theme_inp_arr, theme_out_arr = fill_fight_vec(expert_list_test)

    # размер входного вектора
    input_size = utils.count_keys(path_to_bag)
    n_classes = utils.get_num_class()
    hidden_layer_1 = int(sqrt(input_size * n_classes))
    hidden_layer_2 = int(sqrt(hidden_layer_1 * n_classes))
    print('len_input_vector: ', input_size)

    # построение модели сети
    learning_rate = 0.001
    batch_size = 1
    display_step = 10
    model_path = path_to_weights_nn

    x = tf.placeholder(tf.float32, [None, input_size])
    y = tf.placeholder(tf.float32, [None, n_classes])

    weights_1 = tf.Variable(tf.random_normal([input_size, hidden_layer_1],  stddev=0.01, dtype=tf.float32))
    #weights_2 = tf.Variable(tf.random_normal([hidden_layer_1, hidden_layer_2], stddev=0.01, dtype=tf.float32))
    weights_3 = tf.Variable(tf.random_normal([hidden_layer_1, n_classes], stddev=0.01, dtype=tf.float32))

    biases_1 = tf.Variable(tf.zeros([hidden_layer_1]))
    #biases_2 = tf.Variable(tf.zeros([hidden_layer_2]))
    biases_3 = tf.Variable(tf.zeros([n_classes]))

    layer_1 = tf.nn.relu(tf.add(tf.matmul(x, weights_1), biases_1))
    #layer_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, weights_2), biases_2))
    pred = tf.nn.softmax(tf.matmul(layer_1, weights_3) + biases_3)

    cost = tf.nn.l2_loss(y - pred, name="squared_error_cost")
    optimizer = tf.train.RMSPropOptimizer(learning_rate=learning_rate).minimize(cost)
    tf.summary.scalar('loss', cost)
    merged = tf.summary.merge_all()

    init = tf.global_variables_initializer()

    saver = tf.train.Saver()

    print('start 1st session..')

    with tf.Session() as sess:
        sess.run(init)
        writer = tf.summary.FileWriter(path_to_logs, sess.graph)
        writer.add_graph(sess.graph)
        for epoch in range(450):
            sess.run(optimizer, feed_dict={x: X, y: Y})
            summary = sess.run(merged, feed_dict={x: X, y: Y})
            writer.add_summary(summary, epoch)
            writer.flush()

            print('Epoch ', epoch)
            print('Out', sess.run(pred, feed_dict={x: X,
                                                   y: Y}))
            print('cost ', sess.run(cost, feed_dict={x: X,
                                                     y: Y}))

        print("Fist Optimization Finish")

        # точность обучения
        correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        print("Accuracy:", accuracy.eval({x: Z, y: L}))
        print('len_input_vector: ', input_size)

        #сохраняем веса
        saver.save(sess, model_path)
        print('Сохраняем веса')


"""
    model = Sequential()
    model.add(Dense(7000, input_dim=input_size, activation='relu'))
    #model.add(Dense(800, activation='sigmoid'))
    model.add(Dense(utils.get_num_class(), activation='softmax'))

    sgd = SGD(lr=0.1)
    model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='rmsprop')
    start = time.time()
    model.fit(X, Y, batch_size=2, nb_epoch=6, verbose=1, validation_data=(Z, L))
    end = time.time()
    delta = end - start
    print(model.predict_proba(X))

    score = model.evaluate(X, Y, verbose=0)
    print('accuracy:', score[1])
    print('score:', score[0])
    predict = model.predict(Z)
    print('time = ', delta)
    print(predict)
    l = 1
    for k in theme_inp_arr:
        print('theme = ', l)
        pred_k = model.predict(k)
        print(pred_k)
        mean_pred_k = utils.result_predict(pred_k)
        print('res: ', mean_pred_k)
        l += 1
    #записываем модель сети
    model_json = model.to_json()
    with open(path_to_architech_nn, 'w') as json_file:
        json_file.write(model_json)
    model.save_weights(path_to_weights_nn)
"""


def work():
    art_list = utils.check_art()
    if True:                       #len(art_list) > 0:
        #utils.get_and_add_new_expert_art(art_list)
        path_to_logs, path_to_bag, path_to_weights_nn = get_init_config()
        expert_list = utils.get_expert_list()
        expert_list_fit, expert_list_test = get_list_fit_and_test()
        fill_bag(expert_list, path_to_bag)
        neural_netword(expert_list_fit, expert_list_test, path_to_logs, path_to_bag, path_to_weights_nn)
        """for article in art_list:
            themes_id = classificator.classification(article.article_text)
            if len(themes_id) > 0:
                model_utils.add_themes_in_art(article, themes_id)"""
    else:
        pass
