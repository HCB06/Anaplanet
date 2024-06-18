# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 23:32:16 2024

@author: hasan
"""

import time
from colorama import Fore
import plan_di as pdi
from sklearn.datasets import load_wine
import numpy as np

data = load_wine()
X = data.data
y = data.target

x_train, x_test, y_train, y_test = pdi.split(X, y, 0.6, 42)

x_train = x_train.tolist()
x_test = x_test.tolist()

scaler_params, x_train, x_test = pdi.standard_scaler(x_train, x_test)


y_train, y_test = pdi.encode_one_hot(y_train, y_test)

show_metrics = True

x_test, y_test = pdi.auto_balancer(x_test, y_test)

W = pdi.fit(x_train, y_train)

test_model = pdi.evaluate(x_test, y_test, show_metrics, W)
test_preds = test_model[pdi.get_preds()]
test_acc = test_model[pdi.get_acc()]

model_name = 'wine'
model_type = 'PLAN'
weights_type = 'txt'
weights_format = 'f'
model_path = 'PlanModels/'
class_count = 3

pdi.save_model(model_name, model_type, class_count, test_acc, weights_type, weights_format, model_path, scaler_params, W)

precisison, recall, f1 = pdi.metrics(y_test, test_preds)
print('Precision: ', precisison, '\n', 'Recall: ', recall, '\n', 'F1: ', f1)

y_test = pdi.decode_one_hot(y_test)


for i in range(len(x_test)):
    Predict = pdi.predict_model_ram(x_test[i], scaler_params, W)
    time.sleep(0.6)
    if np.argmax(Predict) == y_test[i]:
        print(Fore.GREEN + 'Predicted Output(index):', np.argmax(Predict), 'Real Output(index):', y_test[i])
    else:
        print(Fore.RED + 'Predicted Output(index):', np.argmax(Predict), 'Real Output(index):', y_test[i])
        
        
