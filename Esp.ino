// #include <MPU6050_tockn.h>
// #include <Wire.h>
// #include <WiFi.h>
// #include <string.h>

// MPU6050 mpu6050(Wire);
// const char* ssid = "OnePlus";
// const char* password = "11111111";
// const char* mqtt_server = "192.168.201.156"; // 或者使用其他MQTT Broker
// const int mqtt_port = 1883; // 对于TLS/SSL加密连接，请使用8883端口
// const char* mqtt_user = "MQTT1"; // 如果需要
// const char* mqtt_password = "123456"; // 如果需要
// String message ;
// const char* mqtt_topic = "test/topic";
// WiFiClient client;
// PubSubClient client(client);

// void callback(char* topic, byte* payload, unsigned int length) {
//   Serial.print("Message arrived [");
//   Serial.print(topic);
//   Serial.print("] ");
//   for (int i = 0; i < length; i++) {
//     Serial.print((char)payload[i]);
//   }
//   Serial.println();
// }

// void setup() {
//   Serial.begin(115200);
//   WiFi.begin(ssid, password);

//   // Wait for connection
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("");
//   Serial.println("WiFi connected");
//   Serial.println("IP address: ");
//   Serial.println(WiFi.localIP());

//   Wire.begin();
//   mpu6050.begin();
//   mpu6050.calcGyroOffsets(true);
//   client.setServer(mqtt_server, mqtt_port);
//   client.setCallback(callback); // 定义回调函数处理接收到的消息
//    if (client.connect("ESP32Client")) { // 尝试连接到MQTT Broker
//     Serial.println("Connected to MQTT broker");
//     client.publish("test/topic", "Hello from ESP32!"); // 发布消息
//     client.subscribe("test/topic"); // 订阅同一主题，以便接收回复
//   } else {
//     Serial.print("Failed to connect to MQTT broker, rc=");
//     Serial.println(client.state());
//   }
// }
 
// void loop() {
//   mpu6050.update();
//   float angleX = mpu6050.getAngleX();
//   float angleY = mpu6050.getAngleY();
//   float angleZ = mpu6050.getAngleZ();
//   message = "angleX: ";
//   message += String(angleX);
//   message += "\tangleY: ";
//   message += String(angleY);
//   message += "\tangleZ: ";
//   message += String(angleZ);
//   Serial.print("angleX : ");
//   Serial.print(angleX);
//   Serial.print("\tangleY : ");
//   Serial.print(angleY);
//   Serial.print("\tangleZ : ");
//   Serial.println(angleZ);
//   if (!client.connected()) {
//     reconnect(); // 如果断开，则尝试重新连接
//   }
//   client.publish(mqtt_topic, message.c_str()); 

//   delay(100);
// }
#include <MPU6050_tockn.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>

// MPU6050对象
MPU6050 mpu6050(Wire);

// Wi-Fi配置
const char* ssid = "OnePlus";
const char* password = "11111111";

// MQTT Broker配置
const char* mqtt_server = "192.168.201.156"; // 或者使用其他MQTT Broker
const int mqtt_port = 1883; // 对于TLS/SSL加密连接，请使用8883端口
const char* mqtt_user = "MQTT1"; // 如果需要
const char* mqtt_password = "123456"; // 如果需要

// MQTT主题
const char* mqtt_topic = "sensor/mpu6050/angles";

// MQTT客户端实例
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // 初始化Wi-Fi连接
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // 初始化I2C总线和MPU6050
  Wire.begin();
  mpu6050.calcGyroOffsets(true); // 校准陀螺仪偏移量
  
  // 设置MQTT客户端
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback); // 定义回调函数处理接收到的消息
  
  // 尝试连接到MQTT Broker
  reconnect();
}

void loop() {
  // 确保与MQTT服务器保持连接
  if (!client.connected()) {
    reconnect(); // 如果断开，则尝试重新连接
  }
  client.loop(); // 处理MQTT网络流量和回调

  // 更新MPU6050读数
  mpu6050.update();

  // 获取角度值
  float angleX = mpu6050.getAngleX();
  float angleY = mpu6050.getAngleY();
  float angleZ = mpu6050.getAngleZ();

  // 构建消息字符串
  String message = "angleX: ";
  message += String(angleX);
  message += "\tangleY: ";
  message += String(angleY);
  message += "\tangleZ: ";
  message += String(angleZ);

  // 打印到串行监视器
  Serial.print("angleX : ");
  Serial.print(angleX);
  Serial.print("\tangleY : ");
  Serial.print(angleY);
  Serial.print("\tangleZ : ");
  Serial.println(angleZ);

  // 发布消息到MQTT主题
  client.publish(mqtt_topic, message.c_str());

  delay(50); // 每秒发送一次更新 [ty-reference](7)
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) { // 尝试连接到MQTT Broker
      Serial.println("Connected to MQTT broker");
      client.subscribe(mqtt_topic); // 订阅同一主题，以便接收回复
    } else {
      Serial.print("Failed to connect, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// 回调函数定义
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}