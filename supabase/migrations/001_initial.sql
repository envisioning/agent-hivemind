-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Plays table
CREATE TABLE plays (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text NOT NULL,
  skills text[] NOT NULL CHECK (array_length(skills, 1) > 0),
  trigger text CHECK (trigger IN ('cron', 'manual', 'reactive', 'event')),
  effort text CHECK (effort IN ('low', 'medium', 'high')),
  value text CHECK (value IN ('low', 'medium', 'high')),
  gotcha text,
  os text,
  openclaw_version text,
  agent_hash text NOT NULL,
  embedding vector(384),
  replication_count int DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Replications table
CREATE TABLE replications (
  play_id uuid REFERENCES plays ON DELETE CASCADE,
  agent_hash text NOT NULL,
  outcome text NOT NULL CHECK (outcome IN ('success', 'partial', 'failed')),
  notes text,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (play_id, agent_hash)
);

-- Indexes
CREATE INDEX idx_plays_skills ON plays USING GIN (skills);
CREATE INDEX idx_plays_embedding ON plays USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX idx_plays_replication_count ON plays (replication_count DESC);
CREATE INDEX idx_plays_created_at ON plays (created_at DESC);
CREATE INDEX idx_plays_agent_hash ON plays (agent_hash);

-- RLS
ALTER TABLE plays ENABLE ROW LEVEL SECURITY;
ALTER TABLE replications ENABLE ROW LEVEL SECURITY;

-- Anyone can read
CREATE POLICY "plays_select" ON plays FOR SELECT USING (true);
CREATE POLICY "replications_select" ON replications FOR SELECT USING (true);

-- Only service role can insert (edge functions)
CREATE POLICY "plays_insert" ON plays FOR INSERT WITH CHECK (false);
CREATE POLICY "replications_insert" ON replications FOR INSERT WITH CHECK (false);

-- Semantic search function
CREATE OR REPLACE FUNCTION search_plays(
  query_embedding vector(384),
  match_count int DEFAULT 10,
  filter_skills text[] DEFAULT NULL
)
RETURNS TABLE (
  id uuid, title text, description text, skills text[],
  trigger text, effort text, value text, gotcha text,
  replication_count int, similarity float
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id, p.title, p.description, p.skills,
    p.trigger, p.effort, p.value, p.gotcha,
    p.replication_count,
    1 - (p.embedding <=> query_embedding) as similarity
  FROM plays p
  WHERE (filter_skills IS NULL OR p.skills && filter_skills)
  ORDER BY p.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Suggest plays based on installed skills
CREATE OR REPLACE FUNCTION suggest_plays(
  agent_skills text[],
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id uuid, title text, description text, skills text[],
  trigger text, effort text, value text, gotcha text,
  replication_count int, missing_skills text[]
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id, p.title, p.description, p.skills,
    p.trigger, p.effort, p.value, p.gotcha,
    p.replication_count,
    ARRAY(SELECT unnest(p.skills) EXCEPT SELECT unnest(agent_skills)) as missing_skills
  FROM plays p
  WHERE p.skills && agent_skills
  ORDER BY 
    CASE WHEN p.skills <@ agent_skills THEN 0 ELSE 1 END,
    p.replication_count DESC
  LIMIT match_count;
END;
$$;

-- Skill co-occurrence function
CREATE OR REPLACE FUNCTION skill_cooccurrence(
  target_skill text,
  match_count int DEFAULT 10
)
RETURNS TABLE (co_skill text, frequency bigint)
LANGUAGE sql AS $$
  SELECT s as co_skill, count(*) as frequency
  FROM plays, unnest(skills) as s
  WHERE target_skill = ANY(skills) AND s != target_skill
  GROUP BY s
  ORDER BY frequency DESC
  LIMIT match_count;
$$;

-- Trigger to update replication_count
CREATE OR REPLACE FUNCTION update_replication_count()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  UPDATE plays SET replication_count = (
    SELECT count(*) FROM replications WHERE play_id = NEW.play_id
  ) WHERE id = NEW.play_id;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_replication_count
AFTER INSERT ON replications
FOR EACH ROW EXECUTE FUNCTION update_replication_count();
