# wingardium-leviosa

## 魔法与科技的结合：魔法棒！

**背景故事：** 在一个遥远的未来，魔法与科技和谐共存。巫师们不再只是挥舞着魔杖念咒语，他们开始使用智能设备来增强自己的魔法。你，作为一个现代巫师，决定打造一把能够识别特定动作并执行神奇操作的智能法杖。

**项目愿景：** 你梦想中的法杖不仅仅是一个简单的魔法工具，它能够理解你的每一个动作，并且通过这些动作来控制你的魔法世界。比如，轻轻一挥，门就自动打开了，再挥一下，灯光随之变化。

**魔法组件：**

- **ESP32魔杖核心**：这是你的魔杖的大脑，它能够感知周围的魔法波动（传感器数据），并且通过神秘的无线信号（MQTT协议）与你的魔法主机沟通。
- **动作识别水晶球**：在你的魔法主机里，有一个强大的水晶球（深度学习模型），它能够识别你的魔杖做出的各种复杂手势。
- **自动门咒**：一旦你的法杖被正确挥动，这个咒语就会被触发，门就会自动打开，仿佛有看不见的手在操作。

**魔法施展过程：**

1. **收集魔法能量**：你的ESP32魔杖核心开始收集周围的魔法能量（陀螺仪信息）。
2. **传输魔法信号**：收集到的能量通过无线信号发送到你的魔法主机。
3. **水晶球的预言**：魔法主机中的水晶球开始工作，识别出你的手势。
4. **施展咒语**：一旦水晶球识别出特定的手势，它就会施展相应的咒语（开门等操作）。

**魔法世界的扩展：** 这个项目最棒的地方在于它的扩展性。你可以不断学习新的手势，训练你的水晶球识别它们，并且创造更多的咒语来扩展你的魔法世界。无论是控制家里的灯光，还是播放音乐，只要你的想象力足够丰富，你的法杖就能实现。

**社区的魔法合作：** 而且，你不是孤单的巫师。全球的巫师们都在分享他们的魔法代码和设计，你可以从他们的创意中获得灵感，也可以分享你的魔法创造，让整个魔法社区变得更加强大。

这个项目不仅仅是技术的展示，它是对魔法世界的一次新的探索，让每个人都能成为创造者，用科技的力量扩展魔法的边界。拿起你的智能法杖，让我们一起开启这段奇妙的魔法旅程吧！🧙‍♂️🚀✨


# 项目说明
这个项目由两个3个大板块组成硬件部分，mqtt部分，模型部分，下面将分别进行详细说明

## 硬件部分
### 1.MPU6050
这是一个六轴陀螺仪，详细的参数可参考**GY521mpu-6050资料**文件夹，这里为了快速开发参考了博客https://blog.csdn.net/weixin_42854045/article/details/127310247 ，参考博客代码可以很快了解如何获取其中三个我们需要使用的参数，如果想使用其他三个参数，可以参考**GY521mpu-6050资料**，通信是使用i2c通信协议，我这里使用的ESP32开发板默认的GPIO是21和22，连接方式为GPIO21 连接SDA。GPIO22连接SCL，保证AD0引脚悬空。vcc连接3.3v，gnd连接gnd即可
### 2.ESP核心代码
接下来ESP32上的核心代码，这里ESP主要要做三件事，1读取按钮状态，2获取陀螺仪消息，3mqtt转发消息，1，3的教程很好找，这里不赘述，2上面已经提及过，也不再说。接下来简单说说代码逻辑，当读取到按钮按下时开始采集陀螺仪消息，每十个采样点为1组进行转发，一共转发10组，代码里设计了一点冗余保证稳定性，并在每一组前加上一个标识符（0，1，2，3……）以便接收方知道是哪组数据。
### 3.3D打印模型
该模型基于另一个魔法棒项目（来源：lyg09270 Cyberry_Potter_Electromagic_Wand）的设计。在此基础上，后续可以根据需要进行自定义建模与设计。

## MQTT部分
这里我是使用EMQX配置了一个服务器，用mqttx进行测试具体可参考网上教学。

## 模型部分
这里的代码在model文件夹中
数据采集是在*data_receive.py*文件里，逻辑为当收到mqtt的数据时，判断标识符是否从0开始，接着收集从0到9的数据，如果中间有缺失则重新开始收集，每10组保存为一个csv文件
接下来时模型的训练与推理，在*model.py*文件里，这里使用的是SVM模型，当采集到10组数据时，更新predict.csv文件并进行推理。


# 改进
1硬件部分集成度低，3d打印外壳需要重新设计，电源模块也要重新考虑，可能需要绘制简单的pcb板进行美化与集成，如果有这方面的大佬欢迎交流讨论。
2当前模型的准确度较低，可考虑使用更复杂的模型，在*model*文件夹下有两个testmodel可以参考。
3识别出动作后的功能目前只设计了上传华为云控制开门，后面可以开发其他功能
