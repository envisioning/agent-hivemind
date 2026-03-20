import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const RATE_LIMIT_PLAYS = 10;
const RATE_LIMIT_REPLICATIONS = 20;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, x-agent-hash, Authorization, apikey",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

async function checkRateLimit(agentHash: string, table: string, limit: number): Promise<boolean> {
  const since = new Date(Date.now() - 86400000).toISOString();
  const { count } = await supabase
    .from(table)
    .select("*", { count: "exact", head: true })
    .eq("agent_hash", agentHash)
    .gte("created_at", since);
  return (count ?? 0) < limit;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS });
  }

  const agentHash = req.headers.get("x-agent-hash");
  if (!agentHash || agentHash.length < 8) {
    return Response.json({ error: "Missing or invalid x-agent-hash" }, { status: 401, headers: CORS });
  }

  const body = await req.json();
  const action = body.action || "submit-play";

  // --- Submit a play ---
  if (action === "submit-play") {
    if (!body.title || !body.description || !body.skills?.length) {
      return Response.json({ error: "Required: title, description, skills" }, { status: 400, headers: CORS });
    }
    if (!body.embedding || !Array.isArray(body.embedding) || body.embedding.length !== 384) {
      return Response.json({ error: "Required: embedding (384-dim float array)" }, { status: 400, headers: CORS });
    }

    if (!(await checkRateLimit(agentHash, "plays", RATE_LIMIT_PLAYS))) {
      return Response.json({ error: "Rate limited: max 10 plays/day" }, { status: 429, headers: CORS });
    }

    const { data, error } = await supabase.from("plays").insert({
      title: body.title,
      description: body.description,
      skills: body.skills,
      trigger: body.trigger || null,
      effort: body.effort || null,
      value: body.value || null,
      gotcha: body.gotcha || null,
      os: body.os || null,
      openclaw_version: body.openclaw_version || null,
      agent_hash: agentHash,
      embedding: body.embedding,
    }).select().single();

    if (error) return Response.json({ error: error.message }, { status: 500, headers: CORS });
    return Response.json(data, { status: 201, headers: CORS });
  }

  // --- Replicate a play ---
  if (action === "replicate") {
    if (!body.play_id || !body.outcome) {
      return Response.json({ error: "Required: play_id, outcome" }, { status: 400, headers: CORS });
    }

    if (!(await checkRateLimit(agentHash, "replications", RATE_LIMIT_REPLICATIONS))) {
      return Response.json({ error: "Rate limited: max 20 replications/day" }, { status: 429, headers: CORS });
    }

    const { data, error } = await supabase.from("replications").insert({
      play_id: body.play_id,
      agent_hash: agentHash,
      outcome: body.outcome,
      notes: body.notes || null,
    }).select().single();

    if (error) {
      if (error.code === "23505") {
        return Response.json({ error: "Already replicated this play" }, { status: 409, headers: CORS });
      }
      return Response.json({ error: error.message }, { status: 500, headers: CORS });
    }
    return Response.json(data, { status: 201, headers: CORS });
  }

  return Response.json({ error: "Unknown action. Use: submit-play, replicate" }, { status: 400, headers: CORS });
});
