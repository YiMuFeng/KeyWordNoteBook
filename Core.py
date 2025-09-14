# Copyright (c) 2025 Y.MF. All rights reserved.
#
# 本代码及相关文档受著作权法保护，未经授权，禁止任何形式的复制、分发、修改或商业使用。
# 如需使用或修改本代码，请联系版权所有者获得书面许可（联系方式：1428483061@qq.com）。
#
# 免责声明：本代码按"原样"提供，不提供任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性的担保。
# 在任何情况下，版权所有者不对因使用本代码或本代码的衍生作品而导致的任何直接或间接损失承担责任。
#
# 项目名称：Core.py
# 项目仓库：https://github.com/YiMuFeng/KeyWordNoteBook.git
# 创建时间：2025/8/16 22:57
# 版权所有者：Y.MF
# 联系方式：1428483061@qq.com
# 许可协议：Apache License 2.0

"""
密码管理核心
实现文件管理，词条加密、存储功能
提供增、删、改、查的API函数
"""
__version__ = "0.0.1.2"

from cryptography.fernet import Fernet
import json
import base64
from argon2 import PasswordHasher,exceptions,Type
import re
import secrets
import os
import hmac
import hashlib


def is_base64(s: str) -> bool:
    """验证字符串是否为Base64编码的字符串"""
    try:
        return base64.b64encode(base64.b64decode(s)) == s.encode()
    except:
        return False

class Argon2Params(dict):
    """ARGON2算法参数"""
    keycode = {
        "verify_hash": lambda x:isinstance(x,str) and x.startswith("$argon2id$"),   # 验证哈希数
        "hash_len": lambda x:isinstance(x,int) and x >= 64,                         # 哈希结果长度
        "encryption_salt": lambda x:isinstance(x,str) and is_base64(x),             # AES加密盐
        "hmac_salt": lambda x: isinstance(x, str) and is_base64(x),                 # HMAC盐
        "hmac_key_encrypted":lambda x:isinstance(x,str),                            # 加密存储HMAC密钥
        "integrity_check": lambda x: isinstance(x, str) and len(x) == 64            # HMAC完整性校验值
    }
    def __setitem__(self, key, value):
        if key not in self.keycode:
            raise KeyError(f"不允许的键: {key}")
        if not self.keycode[key](value):
            raise ValueError(f"键 {key} 的值 {value} 不符合要求")
        super().__setitem__(key, value)
    def update(self, *args, **kwargs):
        temp_dict = dict(*args, **kwargs)
        for key, value in temp_dict.items():
            self[key] = value

class KeyItem(dict):
    """用户条目声明"""
    keycode = {
        # 由管理器控制和获取
        "Index": lambda x:isinstance(x,str),            # 条目序号，唯一ID
        "PasswordLevel": lambda x: isinstance(x, int),  # 密码等级
        # 由用户填写
        "URL": lambda x:isinstance(x,str),              # 使用的网址
        "UserName": lambda x:isinstance(x,str),         # 用户名
        "Password": lambda x:isinstance(x,str),         # 密码，在文件中使用密文储存
        "LinkURL": lambda x:isinstance(x,str),          # 关联账户
        "Note": lambda x:isinstance(x,str)              # 备注
    }
    def __setitem__(self, key, value):
        if key not in self.keycode:
            raise KeyError(f"不允许的键: {key}")
        if not self.keycode[key](value):
            raise ValueError(f"键 {key} 的值 {value} 不符合要求")
        super().__setitem__(key, value)
    def update(self, *args, **kwargs):
        temp_dict = dict(*args, **kwargs)
        for key, value in temp_dict.items():
            self[key] = value

class FrequentlyKey(dict):
    """常用密码条目"""
    keycode = {
        "Password": lambda x:isinstance(x,str),         # 密码，在文件中使用密文储存
        "PasswordLevel": lambda x: isinstance(x, int),  # 密码等级
        "Note": lambda x: isinstance(x, str)  # 备注
    }
    def __setitem__(self, key, value):
        if key not in self.keycode:
            raise KeyError(f"不允许的键: {key}")
        if not self.keycode[key](value):
            raise ValueError(f"键 {key} 的值 {value} 不符合要求")
        super().__setitem__(key, value)
    def update(self, *args, **kwargs):
        temp_dict = dict(*args, **kwargs)
        for key, value in temp_dict.items():
            self[key] = value

class KeyWordNoteBook:
    """密码本管理器"""
    def __init__(self, mainKey:str,path:str=r"my_key.json"):
        """
        :param mainKey: 管理员主密钥
        :param path: 密码本文件路径
        """
        self.Path = path
        self.MainKey = mainKey
        self.load_dict: dict = {}       # 主字典
        self.verify_hash = None         # 主密码校验哈希
        self.encryption_salt = None     # 加密专用盐
        self.hmac_key = None            # HMAC密钥

        self.ph = PasswordHasher(       # argon2加密器初始化
            type=Type.ID,
            memory_cost=131072,
            time_cost=6,
            parallelism=6,
            hash_len =64)   # TODO：hash_len从文件中动态加载设置

        self._init_or_load_file()

    # API函数
    def verify_main_key(self,upw:str)->bool:
        """
        验证用户权限
        :param upw: 二级密码
        """
        try:
            self.ph.verify(self.verify_hash, upw)
            print("主密码验证成功")
            return True
        except exceptions.VerifyMismatchError:
            print("密码验证失败")
            return False

    def add_item(self, data: KeyItem,upw:str) -> str:
        """
        向文件中新增条目，主键自增
        :param data:要添加的条目
        :param upw: 二级密码
        :return:新增条目的key
        """
        # 验证用户权限
        try:
            self.ph.verify(self.verify_hash, upw)
            print("主密码验证成功,添加条目")
        except exceptions.VerifyMismatchError:
            print("二级密码验证失败，不能添加条目")
            return "-1"

        # 编辑条目
        data["Index"] = self._get_index()
        data["PasswordLevel"] = self.get_password_level(data["Password"])
        data["Password"] = self._encode_aes(data["Password"])  # AES加密主数据

        # 写入条目
        self.load_dict["ItemList"].update({data["Index"]: data})
        self._sync_to_file()
        print("已写入条目", data["Index"])
        return data["Index"]

    def delete_item(self,No:str,upw:str)->bool:
        """
        从文件中删除指定条目标记为No的条目
        :param upw: 二级密码
        :param No: 要删除的条目的Index
        :return: 是否删除成功
        """
        try:
            self.ph.verify(self.verify_hash, upw)
            print("主密码验证成功,删除条目")
        except exceptions.VerifyMismatchError:
            print("二级密码验证失败，不能删除条目")
            return False

        if No in self.load_dict["ItemList"]:
            # 从内存字典中删除条目
            del self.load_dict["ItemList"][No]

            # 同步到文件
            self._sync_to_file()
            print(f"已删除条目 {No}")
            return True
        else:
            print(f"条目 {No} 不存在，删除失败")
            return False

    def update_item(self, No: str, data: KeyItem,upw:str):
        """
        修改条目
        :param upw: 二级密码
        :param No: 要修改的条目编号
        :param data:新结构体
        :return:成功返回新条目索引，失败返回False
        """
        # 验证用户权限
        try:
            self.ph.verify(self.verify_hash, upw)
            print("主密码验证成功,修改条目")
        except exceptions.VerifyMismatchError:
            print("二级密码验证失败，不能修改条目")
            return False

        if No in self.load_dict["ItemList"]:
            # 修改条目
            item = self.load_dict["ItemList"][No]

            data["Index"] = item["Index"]
            if "Password" in data:
                data["PasswordLevel"] = self.get_password_level(data["Password"])
                data["Password"] = self._encode_aes(data["Password"])  # AES加密主数据
            else:
                # 如果未提供新密码，保留原密码
                data["Password"] = item["Password"]
                data["PasswordLevel"] = item["PasswordLevel"]

            # 写入条目
            self.load_dict["ItemList"].update({data["Index"]: data})
            self._sync_to_file()
            print("已写入条目", data["Index"])
            return data["Index"]
        else:
            print(f"条目 {No} 不存在，修改失败")
            return False

    def get_item_by_id(self,No:str,upw:str)->dict|None:
        """
        获取指定条目的（解密后）
        :param upw: 用户密码，独立验证
        :param No: 指定条目索引
        :return: 解密后的单个条目
        """
        # 1. 验证权限（确保用户已登录）
        try:
            self.ph.verify(self.verify_hash, upw)
            print("主密码验证成功,展示条目")
        except exceptions.VerifyMismatchError:
            print("二级密码验证失败，不能展示条目")
            return None

        # 2. 获取条目数据
        if No in self.load_dict["ItemList"]:
            target_items = self.load_dict.get("ItemList").get(No).copy()#注意返回拷贝
            print(target_items)
            # 解密密码字段
            try:
                target_items["Password"] = self._decode_aes(target_items["Password"])
                return target_items
            except Exception as e:
                print(f"解密条目 {No} 失败: {str(e)}")
                return None
        return None

    def get_non_secret_items(self)->list:
        """
        获取所有条目（非密码字段）
        :return:
        """
        item_list = self.load_dict.get("ItemList", {})
        non_secret_items = []  # 存储过滤后的非敏感条目

        # 定义允许向前端返回的非敏感字段（明确白名单，拒绝一切未声明字段）
        allowed_fields = {
            "Index",            # 条目唯一ID
            "LinkURL",          # 关联账户
            "Note",             # 备注
            "PasswordLevel",    # 密码等级
            "URL",              # 网址
            "UserName"          # 用户名
        }
        # 过滤敏感字段：仅保留allowed_fields中的字段
        for item_id, item_data in item_list.items():
            filtered_item = {
                field: item_data.get(field, "")
                for field in allowed_fields
                if field in item_data
            }

            non_secret_items.append(filtered_item)

        return non_secret_items

    def get_frequently_key(self,level:int):
        """
        获取常用密码
        :param level:常用密码的等级
        :return:
        """
        return self.load_dict["FrequentlyKeys"]

    # 私有（保护）函数
    def _init_or_load_file(self):
        """
        文件加载，验证，或初始化
        :return:
        """
        # 检查文件是否存在
        if not os.path.exists(self.Path):
            self._initialize_new_book()
            return

        with open(self.Path, 'r', encoding='utf-8') as self.file:
            try:
                self.file.seek(0)
                self.load_dict = json.load(self.file)  # json文件->dict
            except json.JSONDecodeError:
                print("JSON文件格式错误，使用空文件，重新初始化密码")
                self._initialize_new_book()
                return

        params = self.load_dict.get("ARGON2_PARAMS", {})

        # 验证核心参数完整性（必须包含所有关键字段）
        required_params = [ "verify_hash", "hash_len","encryption_salt",
                            "hmac_salt", "hmac_key_encrypted", "integrity_check"]
        missing = [p for p in required_params if p not in params]
        if missing:
            raise UnicodeError(f"文件参数不完整，缺少：{', '.join(missing)}")

        # 验证登录
        self.verify_hash = params["verify_hash"]
        try:
            self.ph.verify(self.verify_hash, self.MainKey)
            print("主密码验证成功")
        except exceptions.VerifyMismatchError:
            raise ValueError ("输入的登录密码不正确")
        except exceptions.VerificationError:
            raise UnicodeError("哈希字符串格式错误")
        except Exception as e:
            raise RuntimeError(f"登录时发生未知错误 - {str(e)}")

        # 解析AES盐
        self.encryption_salt = params["encryption_salt"]                # b64 str
        self.encryption_salt = base64.b64decode(self.encryption_salt)   # bytes
        # 解析HMAC盐 TODO:实际上hmac盐在加载时不需要使用，这里仅保证其完整性 为hmac_key解码失败时提供降级处理
        self.hmac_salt = params["hmac_salt"]                            # b64 str
        self.hmac_salt = base64.b64decode(self.hmac_salt)               # bytes

        # 解析HMAC密钥
        encrypted_hmac_key = params["hmac_key_encrypted"]       # 读取文件中的hmac密钥 加密后的b64str
        hmac_key_str = self._decode_aes(encrypted_hmac_key)     # 解密的base64 str
        self.hmac_key = base64.b64decode(hmac_key_str)          # 解密hmac密钥 bytes

        # 文件完整性验证
        computed_hmac = self._compute_file_hmac(self.load_dict)    # 计算文件的hmac
        if computed_hmac != params["integrity_check"]:
            raise ValueError("文件HMAC校验失败，内容可能被篡改或损坏")

        print("文件加载完成，验证通过")

    def _initialize_new_book(self):
        """
        新建文件，初始化新密码
        用于文件不存在，或json文件格式错误时
        :return:
        """
        # 1. 生成验证用哈希
        self.verify_hash = self.ph.hash(self.MainKey)
        # 2. 生成16字节AES盐
        self.encryption_salt = secrets.token_bytes(16)  # bytes
        encrypted_salt_b64 = base64.b64encode(self.encryption_salt).decode('utf-8')  # Base64 str
        # 3. 生成HMAC盐
        self.hmac_salt = secrets.token_bytes(32)    # bytes
        hmac_salt_b64 = base64.b64encode(self.hmac_salt).decode('utf-8')    # Base64 str
        # 4. 派生HMAC密钥
        self.hmac_key = self._derive_hmac_key()  # bytes
        hmac_key_str = base64.b64encode(self.hmac_key).decode('utf-8')  # Base64 str
        # 用AES加密HMAC密钥后存储
        encrypted_hmac_key = self._encode_aes(hmac_key_str)  # 加密后的Base64 str

        # 初始化数据结构
        self.load_dict: dict = {}
        m_Argon2Params = Argon2Params()  # 加密参数
        m_Argon2Params["verify_hash"] = self.verify_hash
        m_Argon2Params["hash_len"] = 64
        m_Argon2Params["encryption_salt"] = encrypted_salt_b64
        m_Argon2Params["hmac_salt"] = hmac_salt_b64
        m_Argon2Params["hmac_key_encrypted"] = encrypted_hmac_key
        m_Argon2Params["integrity_check"] = "1234567890123456789012345678901234567890123456789012345678901234"

        m_ItemDict: dict[str:KeyItem] = {}  # 用户条目
        m_FrequentlyKeyDict: dict[str:FrequentlyKey] = {}  # 常用条目

        # 保存 同步文件
        self.load_dict.update({
            "ARGON2_PARAMS": m_Argon2Params,
            "ItemList": m_ItemDict,
            "FrequentlyKeys": m_FrequentlyKeyDict
            })
        self._sync_to_file()
        print("新密码本初始化完成")

    def _compute_file_hmac(self, data: dict) -> str:
        """
        使用HMAC密钥计算文件HMAC
        :param data: 要计算的文件dict
        :return:hmac值
        """
        import copy
        # 排除校验值本身
        data_to_check = copy.deepcopy(data)
        data_to_check["ARGON2_PARAMS"].pop("integrity_check", None)
        # 序列化HMAC计算器
        data_str = json.dumps(data_to_check,
                              sort_keys=True,
                              ensure_ascii=False,
                              indent=4,  # 增加缩进
                              separators=(',', ': ')
                              ).encode()

        # 计算HMAC（使用常驻内存的密钥）
        return hmac.new(
            self.hmac_key,
            msg=data_str,
            digestmod=hashlib.sha256
        ).hexdigest()

    def _sync_to_file(self):
        """将内存中的数据同步到文件，统一管理写入操作"""
        with open(self.Path, 'w', encoding='utf-8') as f:
            computed_hmac = self._compute_file_hmac(self.load_dict)
            self.load_dict["ARGON2_PARAMS"]["integrity_check"] = computed_hmac
            json.dump(self.load_dict,
                      f,
                      sort_keys=True,
                      ensure_ascii=False,
                      indent=4,
                      separators=(',', ': '))

    def _derive_hmac_key(self)->bytes:
        """使用hmac_salt派生HMAC密钥"""
        if not self.hmac_salt:
            raise RuntimeError("HMAC盐值未初始化")
        try:
            # 用主密码+hmac盐值生成哈希，提取前16字节作为hmac密钥
            hash_result = self.ph.hash(self.MainKey, salt=self.hmac_salt)

            parts = hash_result.split("$")
            if len(parts) < 6:
                raise ValueError(f"无效的Argon2哈希格式: {hash_result}")
            # 提取哈希部分并使用Argon2专用Base64解码器解码
            hash_part = parts[-1]
            hash_bytes = self.argon2_base64_decode(hash_part)
            # 截取16字节（128位）作为HMAC密钥
            hmac_key = hash_bytes[:16]
            if len(hmac_key) < 16:
                raise ValueError(f"哈希结果长度不足，无法生成16字节HMAC密钥（实际长度: {len(hash_bytes)}）")
            return hmac_key
        except Exception as e:
            raise RuntimeError(f"派生HMAC密钥失败: {str(e)}")

    def _encode_aes(self, plaintext: str) -> str:
        """
        使用AES加密明文
        :param plaintext: 要加密的明文（b64 str ）
        :return: 加密后的字符串（Base64编码，包含IV）
        """
        try:
            fernet = self._get_fernet()
            encrypted_token = fernet.encrypt(plaintext.encode('utf-8'))
            return encrypted_token.decode('utf-8')  # 转为字符串存储
        except Exception as e:
            raise RuntimeError(f"AES加密失败: {str(e)}")

    def _decode_aes(self, ciphertext: str) -> str:
        """
        使用cryptography的Fernet解密
        :param ciphertext: 加密后的令牌字符串
        :return: 解密后的明文
        """
        try:
            fernet = self._get_fernet()
            decrypted_bytes = fernet.decrypt(ciphertext.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"AES解密失败（可能被篡改或密钥错误）: {str(e)}")

    def _get_fernet(self) -> Fernet:
        """
        生成Fernet加密器（封装了AES-GCM）
        """
        # 派生32字节AES密钥
        aes_key = self._derive_aes_key()  # 32字节密钥（AES-256）
        # 将原始密钥转换为Fernet要求的URL安全Base64格式
        fernet_key = base64.urlsafe_b64encode(aes_key)
        # 确保密钥长度正确，32字节原始密钥经Base64编码后应为44字节
        if len(fernet_key) != 44:
            raise ValueError(f"无效的Fernet密钥长度: {len(fernet_key)}")
        # 返回Fernet加密器（内部使用AES-GCM模式，自带认证）
        return Fernet(fernet_key)

    def _derive_aes_key(self) -> bytes:
        """
        使用加密专用盐值派生AES密钥,应该随用随调，使用后立刻清理
        """
        if not self.encryption_salt:
            raise RuntimeError("加密盐值未初始化")
        # 用主密码+加密盐值生成哈希，提取前32字节作为AES-256密钥
        try:
            hash_result = self.ph.hash(self.MainKey, salt=self.encryption_salt)
            parts = hash_result.split("$")
            if len(parts) < 6:
                raise ValueError(f"无效的Argon2哈希格式: {hash_result}")
            # 提取哈希部分并使用Argon2专用Base64解码器解码
            hash_part = parts[-1]
            hash_bytes = self.argon2_base64_decode(hash_part)
            # 截取前32字节作为AES-256密钥
            aes_key = hash_bytes[:32]
            if len(aes_key) < 32:
                raise ValueError(f"哈希结果长度不足，无法生成32字节AES密钥")
            return aes_key
        except Exception as e:
            raise RuntimeError(f"派生AES密钥失败: {str(e)}")

    def _get_index(self)->str:
        """
        获取一个新的条目index
        :return:
        """
        ItemList = self.load_dict.get("ItemList",{})
        if not ItemList:
            return "1"
        # 取现有最大索引值并加1，确保唯一性
        max_index = max(int(key) for key in ItemList)
        return str(max_index + 1)

    @staticmethod
    def get_password_level(key: str) -> int:
        """
        估计密码强度（0-5级，数字越大越安全）
        :param key: 待评估的密码字符串
        :return: 强度等级（0-5）
        """
        if not isinstance(key, str) or len(key) == 0:
            return 0
        score = 0  # 评分
        length = len(key)
        # 1. 密码长度评估（占比30%）
        if length >= 16:
            score += 3  # 超长密码（优秀）
        elif length >= 12:
            score += 2  # 长密码（良好）
        elif length >= 8:
            score += 1  # 标准长度（及格）
        # 小于8位不加分

        # 2. 字符类型多样性（占比40%）
        # 检查是否包含小写字母、大写字母、数字、特殊符号
        has_lower = re.search(r'[a-z]', key) is not None
        has_upper = re.search(r'[A-Z]', key) is not None
        has_digit = re.search(r'\d', key) is not None
        has_special = re.search(r'[^a-zA-Z0-9]', key) is not None

        # 每包含一种类型加1分，最多4分
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        score += char_types

        # 3. 复杂度评估（占比30%）
        # 3.1 避免纯数字或纯字母
        if not (key.isdigit() or key.isalpha()):
            score += 1

        # 3.2 检查是否包含常见弱密码模式（如连续字符、重复字符）
        weak_patterns = [
            r'^(0-9){6,}$',  # 纯数字且长度≥6
            r'^[a-zA-Z]{6,}$',  # 纯字母且长度≥6
            r'^(.)\1{4,}$',  # 单个字符重复≥5次（如aaaaa）
            r'^123456|654321|111111|abcdef|fedcba$'  # 常见序列
        ]
        is_weak_pattern = any(re.match(pattern, key.lower()) for pattern in weak_patterns)
        if not is_weak_pattern:
            score += 1

        # 3.3 检查是否包含常见词典词（简单检查）
        common_words = {'password', '123456', 'qwerty', 'admin', 'user', 'passwd', 'abc123'}
        if key.lower() not in common_words and not any(word in key.lower() for word in common_words):
            score += 1

        # 映射分数到0-5级（总分最高10分）
        level = min(5, max(0, (score // 2)))  # 10分→5级，8分→4级，以此类推
        return level

    @staticmethod
    def argon2_base64_decode(encoded: str) -> bytes:
        """
        手动解码Argon2使用的Base64变体（不依赖私有API）
        参考：https://github.com/P-H-C/phc-winner-argon2/blob/master/src/encoding.c
        """
        # 1. 替换特殊字符（Argon2用-代替+，用_代替/）
        encoded = encoded.replace('-', '+').replace('_', '/')

        # 2. 补充Base64填充符=（确保长度是4的倍数）
        padding_needed = (4 - (len(encoded) % 4)) % 4
        encoded += '=' * padding_needed

        # 3. 标准Base64解码
        return base64.b64decode(encoded)


if __name__=="__main__":
    # API示例
    m_KeyWordNotBook = KeyWordNoteBook("testp")
    testlint = KeyItem()
    testlint.update({
        "Index": "0",
        "PasswordLevel": 4,
        "URL": "https://github.com/settings/profile",
        "UserName": "1428483061@qq.com",
        "Password": "123456",
        "LinkURL": "",
        "Note": "github账户" })

    # # 写入密码本
    m_KeyWordNotBook.add_item(testlint,upw="testpw")
    # m_KeyWordNotBook.delete_item("11",upw="testpw")
    # m_KeyWordNotBook.update_item("1",testlint,upw="testpw")
    # print(m_KeyWordNotBook.get_item_by_id("7",upw="testpw"))
    # m_KeyWordNotBook.get_item_by_id("2",upw="testpasswords")
    # m_KeyWordNotBook.get_item_by_id("2",upw="testpw")
