"""
执行数据库迁移脚本
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从DATABASE_URL解析连接信息
DATABASE_URL = os.getenv("DATABASE_URL", "")
# 将asyncpg格式转换为标准格式
db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def run_migration():
    """执行迁移"""
    print("开始执行数据库迁移...")

    # 连接数据库
    conn = await asyncpg.connect(db_url)

    try:
        # 定义迁移SQL语句
        migrations = [
            # 1. 添加 config_type 字段
            """ALTER TABLE ai_configs ADD COLUMN config_type VARCHAR(50)""",

            # 2. 为现有数据设置默认值
            """UPDATE ai_configs SET config_type = 'content_generation' WHERE config_type IS NULL""",

            # 3. 将字段设置为NOT NULL
            """ALTER TABLE ai_configs ALTER COLUMN config_type SET NOT NULL""",

            # 4. 添加索引
            """CREATE INDEX idx_ai_configs_config_type ON ai_configs(config_type)""",
            """CREATE INDEX idx_ai_configs_user_config_type ON ai_configs(user_id, config_type)""",
        ]

        # 执行每条SQL
        for i, sql in enumerate(migrations):
            print(f"\n[{i+1}/{len(migrations)}] 执行: {sql[:80]}...")

            try:
                await conn.execute(sql)
                print("    成功")
            except Exception as e:
                error_msg = str(e)
                print(f"    失败: {error_msg}")

                # 如果字段/索引已存在，继续执行
                if "already exists" in error_msg or "duplicate" in error_msg.lower():
                    print("    (已存在，跳过)")
                    continue
                else:
                    raise

        print("\n" + "="*50)
        print("数据库迁移完成！")
        print("="*50)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
