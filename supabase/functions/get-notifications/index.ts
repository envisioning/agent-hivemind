import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, x-agent-hash, Authorization, apikey",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
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

  // Fetch unread notifications with comment body and play title
  const { data: notifications, error } = await supabase
    .from("notifications")
    .select("id, type, created_at, comment:comments(body, agent_hash), play:plays(title)")
    .eq("agent_hash", agentHash)
    .eq("read", false)
    .order("created_at", { ascending: false })
    .limit(50);

  if (error) {
    return Response.json({ error: error.message }, { status: 500, headers: CORS });
  }

  // Mark fetched notifications as read
  if (notifications && notifications.length > 0) {
    const ids = notifications.map((n) => n.id);
    await supabase
      .from("notifications")
      .update({ read: true })
      .in("id", ids);
  }

  return Response.json(notifications || [], { headers: CORS });
});
