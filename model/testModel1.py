import os
import re
import numpy as np
import paho.mqtt.client as mqtt

# 动作分类名
motion_names = ['RightAngle', 'SharpAngle', 'Lightning', 'Triangle', 'Letter_h', 'letter_R', 'letter_W', 'letter_phi',
                'Circle', 'UpAndDown', 'Horn', 'Wave', 'NoMotion']

# 定义目录路径
DEF_SAVE_TO_PATH = './TraningData/'
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
    print(f"Received message: {msg.topic} {msg.payload.decode('utf-8')}")

    # 处理接收到的角度数据
    angle_data = process_message(msg.payload)
    print(f"Processed angle data: {angle_data}")

    # 将数据添加到训练数据列表中
    # 假设你已经知道如何获取相应的标签
    # 这里只是一个示例标签，需要替换为适合的数据标签
    file_list.append(angle_data)
    labels.append(0)  # 假设标签是0，可以根据实际情况更改


# 加载数据集的函数
def load_dataset(root_dir, max_rows=None):
    file_list = []
    labels = []
    for filename in os.listdir(root_dir):
        if filename.endswith(DEF_FILE_FORMAT):
            match = re.match(rf'^([\w]+)_([\d]+){DEF_FILE_FORMAT}$', filename)
            if match:
                motion_name = match.group(1)
                number_str = match.group(2)
                number = int(number_str)
                if 0 <= number <= DEF_FILE_MAX:
                    if motion_name in motion_to_label:
                        file_path = os.path.join(root_dir, filename)
                        # 使用max_rows参数限制读取的行数
                        data = np.loadtxt(file_path, delimiter=' ', usecols=(3, 4, 5), max_rows=max_rows)
                        file_list.append(data)
                        labels.append(motion_to_label[motion_name])
                    else:
                        print(f"Motion name not recognized: {filename}")
                else:
                    print(f"Number out of range: {filename}")
            else:
                print(f"Invalid file name format: {filename}")
    return file_list, labels


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
    file_list, labels = shuffle(file_list, labels, random_state=42)

    # 切分训练集与测试集
    x_train, x_test, y_train, y_test = train_test_split(file_list, labels, test_size=0.2, random_state=42)

    # 标签转换为整数
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)

    return x_train, y_train, x_test, y_test


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

# 等待数据收集
import time

time.sleep(30)  # 等待30秒以便收集一些数据

# 停止接收消息
client.loop_stop()

# 数据预处理
x_train, y_train, x_test, y_test = preprocess_data(file_list, labels)

# 如果没有数据，结束程序
if x_train is None:
    print("No data available. Exiting...")
    exit(1)

# 训练模型（可以使用一些简单的传统算法，如KNN等）
# 这里只是一个简单的实现，可以替换为其他算法

from collections import Counter

def knn_predict(x_train, y_train, x_test, k=3):
    # 简单的KNN实现：计算距离并找出最近的k个邻居
    predictions = []
    for test_point in x_test:
        distances = np.linalg.norm(x_train - test_point, axis=1)
        nearest_neighbors = np.argsort(distances)[:k]
        nearest_labels = y_train[nearest_neighbors]
        predicted_label = Counter(nearest_labels).most_common(1)[0][0]
        predictions.append(predicted_label)
    return np.array(predictions)

# 使用KNN进行预测
y_pred = knn_predict(x_train.reshape(x_train.shape[0], -1), y_train, x_test.reshape(x_test.shape[0], -1))

# 评估模型（简单输出预测结果的精度）
accuracy = np.mean(y_pred == y_test)
print(f"Accuracy: {accuracy * 100:.2f}%")
