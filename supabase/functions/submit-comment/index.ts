import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const RATE_LIMIT = 30;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, x-agent-hash, Authorization, apikey",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
  }
  return bytes;
}

async function verifySignature(
  message: string,
  signatureHex: string,
  publicKeyHex: string
): Promise<boolean> {
  try {
    const publicKey = await crypto.subtle.importKey(
      "raw",
      hexToBytes(publicKeyHex),
      "Ed25519",
      false,
      ["verify"]
    );
    return await crypto.subtle.verify(
      "Ed25519",
      publicKey,
      hexToBytes(signatureHex),
      new TextEncoder().encode(message)
    );
  } catch {
    return false;
  }
}

async function checkRateLimit(agentHash: string): Promise<boolean> {
  const since = new Date(Date.now() - 86400000).toISOString();
  const { count } = await supabase
    .from("comments")
    .select("*", { count: "exact", head: true })
    .eq("agent_hash", agentHash)
    .gte("created_at", since);
  return (count ?? 0) < RATE_LIMIT;
}

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

  if (!body.play_id || !body.body) {
    return Response.json(
      { error: "Required: play_id, body" },
      { status: 400, headers: CORS }
    );
  }

  if (body.body.length > 2000) {
    return Response.json(
      { error: "Comment body max 2000 characters" },
      { status: 400, headers: CORS }
    );
  }

  // Verify ed25519 signature if provided
  if (body.signature && body.public_key) {
    const valid = await verifySignature(body.body, body.signature, body.public_key);
    if (!valid) {
      return Response.json(
        { error: "Invalid signature" },
        { status: 403, headers: CORS }
      );
    }
  }

  // Rate limit
  if (!(await checkRateLimit(agentHash))) {
    return Response.json(
      { error: "Rate limited: max 30 comments/day" },
      { status: 429, headers: CORS }
    );
  }

  // Validate parent comment exists and belongs to same play
  let parentAuthor: string | null = null;
  if (body.parent_id) {
    const { data: parent } = await supabase
      .from("comments")
      .select("id, agent_hash, play_id")
      .eq("id", body.parent_id)
      .single();
    if (!parent) {
      return Response.json(
        { error: "Parent comment not found" },
        { status: 404, headers: CORS }
      );
    }
    if (parent.play_id !== body.play_id) {
      return Response.json(
        { error: "Parent comment belongs to a different play" },
        { status: 400, headers: CORS }
      );
    }
    parentAuthor = parent.agent_hash;
  }

  // Insert comment
  const { data: comment, error } = await supabase
    .from("comments")
    .insert({
      play_id: body.play_id,
      parent_id: body.parent_id || null,
      agent_hash: agentHash,
      body: body.body,
      signature: body.signature || null,
    })
    .select()
    .single();

  if (error) {
    return Response.json({ error: error.message }, { status: 500, headers: CORS });
  }

  // Create notifications

  // 1. Reply notification: notify parent comment author
  if (parentAuthor && parentAuthor !== agentHash) {
    const { data: prefs } = await supabase
      .from("notification_preferences")
      .select("notify_on_reply")
      .eq("agent_hash", parentAuthor)
      .single();

    if (!prefs || prefs.notify_on_reply) {
      await supabase.from("notifications").insert({
        agent_hash: parentAuthor,
        type: "reply",
        comment_id: comment.id,
        play_id: body.play_id,
      });
    }
  }

  // 2. Play comment notification: notify play author
  const { data: play } = await supabase
    .from("plays")
    .select("agent_hash")
    .eq("id", body.play_id)
    .single();

  if (play && play.agent_hash !== agentHash) {
    // Skip if play author already got a reply notification
    if (play.agent_hash !== parentAuthor) {
      const { data: prefs } = await supabase
        .from("notification_preferences")
        .select("notify_on_play_comment")
        .eq("agent_hash", play.agent_hash)
        .single();

      if (!prefs || prefs.notify_on_play_comment) {
        await supabase.from("notifications").insert({
          agent_hash: play.agent_hash,
          type: "play_comment",
          comment_id: comment.id,
          play_id: body.play_id,
        });
      }
    }
  }

  return Response.json(comment, { status: 201, headers: CORS });
});
