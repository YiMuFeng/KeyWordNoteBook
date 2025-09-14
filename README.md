## 🗂️ 快速导航  
- [项目结构](#一项目结构)
- [总体说明](#二总体说明)
- [安全设计](#三安全设计)
- [依赖清单](#四依赖清单)
- [版本历史](#五版本历史)  
- [版权声明](#六版权声明)

## 一、项目结构
    password-manager/
    ├── main.py             # 启动入口
    ├── Core.py             # 核心逻辑（加密、存储）
    ├── UI.py               # 用户界面（PyQt5）
    ├── my_key.json         # 记录文件
    └── README.md           # 自述文件

## 二、总体说明
各类网站和产品的账号和密码又多，每个网站对于密码的要求又不同，
时间长了会记不住这些密码和账号。
好记性不如烂笔头，安全的将自己的账号和密码记录到文件中是有必要的
这就要求能够对密码进行加密，防止泄露。

本项目使用JSON格式保存网站、账号和密码等信息，并基于密码学方法，
对密码字段进行加密，防止文件泄露造成损失

基本功能：
使用JSON保存网站、用户名、密码、密码等级提示，关联账户，备注说明等字段，
按照长度、是否区分或强制大小写字母，是否支持或强制特殊符号生成密码等级提示
对常用密码进行分级、加密保存， 并提供了便于操作的用户界面

JSON文件中的标准化词条如下

     load_dict = {
        "ARGON2_PARAMS":Argon2Params            # 加密参数
        "ItemList":ItemDict                     # 存储条目
        "FrequentlyKeys":FrequentlyKeyDict      # 常用条目
        }
    其中：
    ARGON2_PARAMS = {                           
        "verify_hash": argon2id_str,            # 验证哈希数
        "hash_len": int,                        # 哈希结果长度
        "encryption_salt": base64_str,          # AES加密盐
        "hmac_salt": base64_str,                # HMAC盐
        "hmac_key_encrypted":str,               # 加密存储HMAC密钥
        "integrity_check": str                  # HMAC完整性校验值
        }
    ItemDict = {
        "1":KeyItem,                            # 第一条用户数据
        "2":KeyItem,                            # ...
        ...
        }
    FrequentlyKeysDict = {
        "1":FrequentlyKey,                      # 第一条常用数据
        "2":FrequentlyKey,                      # ...
        ...
        }
    条目：
    KeyItem = {
        "Index": str,                           # 条目序号，唯一ID
        "PasswordLevel": int                    # 密码等级
        "URL": str,                             # 使用的网址
        "UserName": str,                        # 用户名
        "Password": str,                        # 密码，在文件中使用密文储存
        "LinkURL": str,                         # 关联账户
        "Note": str                             # 备注
        }   
    常用条目：
    FrequentlyKey = {
        "Password": str,                        # 密码，在文件中使用密文储存
        "PasswordLevel": int,                   # 密码等级
        "Note": str                             # 备注
        }

## 三、安全设计
### Core:
密码等敏感信息采用AES算法进行加密保存，AES密钥本身长度较大，而且常采用随机数，不便记忆。
因此采用二级派生的算法，利用用户自主设定的主密钥派生获得安全的AES密钥
为了防止密码本文件本身被篡改或损坏，利用HMAC算法对文件进行签名和完整性校验。
因此主要的密钥派生关系和用法如下：

    主密钥--argon2->验证哈希
    主密钥+AES盐--argon2->AES密钥
    主密钥+HMAC盐--argon2->HMAC密钥
    HMAC密钥--AES->加密存储，降低HMAC派生开销
    文件--HMAC->校验值，对比文件是否被篡改
    词条--AES->加密存储词条
API的安全性设计：

    API主要提供了登录密码验证、增加、删除、修改、查看非密信息、查看加密数据
    除获取非密信息外的API函数，均需要进行二次密码验证
### UI:
    UI仅负责与用户交互和提供图形化显示，本身不保存任何信息，全部由Core的API函数进行处理
    UI在获取用户输入的明文密码后，仅在API函数调用中传递，在内存中短暂暴露。
    UI获取Core返回的解密数据后，任何操作都会重新覆盖显示信息
### main:

## 四、依赖清单
    requirements:
        Python : 3.12.7
        conda : 24.11.3
        cryptography : 43.0.0
        argon2-cffi : 23.1.0
        PyQt5 : 5.15.10

## 五、版本历史
    8.30：初始化工程
    8.31：添加UI。合并开源声明文件、版权声明文件分支
    9.7：更新UI风格和登录界面
    9.14：完善UI功能和风格优化

## 六、版权声明
    Copyright (c) 2025 Y.MF. All rights reserved.
    本代码及相关文档受著作权法保护，未经授权，禁止任何形式的复制、分发、修改或商业使用。
    如需使用或修改本代码，请联系版权所有者获得书面许可（联系方式：1428483061@qq.com）。
    
    免责声明：本代码按"原样"提供，不提供任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性的担保。
    在任何情况下，版权所有者不对因使用本代码或本代码的衍生作品而导致的任何直接或间接损失承担责任。
    
    项目名称：密码本
    项目仓库：https://github.com/YiMuFeng/KeyWordNoteBook.git
    创建时间：2025/8/16
    版权所有者：Y.MF
    联系方式：1428483061@qq.com
    许可协议：Apache License 2.0
