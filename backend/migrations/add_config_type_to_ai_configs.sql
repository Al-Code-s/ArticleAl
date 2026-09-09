-- 添加 config_type 字段到 ai_configs 表
-- 执行时间: 2026-09-08

-- 1. 添加 config_type 字段（允许为NULL，用于迁移）
ALTER TABLE ai_configs
ADD COLUMN config_type VARCHAR(50);

-- 2. 为现有数据设置默认值（假设现有配置都是内容生成类型）
UPDATE ai_configs
SET config_type = 'content_generation'
WHERE config_type IS NULL;

-- 3. 将字段设置为NOT NULL
ALTER TABLE ai_configs
ALTER COLUMN config_type SET NOT NULL;

-- 4. 添加索引以提高查询性能
CREATE INDEX idx_ai_configs_config_type ON ai_configs(config_type);
CREATE INDEX idx_ai_configs_user_config_type ON ai_configs(user_id, config_type);

-- 回滚脚本（如果需要）
-- ALTER TABLE ai_configs DROP COLUMN config_type;
-- DROP INDEX IF EXISTS idx_ai_configs_config_type;
-- DROP INDEX IF EXISTS idx_ai_configs_user_config_type;
