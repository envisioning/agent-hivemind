-- Add risk_card JSONB column to plays table
-- Stores deterministic risk assessment: overall level, dimension scores, detected flags
ALTER TABLE plays ADD COLUMN risk_card jsonb;
