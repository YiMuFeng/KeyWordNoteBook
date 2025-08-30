## 🗂️ 快速导航  
- [项目结构](#一项目结构)
- [总体说明](#二总体说明)
- [安全设计](#三安全设计)
- [依赖清单](#四依赖清单)
- [版本历史](#五版本历史)  

## 一、项目结构
    password-manager/
    ├── main.py             # 启动入口
    ├── Core.py             # 核心逻辑（加密、存储）
    ├── UI.py               # 用户界面（PyQt5）
    ├── my_key.json         # 记录文件
    └── README.md           # 自述文件

## 二、总体说明

基于JSON和AES算法构建密码本
基本功能：
使用JSON保存网站、用户名、密码、密码等级提示，关联账户，备注说明等字段，密码字段采用加密方式
对常用密码进行分级、加密保存，按照长度、是否区分或强制大小写字母，是否支持或强制特殊符号

主要算法和逻辑：
初始化密码本管理器，加载文件：若文件不存在，或不符合JSON格式，重新创建一个新的密码本
登录和文件校验：读取文件，加载"ARGON2_PARAMS"词条中加密相关字节，验证字节完整性
利用输入的登录密码（主密钥）和"verify_hash"记录，基于argon2算法，验证登录。
读取"encryption_salt"获取AES密钥盐，用argon2算法和AES盐派生AES密钥。
使用AES密钥解析"hmac_key_encrypted"获得HMAC密钥；
使用HMAC密钥计算文件HMAC值，进行完整性校验，登录完成。

新文件创建：
用主密钥生成登录用验证哈希
生成AES盐，HMAC盐，派生AES密钥和HMAC密钥
使用AES加密HMAC密钥
将验证哈希和盐写入文件，计算文件HMAC，保存到文件
    

json结构如下

    load_dict = {
        "ARGON2_PARAMS":Argon2Params   # 加密参数
        "ItemList":ItemDict             # 存储条目
        "FrequentlyKeys":FrequentlyKeyDict       # 常用条目
        "hmac_salt": lambda x: isinstance(x, str) and is_base64(x),                 # HMAC盐
        "hmac_key_encrypted":lambda x:isinstance(x,str),                            # 加密存储HMAC密钥
        "integrity_check": lambda x: isinstance(x, str) and len(x) == 64
        }
其中：

    ARGON2_PARAMS = {
        "verify_hash": lambda x:isinstance(x,str) and x.startswith("$argon2id$"),   # 验证哈希数
        "hash_len": lambda x:isinstance(x,int) and x >= 32,                         # 哈希结果长度
        "encryption_salt": lambda x:isinstance(x,str) and is_base64(x),             # AES加密盐
        "hmac_salt": lambda x: isinstance(x, str) and is_base64(x),                 # HMAC盐
        "hmac_key_encrypted":lambda x:isinstance(x,str),                            # 加密存储HMAC密钥
        "integrity_check": lambda x: isinstance(x, str) and len(x) == 64            # HMAC完整性校验值
        }

    ItemDict = {
        "1":KeyItem,                    # 第一条用户数据
        "2":KeyItem,                    # ...
        ...
        }

    KeyItem = {
        "Index": str,                   # 条目序号，唯一ID
        "PasswordLevel": int            # 密码等级
        "URL": str,                     # 使用的网址
        "UserName": str,                # 用户名
        "Password": str,                # 密码，在文件中使用密文储存
        "LinkURL": str,                 # 关联账户
        "Note": str                     # 备注
        }   

    FrequentlyKeysDict = {
        "1":FrequentlyKey,                  # 第一条常用数据
        "2":FrequentlyKey,                  # ...
        ...
        } 

    FrequentlyKey = {
        "Password": str,                # 密码，在文件中使用密文储存
        "PasswordLevel": int,           # 密码等级
        "Note": str                     # 备注
        }

## 三、安全设计
### Core:
    主密钥--argon2->验证哈希
    主密钥+AES盐--argon2->AES密钥
    主密钥+HMAC盐--argon2->HMAC密钥
    HMAC密钥--AES->加密存储，降低HMAC派生开销
    文件--HMAC->校验值，对比文件是否被篡改
    词条--AES->加密存储词条
### UI:
    

## 四、依赖清单
requirements:

    Python : 3.12.7
    conda : 24.11.3
    cryptography : 43.0.0
    argon2-cffi : 23.1.0
    PyQt5 : 5.15.10

## 五、版本历史
版本历史：