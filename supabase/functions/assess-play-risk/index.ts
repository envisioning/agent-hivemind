import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, apikey",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

// --- Feature detection patterns ---
// Each pattern maps a feature flag to regex patterns checked against play content

type FeatureFlag =
  | "shell_exec"
  | "writes_files"
  | "deletes_files"
  | "uses_network"
  | "uses_credentials"
  | "writes_external"
  | "installs_dependencies"
  | "creates_persistence"
  | "touches_personal_data"
  | "runs_remote_code";

const FEATURE_PATTERNS: Record<FeatureFlag, RegExp[]> = {
  shell_exec: [
    /\bshell\b/i, /\bbash\b/i, /\bexec\b/i, /\bcommand[- ]?line\b/i,
    /\bterminal\b/i, /\bsubprocess\b/i, /\bspawn\b/i, /\bsystem\s*\(/i,
    /\bchild.process\b/i, /\bos\.system\b/i,
  ],
  writes_files: [
    /\bwrit(e|es|ing)\s+(to\s+)?(a\s+)?file/i, /\bsave\s+(to\s+)?disk/i,
    /\bfs\.write/i, /\bfile\s+output/i, /\bcreate\s+(a\s+)?file/i,
    /\bwrite\s+to\s+disk/i, /\boverwrite/i,
  ],
  deletes_files: [
    /\bdelet(e|es|ing)\s+(a\s+)?file/i, /\bremov(e|es|ing)\s+(a\s+)?file/i,
    /\brm\s+-/i, /\bunlink/i, /\bclean\s*up\b.*file/i,
    /\bwipe/i, /\bpurge/i,
  ],
  uses_network: [
    /\bhttp/i, /\bapi\b/i, /\bfetch/i, /\brequest/i,
    /\bcurl\b/i, /\bwebhook/i, /\bendpoint/i, /\burl\b/i,
    /\bsocket\b/i, /\bwebsocket/i,
  ],
  uses_credentials: [
    /\bapi[- ]?key/i, /\btoken/i, /\bcredential/i, /\bpassword/i,
    /\bsecret/i, /\bauth/i, /\boauth/i, /\b\.env\b/i,
    /\bservice[- ]?account/i, /\baccess[- ]?key/i,
  ],
  writes_external: [
    /\bsend\s+(an?\s+)?email/i, /\bpost\s+to\b/i, /\bslack\b/i,
    /\btweet/i, /\bpublish/i, /\bnotif(y|ication)/i,
    /\bsms\b/i, /\bmessage\b/i, /\bgmail\b/i, /\bwebhook\b/i,
    /\bupload/i, /\bdeploy/i,
  ],
  installs_dependencies: [
    /\bnpm\s+install/i, /\bpip\s+install/i, /\bbrew\s+install/i,
    /\bapt[- ]get/i, /\byarn\s+add/i, /\binstall\s+(a\s+)?package/i,
    /\binstall\s+(a\s+)?dependenc/i, /\bcargo\s+add/i,
  ],
  creates_persistence: [
    /\bcron/i, /\bschedul/i, /\bdaemon/i, /\bsystemd/i,
    /\blaunchd/i, /\bstartup/i, /\bautostart/i,
    /\bbackground\s+(task|job|process)/i, /\bpersist/i,
  ],
  touches_personal_data: [
    /\bcontact/i, /\bcalendar/i, /\bemail\b/i, /\bgmail\b/i,
    /\bpersonal\b/i, /\bprivate\b/i, /\bhealth\b/i,
    /\blocation\b/i, /\bbrowsing\s+history/i, /\bphoto/i,
  ],
  runs_remote_code: [
    /\beval\b/i, /\bremote\s+(code|script|exec)/i,
    /\bdownload\s+and\s+(run|exec)/i, /\bcurl.*\|\s*bash/i,
    /\bscript\s+injection/i, /\bcode\s+from\s+(url|remote|internet)/i,
  ],
};

// --- Dimension scoring rules ---
// Maps feature flags to the dimensions they affect and at what level

type RiskLevel = "low" | "medium" | "high";
type Dimension =
  | "security"
  | "privacy"
  | "destructiveness"
  | "cost"
  | "external_side_effects"
  | "supply_chain"
  | "reversibility"
  | "autonomy";

const DIMENSION_RULES: Array<{
  flag: FeatureFlag;
  dimension: Dimension;
  level: RiskLevel;
}> = [
  // Security
  { flag: "runs_remote_code", dimension: "security", level: "high" },
  { flag: "shell_exec", dimension: "security", level: "medium" },
  { flag: "uses_credentials", dimension: "security", level: "medium" },
  { flag: "installs_dependencies", dimension: "security", level: "medium" },

  // Privacy
  { flag: "uses_credentials", dimension: "privacy", level: "high" },
  { flag: "touches_personal_data", dimension: "privacy", level: "high" },
  { flag: "uses_network", dimension: "privacy", level: "low" },

  // Destructiveness
  { flag: "deletes_files", dimension: "destructiveness", level: "high" },
  { flag: "writes_files", dimension: "destructiveness", level: "medium" },
  { flag: "shell_exec", dimension: "destructiveness", level: "low" },

  // Cost
  { flag: "uses_network", dimension: "cost", level: "low" },
  { flag: "writes_external", dimension: "cost", level: "medium" },
  { flag: "installs_dependencies", dimension: "cost", level: "low" },

  // External side effects
  { flag: "writes_external", dimension: "external_side_effects", level: "high" },
  { flag: "uses_network", dimension: "external_side_effects", level: "medium" },

  // Supply chain
  { flag: "installs_dependencies", dimension: "supply_chain", level: "high" },
  { flag: "runs_remote_code", dimension: "supply_chain", level: "high" },

  // Reversibility
  { flag: "deletes_files", dimension: "reversibility", level: "high" },
  { flag: "writes_external", dimension: "reversibility", level: "high" },
  { flag: "writes_files", dimension: "reversibility", level: "medium" },
  { flag: "creates_persistence", dimension: "reversibility", level: "medium" },

  // Autonomy
  { flag: "creates_persistence", dimension: "autonomy", level: "high" },
  { flag: "shell_exec", dimension: "autonomy", level: "medium" },
  { flag: "runs_remote_code", dimension: "autonomy", level: "high" },
];

// Required capabilities inferred from flags
const CAPABILITY_MAP: Partial<Record<FeatureFlag, string>> = {
  shell_exec: "shell",
  writes_files: "filesystem_write",
  deletes_files: "filesystem_write",
  uses_network: "network",
  uses_credentials: "credentials",
  writes_external: "external_services",
  installs_dependencies: "package_manager",
  creates_persistence: "system_config",
  touches_personal_data: "personal_data",
  runs_remote_code: "code_execution",
};

const LEVEL_RANK: Record<RiskLevel, number> = { low: 1, medium: 2, high: 3 };
const RANK_TO_LEVEL: Record<number, RiskLevel> = { 1: "low", 2: "medium", 3: "high" };

function extractFeatures(content: string): FeatureFlag[] {
  const detected: FeatureFlag[] = [];
  for (const [flag, patterns] of Object.entries(FEATURE_PATTERNS)) {
    if (patterns.some((re) => re.test(content))) {
      detected.push(flag as FeatureFlag);
    }
  }
  return detected;
}

function scoreDimensions(flags: FeatureFlag[]): Record<Dimension, RiskLevel> {
  const scores: Record<Dimension, number> = {
    security: 0,
    privacy: 0,
    destructiveness: 0,
    cost: 0,
    external_side_effects: 0,
    supply_chain: 0,
    reversibility: 0,
    autonomy: 0,
  };

  const flagSet = new Set(flags);

  for (const rule of DIMENSION_RULES) {
    if (flagSet.has(rule.flag)) {
      const rank = LEVEL_RANK[rule.level];
      if (rank > scores[rule.dimension]) {
        scores[rule.dimension] = rank;
      }
    }
  }

  const result: Record<string, RiskLevel> = {};
  for (const [dim, rank] of Object.entries(scores)) {
    result[dim] = RANK_TO_LEVEL[rank] || "low";
  }
  return result as Record<Dimension, RiskLevel>;
}

function computeOverall(dimensions: Record<Dimension, RiskLevel>): RiskLevel {
  let maxRank = 0;
  for (const level of Object.values(dimensions)) {
    const rank = LEVEL_RANK[level];
    if (rank > maxRank) maxRank = rank;
  }
  return RANK_TO_LEVEL[maxRank] || "low";
}

function computeConfidence(flags: FeatureFlag[]): number {
  // More flags detected => higher confidence in the assessment
  // 0 flags => 0.2 (low confidence baseline), 5+ flags => 0.9 cap
  const count = flags.length;
  if (count === 0) return 0.2;
  return Math.min(0.9, 0.2 + count * 0.14);
}

function buildRiskCard(play: { title: string; description: string; gotcha?: string }) {
  const content = [play.title, play.description, play.gotcha || ""].join(" ");
  const flags = extractFeatures(content);
  const dimensions = scoreDimensions(flags);
  const overall = computeOverall(dimensions);
  const confidence = Math.round(computeConfidence(flags) * 100) / 100;

  const required_capabilities = [
    ...new Set(flags.map((f) => CAPABILITY_MAP[f]).filter(Boolean)),
  ];

  return {
    overall,
    confidence,
    dimensions,
    flags,
    required_capabilities,
  };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS });
  }

  try {
    const body = await req.json();
    const action = body.action || "assess";

    // --- Assess a single play by ID ---
    if (action === "assess") {
      if (!body.play_id) {
        return Response.json({ error: "Required: play_id" }, { status: 400, headers: CORS });
      }

      const { data: play, error } = await supabase
        .from("plays")
        .select("id, title, description, gotcha")
        .eq("id", body.play_id)
        .single();

      if (error || !play) {
        return Response.json({ error: "Play not found" }, { status: 404, headers: CORS });
      }

      const riskCard = buildRiskCard(play);

      const { error: updateError } = await supabase
        .from("plays")
        .update({ risk_card: riskCard })
        .eq("id", play.id);

      if (updateError) {
        return Response.json({ error: updateError.message }, { status: 500, headers: CORS });
      }

      return Response.json({ play_id: play.id, risk_card: riskCard }, { headers: CORS });
    }

    // --- Backfill: assess all plays without a risk_card ---
    if (action === "backfill") {
      const { data: plays, error } = await supabase
        .from("plays")
        .select("id, title, description, gotcha")
        .is("risk_card", null);

      if (error) {
        return Response.json({ error: error.message }, { status: 500, headers: CORS });
      }

      let updated = 0;
      for (const play of plays || []) {
        const riskCard = buildRiskCard(play);
        const { error: updateError } = await supabase
          .from("plays")
          .update({ risk_card: riskCard })
          .eq("id", play.id);
        if (!updateError) updated++;
      }

      return Response.json({ updated, total: (plays || []).length }, { headers: CORS });
    }

    // --- Preview: assess content without saving ---
    if (action === "preview") {
      if (!body.title || !body.description) {
        return Response.json({ error: "Required: title, description" }, { status: 400, headers: CORS });
      }

      const riskCard = buildRiskCard({
        title: body.title,
        description: body.description,
        gotcha: body.gotcha,
      });

      return Response.json({ risk_card: riskCard }, { headers: CORS });
    }

    return Response.json(
      { error: "Unknown action. Use: assess, backfill, preview" },
      { status: 400, headers: CORS }
    );
  } catch (err) {
    return Response.json(
      { error: err instanceof Error ? err.message : "Internal error" },
      { status: 500, headers: CORS }
    );
  }
});
