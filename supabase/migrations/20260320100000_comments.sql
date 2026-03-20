-- Comments, notifications, and notification preferences

-- Comments table
CREATE TABLE comments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  play_id uuid NOT NULL REFERENCES plays ON DELETE CASCADE,
  parent_id uuid REFERENCES comments ON DELETE CASCADE,
  agent_hash text NOT NULL,
  body text NOT NULL CHECK (char_length(body) <= 2000),
  signature text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Notification preferences (per agent)
CREATE TABLE notification_preferences (
  agent_hash text PRIMARY KEY,
  notify_on_reply boolean DEFAULT true,
  notify_on_play_comment boolean DEFAULT true,
  webhook_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Notification type enum
CREATE TYPE notification_type AS ENUM ('reply', 'play_comment');

-- Notifications table
CREATE TABLE notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_hash text NOT NULL,
  type notification_type NOT NULL,
  comment_id uuid REFERENCES comments ON DELETE CASCADE,
  play_id uuid REFERENCES plays ON DELETE CASCADE,
  read boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Indexes
CREATE INDEX idx_comments_play_id ON comments (play_id);
CREATE INDEX idx_comments_agent_hash ON comments (agent_hash);
CREATE INDEX idx_comments_parent_id ON comments (parent_id);
CREATE INDEX idx_notifications_agent_read_created ON notifications (agent_hash, read, created_at DESC);

-- RLS
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- SELECT: public
CREATE POLICY "comments_select" ON comments FOR SELECT USING (true);
CREATE POLICY "notification_preferences_select" ON notification_preferences FOR SELECT USING (true);
CREATE POLICY "notifications_select" ON notifications FOR SELECT USING (true);

-- INSERT: service role only (edge functions)
CREATE POLICY "comments_insert" ON comments FOR INSERT WITH CHECK (false);
CREATE POLICY "notification_preferences_insert" ON notification_preferences FOR INSERT WITH CHECK (false);
CREATE POLICY "notifications_insert" ON notifications FOR INSERT WITH CHECK (false);

-- UPDATE: service role only (edge functions mark read, upsert prefs)
CREATE POLICY "notifications_update" ON notifications FOR UPDATE USING (false);
CREATE POLICY "notification_preferences_update" ON notification_preferences FOR UPDATE USING (false);

-- updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_comments_updated_at
BEFORE UPDATE ON comments
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_notification_preferences_updated_at
BEFORE UPDATE ON notification_preferences
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
