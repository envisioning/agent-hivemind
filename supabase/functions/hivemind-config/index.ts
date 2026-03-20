// Public config endpoint — returns the anon key and URL for hivemind clients.
// No auth required. This replaces embedding the key in the script.

Deno.serve((_req: Request) => {
  return new Response(
    JSON.stringify({
      supabase_url: "https://tjcryyjrjxbcjzybzdow.supabase.co",
      supabase_anon_key:
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +
        "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqY3J5eWpyanhiY2p6eWJ6ZG93Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5NTIzNjUsImV4cCI6MjA4OTUyODM2NX0." +
        "G_PtxkbqXO6jz1mGUX7-afO1WlHl1c_z0_QBNbqLeJU",
      version: "1.0",
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=86400",
      },
    },
  );
});
