import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, x-agent-hash, Authorization, apikey",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS });
  }

  const agentHash = req.headers.get("x-agent-hash");
  if (!agentHash || agentHash.length < 8) {
    return Response.json(
      { error: "Missing or invalid x-agent-hash" },
      { status: 401, headers: CORS }
    );
  }

  const body = await req.json();

  const row: Record<string, unknown> = { agent_hash: agentHash };
  if (body.notify_on_reply !== undefined) row.notify_on_reply = body.notify_on_reply;
  if (body.notify_on_play_comment !== undefined) row.notify_on_play_comment = body.notify_on_play_comment;
  if (body.webhook_url !== undefined) row.webhook_url = body.webhook_url;

  const { data, error } = await supabase
    .from("notification_preferences")
    .upsert(row, { onConflict: "agent_hash" })
    .select()
    .single();

  if (error) {
    return Response.json({ error: error.message }, { status: 500, headers: CORS });
  }

  return Response.json(data, { headers: CORS });
});
