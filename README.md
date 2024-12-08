# wingardium-leviosa

# 实时传感器数据分类与预测系统

## 项目简介

本项目是一个基于支持向量机（SVM）算法的实时传感器数据分类与预测系统。该系统通过 MQTT 协议从物联网传感器实时收集数据，并利用机器学习模型（SVM）对数据进行训练与预测。它可以用于智能家居、工业物联网等场景，实现对实时采集的传感器数据进行分析和预测，帮助用户实时了解设备状态、监测异常并优化决策。

### 主要功能

- **数据预处理与拆分**：从传感器采集的原始数据中提取特征，清洗数据并拆分为训练集和测试集。
- **支持向量机（SVM）分类**：使用 SVM 对传感器数据进行分类，训练出高效的预测模型。
- **实时数据收集与预测**：通过 MQTT 协议实时收集传感器数据，并对实时采集的数据进行预测。
- **自动保存预测结果**：每次新数据到来时，自动记录预测结果，便于后续分析与监控。
- **模型保存与加载**：训练好的 SVM 模型保存为 `.joblib` 文件，便于加载与使用。
- **数据日志与异常检测**：系统支持记录数据处理过程与预测结果，能够对异常数据进行检测并报警。

## 项目架构

/sensor-data-classification ├── train_classifier.py # 训练分类器并保存模型 ├── mqtt_client.py # MQTT 客户端收集数据并进行预测 ├── angle_classifier.joblib # 训练好的分类器模型文件 ├── data # 存储传感器数据的文件夹 ├── logs # 存储预测日志的文件夹 ├── requirements.txt # 依赖库列表 └── README.md # 项目文档

## 功能概述

### 1. 数据加载与预处理

项目支持从 CSV 格式的传感器数据文件加载数据，并进行数据清洗与预处理。数据会被拆分为训练集和测试集，并经过特征提取处理，转化为可以输入机器学习模型的格式。预处理步骤包括：
- 处理缺失数据
- 标准化数据（如需要）
- 特征选择与提取

### 2. 模型训练

在训练阶段，我们使用支持向量机（SVM）算法对传感器数据进行训练。通过对不同类别的数据进行训练，模型能够学习如何根据输入特征预测数据所属的类别。训练后的 SVM 分类器将被保存为 `.joblib` 文件，以便日后使用。

### 3. MQTT 实时数据收集

项目支持通过 MQTT 协议从传感器实时收集数据。每当传感器发布数据，客户端通过订阅相应的 MQTT 主题来获取实时数据，并将数据保存到本地 CSV 文件中。项目支持：
- 连接不同的 MQTT 代理
- 订阅多个 MQTT 主题
- 自动保存实时收集到的数据

### 4. 实时预测

训练好的 SVM 模型可用于实时数据预测。当新的传感器数据到来时，项目会自动使用训练好的模型进行预测，输出数据的类别标签，并将结果保存到日志文件中。

### 5. 数据日志与异常检测

为了便于分析与调试，系统会记录每次预测的结果和处理过程。如果系统检测到异常数据（例如，传感器输入超出正常范围），将自动触发警报并记录异常信息。

## 环境要求

### 必须的库
- Python 3.x（推荐 Python 3.8 及以上）
- 必须的 Python 库：
  - `pandas`：用于数据处理与分析
  - `scikit-learn`：用于机器学习模型的训练与评估
  - `paho-mqtt`：用于 MQTT 数据收集
  - `joblib`：用于保存和加载训练好的机器学习模型
  - `csv`：用于处理 CSV 格式的文件
  - `time`：用于时间操作
  - `logging`：用于记录预测日志和异常检测

通过以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### MQTT 代理

- 你可以使用公共的 MQTT 代理（如 `broker.hivemq.com`），也可以配置自己的 MQTT 代理服务器。
- MQTT 代理应该支持标准的 MQTT 协议（如 MQTT 3.1.1）。

## 安装与使用

### 1. 数据准备

在运行项目之前，首先需要准备传感器数据。假设你已经通过物联网设备（如加速度计、温度传感器等）收集了数据，并将数据保存在 `data/` 文件夹中。每个传感器的数据应为一个 CSV 文件，每行包含多维特征数据和对应的类别标签。

### 2. 训练分类器

要训练一个新的分类器，运行以下命令：python train_classifier.py

`mqtt_client.py` 脚本会连接到配置好的 MQTT 代理，订阅指定的主题，实时接收传感器数据。每当接收到新数据时，系统会根据训练好的模型进行预测，并输出预测结果。

### 4. 配置 MQTT

在 `mqtt_client.py` 中，你需要配置以下 MQTT 相关参数：

- `MQTT_BROKER`：你的 MQTT 代理地址，例如 `mqtt://broker.hivemq.com` 或本地代理地址。
- `MQTT_PORT`：MQTT 代理的端口（通常为 `1883`）。
- `MQTT_USERNAME` 和 `MQTT_PASSWORD`：如果需要身份验证，可以配置用户名和密码。
- `MQTT_TOPIC`：订阅的 MQTT 主题，例如 `sensor/mpu6050/angles`。

### 5. 模型加载与预测

如果你已经有一个训练好的模型，或者想要加载已经保存的模型进行预测，可以使用以下代码：

​	

```
from joblib import load

# 加载保存的模型
model = load('angle_classifier.joblib')

# 假设你有新收集到的数据
new_data = [0.2, 0.3, 0.5, 0.1]  # 示例数据

# 进行预测
prediction = model.predict([new_data])
print("预测结果:", prediction)
```

## 数据格式

每个传感器数据样本被组织为一行，包含多个特征。例如，假设我们正在收集一个三轴加速度计的数据，每个数据样本可能包含以下字段：

- `acc_x`：加速度计 X 轴的加速度值
- `acc_y`：加速度计 Y 轴的加速度值
- `acc_z`：加速度计 Z 轴的加速度值
- `label`：数据所属的类别标签（如 `walking`、`running`、`standing` 等）

CSV 文件示例：

```
csv复制代码acc_x,acc_y,acc_z,label
0.12,0.34,0.56,walking
0.15,0.36,0.59,running
0.18,0.37,0.60,standing
```

## 预测流程

1. **数据采集**：通过 MQTT 协议实时从传感器获取数据。
2. **数据保存**：将收集到的传感器数据保存为 CSV 文件。
3. **数据预测**：将保存的 CSV 文件数据输入到训练好的 SVM 模型中，进行分类预测。
4. **输出结果**：将预测的类别标签输出到控制台或保存到日志文件。

## 日志与异常检测

项目内置了简单的异常检测和日志记录功能：

- **日志记录**：每次预测结果和数据处理过程都会被记录到 `logs/` 文件夹中的日志文件中。
- **异常检测**：当传感器数据超出预设的正常范围时，系统会触发警报并记录异常信息。

## 许可证

本项目采用 MIT 许可证。详细信息请参见 LICENSE 文件。

## 鸣谢

- **Scikit-learn**：提供了高效的机器学习算法，包括 SVM 模型。
- **Paho MQTT
