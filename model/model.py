# import os
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, classification_report
# from joblib import dump, load
# import csv
# import time
# import paho.mqtt.client as mqtt
#
# # 配置路径
# base_path = "."  # 替换为实际文件夹路径
# folders = ["class1", "class2", "class3", "class4"]  # 每个类别的文件夹名称
#
# # 数据加载
# def load_data(base_path, folders):
#     data = []
#     labels = []
#
#     for label, folder in enumerate(folders):
#         folder_path = os.path.join(base_path, folder)
#         for file_name in os.listdir(folder_path):
#             if file_name.endswith(".csv"):
#                 file_path = os.path.join(folder_path, file_name)
#                 try:
#                     # 加载 CSV 数据，跳过第一行标题
#                     df = pd.read_csv(file_path, skiprows=1)
#                     data.extend(df.values.tolist())
#                     labels.extend([label] * len(df))  # 为每行数据添加标签
#                 except Exception as e:
#                     print(f"Failed to load {file_path}: {e}")
#
#     return pd.DataFrame(data), pd.Series(labels)
#
# # 加载数据
# data, labels = load_data(base_path, folders)
#
# # 划分训练集和测试集
# X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
#
# # 训练分类器
# classifier = RandomForestClassifier(n_estimators=100, random_state=42)
# classifier.fit(X_train, y_train)
#
# # 测试分类器
# y_pred = classifier.predict(X_test)
# print("Accuracy:", accuracy_score(y_test, y_pred))
# print("Classification Report:\n", classification_report(y_test, y_pred))
#
# # 保存模型
# model_path = "angle_classifier.joblib"
# dump(classifier, model_path)
# print(f"Model saved to {model_path}")
#
# # 使用模型进行预测
# def predict_new_data(model_path, new_data_path):
#     # 加载模型
#     model = load(model_path)
#     # 加载新数据，跳过标题行
#     new_data = pd.read_csv(new_data_path, skiprows=1).values
#     # 预测
#     predictions = model.predict(new_data)
#     return predictions
#
#
#
#
#
# # MQTT 配置
# MQTT_BROKER = "10.20.40.160"  # 替换为实际的 MQTT 服务器地址
# MQTT_PORT = 1883
# MQTT_USERNAME = "Angle"  # 替换为实际用户名
# MQTT_PASSWORD = "123456"  # 替换为实际密码
# MQTT_TOPIC = "sensor/mpu6050/angles"  # 替换为实际主题
#
# # 初始化变量
# collected_data = {}  # 存储每个标识符对应的数据
# expected_num_count = 0  # 期待的下一个标识符
# file_count = 1  # 文件计数
#
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT Broker!")
#         client.subscribe(MQTT_TOPIC)
#     else:
#         print(f"Failed to connect, return code {rc}")
#
# def on_message(client, userdata, msg):
#     global collected_data, expected_num_count, file_count
#
#     message = msg.payload.decode("utf-8")
#     lines = message.split("\n")
#
#     # 获取消息标识符
#     try:
#         num_count = int(lines[0].strip())  # 假设标识符在第一行
#     except ValueError:
#         print("Failed to parse the message identifier")
#         return
#
#     # 如果标识符不是期望的，则跳过此消息并等待下一个标识符为0的消息
#     if num_count != expected_num_count:
#         print(f"Waiting for next data batch with identifier {expected_num_count}, received {num_count}")
#         return
#
#     # 开始收集数据
#     if num_count == expected_num_count:
#         print(f"Started collecting data for batch {expected_num_count}...")
#         collected_data[num_count] = lines[1:]  # 存储数据（忽略第一行的标识符）
#
#         # 检查是否已收集到完整的一组数据（标识符为 0 到 9）
#         if len(collected_data) == 10:  # 如果收到标识符 0 到 9 的所有数据
#             filename = f"predict.csv"
#             with open(filename, mode="w", newline="", encoding="utf-8") as file:
#                 writer = csv.writer(file)
#                 writer.writerow(["angleX", "angleY", "angleZ"])  # CSV 文件标题
#
#                 # 将缓存的所有数据写入 CSV
#                 for i in range(10):
#                     line = collected_data.get(i)
#                     if line:
#                         for data in line:
#                             angles = parse_angles(data)
#                             if angles:
#                                 writer.writerow(angles)
#             # 示例预测
#             new_data_path = "predict.csv"  # 替换为实际新数据文件路径
#             predictions = predict_new_data(model_path, new_data_path)
#             print("Predictions for new data:", predictions)
#             # print(f"Saved data to {filename}")
#
#             # 重置收集状态，准备接收下一个数据包
#             expected_num_count = 0  # 下一组数据的标识符从 0 开始
#             collected_data.clear()  # 清空缓存数据
#             file_count += 1  # 更新文件计数
#             time.sleep(0.5)  # 等待后再继续收集
#
#         else:
#             expected_num_count += 1  # 如果数据还不完整，期望下一个标识符
#
# def parse_angles(data):
#     try:
#         parts = data.split("\t")
#         angleX = float(parts[0].strip())
#         angleY = float(parts[1].strip())
#         angleZ = float(parts[2].strip())
#         return [angleX, angleY, angleZ]
#     except Exception as e:
#         print(f"Failed to parse data: {data}, Error: {e}")
#         return None
#
# def main():
#     # 初始化 MQTT 客户端
#     client = mqtt.Client()
#     client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
#     client.on_connect = on_connect
#     client.on_message = on_message
#
#     try:
#         client.connect(MQTT_BROKER, MQTT_PORT, 60)
#         client.loop_forever()
#     except Exception as e:
#         print(f"Error connecting to MQTT Broker: {e}")
#
# if __name__ == "__main__":
#     main()
#
#
#
#
#


import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC  # 使用 SVM
from sklearn.metrics import accuracy_score, classification_report
from joblib import dump, load
import csv
import time
import paho.mqtt.client as mqtt

# 配置路径
base_path = "."  # 替换为实际文件夹路径
folders = ["class1", "class2", "class3", "class4"]  # 每个类别的文件夹名称


# 数据加载
def load_data(base_path, folders, num_rows_per_sample=100):
    data = []
    labels = []

    for label, folder in enumerate(folders):
        folder_path = os.path.join(base_path, folder)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                try:
                    # 加载 CSV 数据，跳过第一行标题
                    df = pd.read_csv(file_path, skiprows=1)
                    # 将每 num_rows_per_sample 行数据作为一个样本
                    for i in range(0, len(df), num_rows_per_sample):
                        sample_data = df.iloc[i:i + num_rows_per_sample].values.flatten()  # 合并100行数据
                        data.append(sample_data)
                        labels.append(label)  # 为这100行数据添加标签
                except Exception as e:
                    print(f"Failed to load {file_path}: {e}")

    return pd.DataFrame(data), pd.Series(labels)


# 加载数据
data, labels = load_data(base_path, folders)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

# 训练分类器 (使用 SVM)
classifier = SVC(kernel='linear', random_state=42)
classifier.fit(X_train, y_train)

# 测试分类器
y_pred = classifier.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# 保存模型
model_path = "angle_classifier.joblib"
dump(classifier, model_path)
print(f"Model saved to {model_path}")


# 使用模型进行预测
def predict_new_data(model_path, new_data_path):
    # 加载模型
    model = load(model_path)
    # 加载新数据，跳过标题行
    new_data = pd.read_csv(new_data_path, skiprows=1).values
    # 将新数据按100行合并为一个样本（与训练时相同）
    num_rows_per_sample = 100
    samples = []
    for i in range(0, len(new_data), num_rows_per_sample):
        sample_data = new_data[i:i + num_rows_per_sample].flatten()
        samples.append(sample_data)

    # 预测
    predictions = model.predict(samples)
    return predictions


# MQTT 配置
MQTT_BROKER = "10.20.40.160"  # 替换为实际的 MQTT 服务器地址
MQTT_PORT = 1883
MQTT_USERNAME = "Angle"  # 替换为实际用户名
MQTT_PASSWORD = "123456"  # 替换为实际密码
MQTT_TOPIC = "sensor/mpu6050/angles"  # 替换为实际主题

# 初始化变量
collected_data = {}  # 存储每个标识符对应的数据
expected_num_count = 0  # 期待的下一个标识符
file_count = 1  # 文件计数


import csv
import time
import paho.mqtt.client as mqtt

# MQTT 配置
MQTT_BROKER = "10.20.40.160"  # 替换为实际的 MQTT 服务器地址
MQTT_PORT = 1883
MQTT_USERNAME = "Angle"  # 替换为实际用户名
MQTT_PASSWORD = "123456"  # 替换为实际密码
MQTT_TOPIC = "sensor/mpu6050/angles"  # 替换为实际主题

# 初始化变量
collected_data = {}  # 存储每个标识符对应的数据
expected_num_count = 0  # 期待的下一个标识符
file_count = 1  # 文件计数
received_identifiers = set()  # 存储已经接收到的标识符


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    global collected_data, expected_num_count, file_count, received_identifiers

    message = msg.payload.decode("utf-8")
    lines = message.split("\n")

    # 获取消息标识符
    try:
        num_count = int(lines[0].strip())  # 假设标识符在第一行
    except ValueError:
        print("Failed to parse the message identifier")
        return

    # 如果标识符不是期望的，则跳过此消息并等待下一个标识符为0的消息
    if num_count != expected_num_count:
        print(f"Waiting for next data batch with identifier {expected_num_count}, received {num_count}")
        # 如果收到的标识符不是预期的，可以判断是否需要重新从 0 开始收集
        if num_count > expected_num_count:
            print(f"Missing data detected. Restarting collection from 0.")
            reset_collection()  # 重置收集状态
        return

    # 开始收集数据
    if num_count == expected_num_count:
        print(f"Started collecting data for batch {expected_num_count}...")
        collected_data[num_count] = lines[1:]  # 存储数据（忽略第一行的标识符）

        # 记录已接收到的标识符
        received_identifiers.add(num_count)

        # 检查是否已收集到完整的一组数据（标识符为 0 到 9）
        if len(received_identifiers) == 10:  # 如果收到标识符 0 到 9 的所有数据
            # 使用时间戳和文件计数生成唯一的文件名
            filename = f"predict  .csv"
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["angleX", "angleY", "angleZ"])  # CSV 文件标题

                # 将缓存的所有数据写入 CSV
                for i in range(10):
                    line = collected_data.get(i)
                    if line:
                        for data in line:
                            angles = parse_angles(data)
                            if angles:
                                writer.writerow(angles)

            print(f"Saved data to {filename}")

            # 示例预测
            new_data_path = filename  # 使用新生成的 CSV 文件路径
            predictions = predict_new_data(model_path, new_data_path)
            print("Predictions for new data:", predictions)

            # 重置收集状态，准备接收下一个数据包
            reset_collection()

            time.sleep(2)  # 等待后再继续收集

        else:
            expected_num_count += 1  # 如果数据还不完整，期望下一个标识符


def reset_collection():
    """重置数据收集状态"""
    global expected_num_count, collected_data, received_identifiers, file_count
    expected_num_count = 0  # 下一组数据的标识符从 0 开始
    collected_data.clear()  # 清空缓存数据
    received_identifiers.clear()  # 清空接收到的标识符
    file_count += 1  # 更新文件计数


def parse_angles(data):
    try:
        parts = data.split("\t")
        angleX = float(parts[0].strip())
        angleY = float(parts[1].strip())
        angleZ = float(parts[2].strip())
        return [angleX, angleY, angleZ]
    except Exception as e:
        print(f"Failed to parse data: {data}, Error: {e}")
        return None




def main():
    # 初始化 MQTT 客户端
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Error connecting to MQTT Broker: {e}")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()

