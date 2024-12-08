import os
import re
import numpy as np
import paho.mqtt.client as mqtt
import csv
from collections import Counter

# 动作分类名
motion_names = ['RightAngle', 'SharpAngle', 'Lightning', 'Triangle', 'Letter_h', 'letter_R', 'letter_W', 'letter_phi',
                'Circle', 'UpAndDown', 'Horn', 'Wave', 'NoMotion']

# 定义目录路径
DEF_SAVE_TO_PATH = './TraningData_8_17/'
DEF_FILE_NAME = 'training_data.npy'
DEF_FILE_MAX = 50
DEF_FILE_FORMAT = '.txt'

# 动作名称到标签的映射
motion_to_label = {name: idx for idx, name in enumerate(motion_names)}

# MQTT设置
mqtt_broker = "192.168.201.156"  # 你的MQTT代理地址
mqtt_port = 1883  # 端口
client = mqtt.Client(protocol=mqtt.MQTTv311)  # 使用更稳定的 MQTT v3.1.1 协议

# 用于保存接收到的数据
file_list = []
labels = []

# 数据收集标志
collecting_data = False

# 处理MQTT消息
def process_message(msg_payload):
    data = msg_payload.decode('utf-8')  # 将字节解码为字符串

    # 使用正则提取角度数据
    angle_data = {}
    matches = re.findall(r"angle([XYZ]):\s*(-?\d+\.\d+)", data)

    for axis, angle in matches:
        angle_data[axis] = float(angle)

    # 将角度数据转化为数组格式
    angle_array = np.array([angle_data.get('X', 0), angle_data.get('Y', 0), angle_data.get('Z', 0)])
    return angle_array


# 连接回调函数
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    # 订阅角度数据主题
    client.subscribe("sensor/mpu6050/angles")


# 消息接收回调函数
def on_message(client, userdata, msg):
    global collecting_data  # 使用全局变量控制数据收集
    print(f"Received message: {msg.topic} {msg.payload.decode('utf-8')}")

    if collecting_data:
        # 处理接收到的角度数据
        angle_data = process_message(msg.payload)
        print(f"Processed angle data: {angle_data}")

        # 将数据添加到训练数据列表中
        file_list.append(angle_data)
        labels.append(0)  # 假设标签是0，可以根据实际情况更改

        # 如果收集到100次数据，停止收集
        if len(file_list) >= 100:
            collecting_data = False
            print("收集到 100 条数据，停止数据收集。")


# 数据预处理
def preprocess_data(file_list, labels):
    # 确保数据不为空
    if len(file_list) == 0 or len(labels) == 0:
        print("No data collected. Please check your MQTT connection and message handling.")
        return None, None, None, None

    # 假设你已经收集了一些数据
    file_list = np.array(file_list)
    labels = np.array(labels)

    # 进行数据打乱
    indices = np.random.permutation(len(file_list))
    file_list = file_list[indices]
    labels = labels[indices]

    # 切分训练集与测试集
    split_ratio = 0.8
    split_index = int(len(file_list) * split_ratio)
    x_train, x_test = file_list[:split_index], file_list[split_index:]
    y_train, y_test = labels[:split_index], labels[split_index:]

    return x_train, y_train, x_test, y_test


# 训练KNN模型的函数（手动实现KNN）
def knn_predict(x_train, y_train, x_test, k=3):
    # 简单的KNN实现：计算距离并找出最近的k个邻居
    predictions = []
    for test_point in x_test:
        distances = np.linalg.norm(x_train - test_point, axis=1)  # 计算欧几里得距离
        nearest_neighbors = np.argsort(distances)[:k]
        nearest_labels = y_train[nearest_neighbors]
        predicted_label = Counter(nearest_labels).most_common(1)[0][0]
        predictions.append(predicted_label)
    return np.array(predictions)


# 保存数据为CSV文件
def save_data_to_csv(file_list, labels, filename='training_data.csv'):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow(['X', 'Y', 'Z', 'Label'])

        # 写入数据
        for data, label in zip(file_list, labels):
            writer.writerow([data[0], data[1], data[2], label])

    print(f"数据已保存到 {filename} 文件。")


# MQTT连接设置
client.username_pw_set(username="MQTT1", password="123456")
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(mqtt_broker, mqtt_port, 60)
except Exception as e:
    print(f"Error connecting to broker: {e}")
    exit(1)

# 启动MQTT客户端循环
print("Starting MQTT client loop...")
client.loop_start()  # 使用 loop_start 允许程序异步接收消息

# 提示用户输入
user_input = input("请输入 1 来开始收集数据：")

if user_input == '1':
    # 设置开始收集数据
    collecting_data = True
    print("开始收集数据，请稍等...")

    # 等待数据收集（此处设置最大为 100 次数据）
    while collecting_data:
        pass

    # 停止接收消息
    client.loop_stop()

    # 数据预处理
    x_train, y_train, x_test, y_test = preprocess_data(file_list, labels)

    # 如果没有数据，结束程序
    if x_train is None:
        print("No data available. Exiting...")
        exit(1)

    # 使用KNN进行预测
    y_pred = knn_predict(x_train.reshape(x_train.shape[0], -1), y_train, x_test.reshape(x_test.shape[0], -1))

    # 评估模型（简单输出预测结果的精度）
    accuracy = np.mean(y_pred == y_test)
    print(f"Accuracy: {accuracy * 100:.2f}%")

    # 保存数据为CSV文件
    save_data_to_csv(file_list, labels)

else:
    print("输入无效，程序结束。")
    exit(1)
