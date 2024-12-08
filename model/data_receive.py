# import csv
# import time
# import paho.mqtt.client as mqtt
#
# # MQTT 配置
# MQTT_BROKER = "10.20.40.160"  # 替换为实际的 MQTT 服务器地址
# MQTT_PORT = 1883
# MQTT_USERNAME = "Angle"  # 替换为实际用户名
# MQTT_PASSWORD = "123456"  # 替换为实际密码
# MQTT_TOPIC = "sensor/mpu6050/angles"  # 替换为实际主题
#
# # 初始化变量
# file_count = 1  # 文件计数
# group_count = 0  # 当前已接收到的组数
# data_buffer = []  # 用于存储 10 组数据的缓冲区
#
#
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT Broker!")
#         client.subscribe(MQTT_TOPIC)
#     else:
#         print(f"Failed to connect, return code {rc}")
#
#
# def on_message(client, userdata, msg):
#     global group_count, data_buffer, file_count
#
#     message = msg.payload.decode("utf-8").strip()
#     print(f"Received message: {message}")
#
#     # 将接收到的组数据添加到缓冲区
#     try:
#         # 按行拆分接收到的 10 条数据
#         lines = message.split("\n")
#         if len(lines) == 10:  # 确保每组恰好包含 10 条数据
#             data_buffer.extend(lines)
#             group_count += 1
#         else:
#             print("Received incomplete group, skipping.")
#     except Exception as e:
#         print(f"Error processing message: {e}")
#         return
#
#     # 如果缓冲区内已满 10 组数据
#     if group_count == 10:
#         # 保存到 CSV 文件
#         filename = f"{file_count}.csv"
#         with open(filename, mode="w", newline="", encoding="utf-8") as file:
#             writer = csv.writer(file)
#             writer.writerow(["angleX", "angleY", "angleZ"])
#
#             for line in data_buffer:
#                 angles = parse_angles(line)
#                 if angles:
#                     writer.writerow(angles)
#
#         print(f"Saved data to {filename}")
#
#         # 重置缓冲区和计数器
#         data_buffer = []
#         group_count = 0
#         file_count += 1
#
#         # 停止采集 0.5 秒
#         time.sleep(1)
#
#
# def parse_angles(data):
#     """解析单条数据并返回角度值列表"""
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
#
# if __name__ == "__main__":
#     main()
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
            filename = f"{file_count}.csv"
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

            # 重置收集状态，准备接收下一个数据包
            reset_collection()

            time.sleep(0.5)  # 等待后再继续收集

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


