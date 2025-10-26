"""
测试 MongoDB 连接
用于验证数据库配置是否正确
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

async def test_connection():
    """测试数据库连接"""
    print("正在测试 MongoDB 连接...")
    print(f"连接地址: {settings.MONGODB_URL.split('@')[1] if '@' in settings.MONGODB_URL else settings.MONGODB_URL}")
    print(f"数据库名: {settings.MONGODB_DB_NAME}")
    
    try:
        # 创建客户端
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # 测试连接
        await client.admin.command('ping')
        print("✓ 数据库连接成功！")
        
        # 获取数据库
        db = client[settings.MONGODB_DB_NAME]
        
        # 列出集合
        collections = await db.list_collection_names()
        print(f"✓ 当前数据库中的集合: {collections if collections else '(空)'}")
        
        # 测试写入权限
        test_collection = db.test_connection
        result = await test_collection.insert_one({"test": "connection", "timestamp": "test"})
        print(f"✓ 写入测试成功，文档ID: {result.inserted_id}")
        
        # 测试读取权限
        doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✓ 读取测试成功: {doc}")
        
        # 清理测试数据
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✓ 清理测试数据成功")
        
        # 关闭连接
        client.close()
        print("\n✅ 所有数据库连接测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {e}")
        print("\n请检查以下配置：")
        print("1. MongoDB 服务器地址是否正确")
        print("2. 用户名和密码是否正确")
        print("3. 数据库名称是否正确")
        print("4. 网络连接是否正常")
        print("5. 防火墙是否允许连接")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())

