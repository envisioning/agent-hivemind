# OpenClaw Plays Database — Full Review (207 plays)

Generated 2026-03-20. All descriptions enriched from source material.

---
## Morning daily brief
**Trigger:** cron | **Effort:** low | **Value:** high
Automated morning summary delivered at a consistent time combining weather forecast, calendar events, active tasks from your todo app, and stalled reminders. Delivered to Telegram or Discord. Skips empty sections entirely rather than padding with 'nothing found.' Orders items by urgency and includes a personalized note based on recent work patterns. One user reads it while making coffee — it replaces checking 5 different apps to start the day. The quality depends on how many data sources you connect: weather + calendar + todo at minimum.
**Skills:** weather, calendar, todoist
**Gotcha:** Timing matters — too early and calendar data is stale, too late and you've already started your day without the info. The 'skip empty sections' rule is critical for scannability. Start with weather + calendar + todo, then add news and custom sections gradually.
**Source:** https://github.com/digitalknk/openclaw-runbook/blob/main/showcases/daily-brief.md

## Overnight idea research pipeline
**Trigger:** cron | **Effort:** medium | **Value:** high
Capture ideas throughout the day via quick messages ('research solar panels for the cabin'), then at 3 AM the agent runs web research on each pending idea: existing solutions, market landscape, technical feasibility (1-5 scale), and concrete next steps. By morning you have a research document for each idea ready for review. The research runs in isolated sessions so it doesn't pollute your main context. One user describes waking up to '3 research docs on my desk' after brain-dumping ideas before bed.
**Skills:** web_search, todoist
**Gotcha:** Use isolated sessions — research can take 10+ minutes per idea and generates tons of intermediate context. Set a cost cap per night ($5-10) because autonomous research burns tokens fast. The value isn't perfect research; it's triaging 10 ideas down to 2 worth pursuing.
**Source:** https://github.com/digitalknk/openclaw-runbook/blob/main/showcases/idea-pipeline.md

## Weekly LinkedIn post drafter
**Trigger:** cron | **Effort:** medium | **Value:** medium
Every Tuesday, reviews your recent activity from memory files, completed tasks, git commits, and projects, identifies post-worthy insights, and drafts 2-3 LinkedIn posts in your authentic voice. Saved to Notion or a doc for review before posting. The agent learns your voice by reading past posts — strips AI patterns like em dashes and bullet-heavy structure. The best posts come from genuine insights in your daily work, not forced content generation.
**Skills:** notion, memory_search
**Gotcha:** Define voice characteristics explicitly or every post sounds generic. Point the agent at 10-20 of your actual posts so it learns your style. The agent should flag when there's nothing worth posting rather than generate fluff — forced LinkedIn posts are worse than no posts.
**Source:** https://github.com/digitalknk/openclaw-runbook/blob/main/showcases/linkedin-drafter.md

## Weekly tech discoveries digest
**Trigger:** cron | **Effort:** low | **Value:** high
Every Sunday, aggregates tech news from newsletters (via email), GitHub Trending, Hacker News, and relevant subreddits. Curates 5-10 items with one-sentence summaries grouped by category. Filters aggressively based on your interests and past reading patterns. Add explicit skip filters ('skip crypto, generic AI hype') or you get drowned in noise. Delivered as a clean scannable message you can read in 5 minutes.
**Skills:** gmail, web_search, browser
**Gotcha:** The filtering is make-or-break — without it you get 30 items and stop reading. Newsletters often have 2-day delays, so Sunday aggregation gives a complete week view. Also: the agent should link to the original source, not just summarize — you want to be able to click through on interesting items.
**Source:** https://github.com/digitalknk/openclaw-runbook/blob/main/showcases/tech-discoveries.md

## Homelab SSH via Telegram
**Trigger:** reactive | **Effort:** medium | **Value:** high
Run SSH commands on homelab devices through Telegram messages. Uses Tailscale for secure networking. Safety guardrails: confirmation prompts for destructive commands (rm, reboot, dd), command allowlisting for routine operations, and automatic timeout on long-running commands. Quick checks when away from home: 'is Plex running?', 'restart the Docker container', 'check disk space on the NAS.' One user calls this 'a working Unix sysadmin in your pocket for a few dollars per month.'
**Skills:** telegram, exec
**Gotcha:** Always require confirmation for destructive commands — one bad rm -rf from a compromised Telegram account and your NAS is gone. Use Tailscale IPs rather than exposing SSH to the internet. The agent should log all commands executed for audit purposes.
**Source:** https://github.com/digitalknk/openclaw-runbook/blob/main/showcases/homelab-access.md

## Coding task orchestrator
**Trigger:** reactive | **Effort:** medium | **Value:** high
Routes coding tasks to the optimal tool based on complexity: Claude for multi-file refactors and architecture, Codex for standard feature implementation, OpenCode for quick edits. The orchestrator classifies incoming tasks and dispatches automatically. Tracks quota across providers — if one hits rate limits, falls back gracefully. Also monitors cost per task so you see what each operation costs before approving.
**Skills:** coding-agent
**Gotcha:** The classification isn't perfect — sometimes complex work gets sent to a cheap model. Build in escalation: if a task fails twice, escalate to a more capable model. The real value is not having to think about which tool to use for each task.
**Source:** https://github.com/digitalknk/openclaw-runbook/blob/main/showcases/agent-orchestrator.md

## Daily Reddit digest
**Trigger:** cron | **Effort:** low | **Value:** medium
Curated daily summary of top posts from your favorite subreddits, filtered by relevance rather than just popularity. The agent scores posts by topic match, engagement patterns, and discussion depth. Delivers a scannable summary with 1-2 sentence highlights per post. Learns which types of posts you engage with and adjusts scoring over time.
**Skills:** web_search, browser
**Gotcha:** Reddit API rate limits are tight (60 req/min for OAuth) — use web scraping via the public JSON endpoints (reddit.com/r/sub.json) as fallback. Tell the agent which topics within each subreddit interest you: 'r/programming: architecture discussions, NOT language wars.'
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/daily-reddit-digest.md

## Daily YouTube digest
**Trigger:** cron | **Effort:** low | **Value:** medium
Daily summaries of new videos from channels you follow. The agent checks your subscription list, fetches transcripts via yt-dlp, generates 2-3 sentence summaries, and delivers a digest. You decide which videos are worth watching based on the summary rather than clicking through dozens of thumbnails. Can also extract key timestamps and links mentioned in the video. Particularly useful for educational and tech channels.
**Skills:** web_search
**Gotcha:** YouTube API quota is 10K units/day — transcript fetching burns 1-2 units per video, plenty for personal use. Transcript quality varies: auto-captions are good for educational content but terrible for music or heavily edited videos. Batch requests and cache results to stay within limits.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/daily-youtube-digest.md

## X/Twitter account analysis
**Trigger:** manual | **Effort:** low | **Value:** medium
Qualitative analysis of your X/Twitter account: posting patterns, engagement trends by content type, follower growth, optimal posting times, and content gap identification. The agent analyzes your tweet history to find what performs best, then suggests improvements: 'you tweet about frontend but never about the backend work you actually do.' Also tracks competitor accounts for benchmarking.
**Skills:** browser, web_search
**Gotcha:** X API access costs $100/month at basic tier — most people use browser scraping instead. Without API access you only see public metrics (likes, retweets), not impressions or detailed analytics. For serious growth tracking, the official analytics CSV export is better than what the agent can scrape.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/x-account-analysis.md

## Multi-source tech news aggregator
**Trigger:** cron | **Effort:** high | **Value:** high
Aggregates quality-scored tech news from 100+ sources: RSS feeds, X/Twitter, GitHub, and web search. Natural language filtering: 'AI model releases and benchmarks, NOT AI ethics debates or startup funding.' Each item gets scored on relevance, recency, and source authority. Delivers top 5-10 items with summaries. Cross-references stories across sources ('this paper was also discussed on HN with these specific concerns').
**Skills:** rss-ai-reader, web_search, browser
**Gotcha:** Start with 5-10 sources, not 100 — too many overwhelms the scoring and everything ranks medium. The natural language filter is the differentiator; without it you just get noise. Build your source list incrementally as you discover quality feeds.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/multi-source-tech-news-digest.md

## Overnight mini-app builder
**Trigger:** cron | **Effort:** high | **Value:** high
Brain dump goals before bed and the agent autonomously designs, codes, and builds working prototypes overnight. You wake up to functional demos with documentation. The agent picks 1-3 goals per night based on complexity. Prototypes are intentionally minimal MVPs for idea validation, not production code. One user reports waking up to working apps from vague descriptions like 'I want a simple water intake tracker.'
**Skills:** coding-agent, todoist
**Gotcha:** Set a hard cost cap per night ($5-10) — autonomous coding burns API credits fast. Prototypes should be throwaway demos, not production code. The agent will over-promise on overnight builds; manage expectations: simple CRUD apps yes, ML pipelines no.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/overnight-mini-app-builder.md

## YouTube content pipeline
**Trigger:** cron | **Effort:** medium | **Value:** high
Automated video idea scouting, research, and tracking. The agent monitors trending topics in your niche, researches competitor videos (what's performing and why), suggests ideas with angle differentiation, and tracks your content calendar. When you pick a topic, the agent drafts research notes, talking points, and identifies related content to reference. Builds a queue of vetted ideas so you never face 'what should I make next?'
**Skills:** web_search, notion
**Gotcha:** The research is valuable; raw idea generation less so. The agent suggests generic ideas unless you give specific constraints. Competitor outlier tracking — which videos outperform a channel's baseline — is the highest-value output. Build on that rather than raw suggestions.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/youtube-content-pipeline.md

## Multi-agent content factory
**Trigger:** reactive | **Effort:** high | **Value:** high
Multi-agent content production: research agent does deep dives, writing agent drafts in your voice with the humanizer skill, design agent generates visuals. Each sub-agent runs independently with its own context, reports back to a coordinator agent that assembles the final output. One user reports 3x content output after deploying this pipeline.
**Skills:** discord, coding-agent
**Gotcha:** Spawn sub-agents with independent context — shared sessions pollute outputs. The coordinator needs clear quality criteria: 'reject if it sounds AI-written.' More than 3 sub-agents creates coordination overhead that exceeds the parallel processing benefit.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/content-factory.md

## Self-healing home server
**Trigger:** cron | **Effort:** high | **Value:** high
Always-on infrastructure agent with SSH access to your homelab. Monitors health metrics (CPU, RAM, disk, services), detects crashes, and attempts automatic recovery — restarting services, clearing caches, rolling back changes. When auto-fixes fail, sends you a diagnostic report with logs and suggested manual fixes. Maintains a playbook of common issues that grows with each incident. One user reports 99.9% Plex uptime despite never manually restarting it.
**Skills:** exec, docker-essentials
**Gotcha:** Start with monitoring and alerting before enabling auto-healing — trust the diagnosis first. Auto-healing should be limited to safe operations (restart service, clear cache), never destructive ones (delete data, reformat). Make the playbook editable so you can add manual fixes the agent should learn.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/self-healing-home-server.md

## n8n workflow orchestration
**Trigger:** reactive | **Effort:** medium | **Value:** high
Delegate complex API workflows to n8n (open-source Zapier) via webhooks while the agent handles the natural language interface. You say 'when I get a new client email, create a Todoist task and send me a summary' — the agent calls the n8n webhook. n8n handles actual API integrations, error handling, retries, and credential storage. The agent never touches credentials directly. Clean separation: OpenClaw for conversational UX, n8n for reliable execution.
**Skills:** webhook
**Gotcha:** n8n webhooks need to be reachable from your OpenClaw host — same network or Tailscale. Use webhook authentication tokens to prevent unauthorized triggers. The agent should handle n8n errors gracefully: retry with backoff on 500s, alert you on persistent failures.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/n8n-workflow-orchestration.md

## Multi-channel personal assistant
**Trigger:** reactive | **Effort:** medium | **Value:** high
Unified assistant across Telegram, WhatsApp, email, Slack, and calendar. Whatever channel you're on, the agent is there. Routes tasks by channel type: quick questions via Telegram, detailed work via Slack, urgent items via WhatsApp. Maintains context across channels so you can start a conversation in Telegram and continue in Slack. Each channel has appropriate formatting and tone.
**Skills:** telegram, slack, gmail, calendar
**Gotcha:** The main challenge is context leakage — private Telegram conversations shouldn't surface in Slack groups. Set explicit boundaries in SOUL.md: 'in group channels, never reference private conversations.' Message length limits vary by platform — WhatsApp truncates in notifications, so lead with key info.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/multi-channel-assistant.md

## Personal CRM from email
**Trigger:** cron | **Effort:** medium | **Value:** high
Scans Gmail and Google Calendar to discover contacts, builds profiles with company, role, interaction history, and relationship health scores. Natural language queries: 'Who did I last talk to at Company X?' Filters noise (newsletters, cold pitches) automatically. Uses SQLite with vector embeddings for semantic search. Flags stale relationships that need reconnection. The initial inbox scan takes hours for large accounts; incremental updates after that.
**Skills:** gmail, calendar, crm
**Gotcha:** Quality of contact profiles depends on email content richness — 20 back-and-forth messages yield better profiles than a single introduction email. Give feedback on false positives ('that's a newsletter, not a real contact') so the agent learns your noise filters. Run the initial scan overnight.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/personal-crm.md

## Inbox declutter and newsletter digest
**Trigger:** cron | **Effort:** low | **Value:** high
Newsletter emails get automatically identified, summarized, and batched into a daily or weekly digest. Instead of 20 newsletters cluttering your inbox, you get one summary with links to articles you care about. Also handles promotional emails and receipts — each gets categorized, summarized, filed, or deleted based on your rules. One user reports eliminating the need to check email more than once daily.
**Skills:** gmail
**Gotcha:** Expect 5-10% false positives initially where important emails get categorized as newsletters. Review the agent's decisions for the first week and give feedback. Some newsletters have paywalled content the agent can't summarize from the email alone — those get 'paywalled article about X' with the link.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/inbox-declutter.md

## Health and symptom tracker
**Trigger:** cron | **Effort:** medium | **Value:** medium
Track food intake, symptoms, mood, and medications via chat check-ins 2-3x daily at natural meal times. The agent asks what you ate, how you feel, and logs everything. Over time it spots correlations: 'you report headaches after days with poor sleep' or 'mood improves when you exercise in the morning.' Weekly trend reports and on-demand queries. Useful for identifying food sensitivities or tracking chronic conditions.
**Skills:** telegram, oura
**Gotcha:** Schedule check-ins at meal times, not random intervals — too frequent and people stop responding. Correlation analysis is helpful but NOT medical advice. Export data in a format you can share with healthcare providers.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/health-symptom-tracker.md

## Todoist task transparency
**Trigger:** reactive | **Effort:** low | **Value:** medium
Sync agent work to Todoist tasks for visibility. When the agent works on something, it creates or updates a corresponding task. You see what the agent is doing without asking. You can redirect by editing tasks in Todoist. The agent checks periodically and adjusts its work based on your changes — change priority, add notes, or mark as blocked.
**Skills:** todoist
**Gotcha:** Only sync actionable items — agent-to-task noise overwhelms if you log every step. Use Todoist labels to distinguish agent-created vs. your own tasks. The agent should mark tasks complete but you should review before considering them done.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/todoist-task-manager.md

## Family calendar morning briefing
**Trigger:** cron | **Effort:** medium | **Value:** high
Aggregates multiple family members' calendars into a single morning briefing. Shows everyone's schedules, flags conflicts ('you have a meeting when you need to pick up the kids'), and notes logistics. Delivered to a shared family chat or individual DMs. Tracks household inventory and alerts on low supplies. Particularly valuable for families with complex schedules.
**Skills:** calendar, telegram
**Gotcha:** Privacy matters — not everyone wants their full calendar visible. Set boundaries: maybe kids see 'Mom has a work thing' not details. Calendar sync delays mean this is for planning, not time-critical coordination.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/family-calendar-household-assistant.md

## Multi-agent specialized team
**Trigger:** reactive | **Effort:** high | **Value:** high
Run specialized agents as a coordinated team: strategy agent plans, dev agent builds, marketing agent promotes, research agent investigates. Each has its own identity, skills, and workspace. The main agent delegates and consolidates. Lets a single person simulate a small team with specialized expertise.
**Skills:** telegram, coding-agent
**Gotcha:** Each specialist needs its own workspace directory and memory or they overwrite each other's context. The handoff format between agents is critical. Start with 2-3 agents — coordination overhead grows exponentially with team size.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/multi-agent-team.md

## Custom morning brief with AI recommendations
**Trigger:** cron | **Effort:** medium | **Value:** high
Daily briefing that goes beyond aggregation to include AI recommendations. Weather, calendar, tasks, news — plus: 'you have a 2-hour block this afternoon for deep work; your inbox has 3 urgent client emails; here's a 5-minute article on that topic you're learning.' Recommendations improve as the agent learns your patterns.
**Skills:** weather, gmail, todoist, telegram
**Gotcha:** Recommendations can feel intrusive if too frequent. 1-2 solid insights beats 10 mediocre ones. 'You have a meeting in 10 minutes' is useful; 'you should drink water' is annoying. Quality over quantity.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/custom-morning-brief.md

## Meeting notes to action items
**Trigger:** reactive | **Effort:** medium | **Value:** high
Feed meeting transcripts (Fathom, Otter) and the agent extracts structured summaries, your action items, others' commitments, and discussion topics. Your items go to your todo app; others' go to 'waiting on' with follow-up reminders. Can draft follow-up emails summarizing decisions for attendees.
**Skills:** granola-mcp, todoist, gmail
**Gotcha:** Speaker identification in transcripts is critical — without it, 'I'll do X' vs 'You'll do X' gets confused. Also: not every discussed item is an action item. The approval step is important for the first weeks while the agent calibrates.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/meeting-notes-action-items.md

## Habit tracker with accountability
**Trigger:** cron | **Effort:** low | **Value:** medium
Proactive daily check-ins that track habits, maintain streaks, and adapt tone based on engagement. Celebrates wins, gently notes when you're falling off, and suggests adjustments when you consistently miss. Tracks quantitative metrics or simple yes/no. Weekly trend summaries.
**Skills:** telegram
**Gotcha:** Tone calibration is critical — judgmental gets ignored, overly cheerful gets annoying. Use a '2 strikes' rule so occasional misses don't break streaks. Track 'days attempted' not just 'days succeeded.'
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/habit-tracker-accountability-coach.md

## Second brain with searchable memory
**Trigger:** reactive | **Effort:** medium | **Value:** high
Zero-friction capture: text anything to remember — ideas, links, quotes, decisions — and it's stored in a searchable local database with vector embeddings. Later, semantic search: 'what was that article about transformers?' finds it even if you used different words. No organization required upfront — just dump thoughts and the agent handles categorization and cross-referencing.
**Skills:** telegram, memory_search
**Gotcha:** Value kicks in after 2-3 weeks of consistent capture — you need critical mass before search becomes useful. Force yourself to text the agent every time you think 'I should remember this.' The activation energy of a message is lower than opening a note app.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/second-brain.md

## Event guest confirmation calls
**Trigger:** manual | **Effort:** high | **Value:** high
AI-powered phone calls to event guests: confirm attendance, collect dietary restrictions, answer common questions. Uses TTS/STT for natural conversation. Responses collected in structured format for export. Handles time zones and retries. Useful for weddings, conferences, or events with 50+ guests.
**Skills:** voice-wake-say, telegram
**Gotcha:** Only use phone for events where calling is expected (weddings, formal dinners). AI voice quality matters — cheap TTS annoys guests. Legal considerations for robocalls vary by jurisdiction; include opt-out.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/event-guest-confirmation.md

## Phone call notifications
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Convert critical agent alerts into actual phone calls via Twilio. For truly urgent items: server down, security breaches, time-sensitive opportunities. The agent calls your number, speaks the alert, and can take simple voice responses. Ensures you don't miss critical events even on silent.
**Skills:** voice-wake-say
**Gotcha:** Reserve for genuinely urgent events — 1-2 calls per week max or you'll start ignoring them. Twilio costs ~$0.02/min. Test voice quality over phone speakers; some TTS voices that sound good on headphones are muddy on phone audio.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/phone-call-notifications.md

## AI earnings tracker
**Trigger:** cron | **Effort:** medium | **Value:** medium
Track tech company earnings with automated alerts when reports drop, AI-generated summaries of key metrics (revenue, EPS, guidance vs. expectations), and management commentary highlights. Tracks trends: 'third quarter of declining AWS growth.' Delivered as same-day alerts for tracked companies or weekly digests.
**Skills:** web_search, telegram
**Gotcha:** Earnings data from free sources (company IR pages, SEC filings) has a few-hour delay vs. Bloomberg. The AI summary is for quick understanding — always read the primary source for investment decisions. Expect higher token usage during earnings season (Jan/Apr/Jul/Oct).
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/earnings-tracker.md

## Personal knowledge base with RAG
**Trigger:** reactive | **Effort:** medium | **Value:** high
Build a searchable knowledge base by dropping URLs, tweets, and articles into chat. The agent ingests content, extracts entities, chunks and embeds everything, and enables semantic search across all saved items. Different from bookmarks because you can query across content: 'what have I read about attention mechanisms?' Cross-references new content with existing knowledge.
**Skills:** memory_search, web_fetch
**Gotcha:** Ingestion quality varies — Twitter threads lose image context, paywalled articles only capture previews, PDFs need OCR. Review extracted content for important items. Semantic search works best for conceptual queries; use grep for exact string matches.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/knowledge-base-rag.md

## Pre-build idea validator
**Trigger:** manual | **Effort:** low | **Value:** high
Before building, the agent scans GitHub, HN, npm, PyPI, and App Store for similar solutions. Generates a market analysis: crowded (use existing), open opportunity (proceed), or emerging trend (consider timing). Checks for existing repos, recent activity, and community interest. Helps avoid building something that already exists in mature form.
**Skills:** web_search, github
**Gotcha:** The validation informs, not decides — markets support multiple players and sometimes you build for learning. Check dates on existing repos — dormant since 2019 might mean abandoned opportunity. Use this for landscape understanding, not binary build/don't-build.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/pre-build-idea-validator.md

## Spotify player control
**Trigger:** reactive | **Effort:** low | **Value:** medium
Control Spotify playback entirely from your chat app — play, pause, skip, queue songs, search for tracks, and manage playlists without opening the Spotify app. Particularly useful when your hands are full or you're in another workflow: 'play some jazz' or 'add this song to my workout playlist' or 'what's playing right now?' Uses the Spotify Web API with OAuth tokens. The agent can also build smart playlists based on your listening history and mood — 'make me a 2-hour focus playlist based on what I've been listening to.'
**Skills:** spotify-player
**Gotcha:** Spotify's OAuth token expires every hour and needs automatic refresh — make sure the skill handles token rotation or you'll get random failures mid-session. Also: Spotify API only controls playback on the currently active device, so if you switch from phone to desktop, the agent needs to know which device to target.
**Source:** https://clawhub.ai/skills/spotify-player

## Home Assistant integration
**Trigger:** reactive | **Effort:** medium | **Value:** high
Control your entire smart home through natural language via the Home Assistant REST API. Turn lights on/off, adjust thermostats, lock doors, check sensor readings, trigger automations — all from chat. 'Turn off the living room lights', 'set the thermostat to 21°C', 'is the garage door open?' The agent can also create complex conditional automations: 'when I say goodnight, turn off all lights, lock the front door, set the thermostat to 19°C, and arm the alarm.' Runs against your local Home Assistant instance, so no cloud dependency.
**Skills:** home-assistant
**Gotcha:** Use the Home Assistant long-lived access token (not the short-lived one) and configure the API URL as your local HA instance. Entity naming in Home Assistant is often cryptic (switch.living_room_light_2) — create a mapping file in TOOLS.md with friendly names so the agent knows 'living room lights' means entity 'switch.living_room_light_2'. Without this mapping, the agent will guess wrong entity names.
**Source:** https://clawhub.ai/skills/home-assistant

## Philips Hue thinking indicator
**Trigger:** reactive | **Effort:** low | **Value:** low
Flash or color-shift your Philips Hue lights while the agent is processing a request — a physical 'thinking' indicator that shows the agent is working. Lights return to their previous state when the response is ready. Surprisingly satisfying: you see the lights pulse, know the agent is churning, and get a visual cue when the response arrives. Also useful as a notification system: different colors for different alert types (blue for informational, red for urgent). Uses the OpenHue CLI for zero-config bridge discovery.
**Skills:** philips-hue-thinking, openhue
**Gotcha:** The Hue bridge needs to be on the same network as your OpenClaw host. First-time setup requires pressing the physical button on the bridge. Light names in the Hue app often don't match the API names — use 'openhue get lights' to find the actual names your agent should reference.
**Source:** https://clawhub.ai/skills/philips-hue-thinking

## Obsidian notes via CLI
**Trigger:** reactive | **Effort:** low | **Value:** high
Bridge your OpenClaw agent to your Obsidian knowledge vault. Read, search, create, and edit notes from chat while preserving Obsidian's wiki-link syntax and frontmatter. 'Find my notes about project X', 'create a new note in the Projects folder', 'add this to my daily note.' The agent understands Obsidian's folder structure, tags, and linking conventions, so new notes automatically get wikilinks to related existing notes. Useful for capturing ideas on-the-go via phone chat that appear in your Obsidian vault when you sit down at your desk.
**Skills:** obsidian-notesmd-cli
**Gotcha:** The vault must be on the same machine as OpenClaw (or synced via Obsidian Sync/iCloud). The agent reads markdown files directly, so it sees everything in the vault — don't point it at a vault containing sensitive credentials. Also: the agent should preserve existing frontmatter and not add its own metadata unless asked.
**Source:** https://clawhub.ai/skills/obsidian-notesmd-cli

## Notion as agent workspace
**Trigger:** reactive | **Effort:** medium | **Value:** high
Use Notion databases as structured storage for the agent — tasks, notes, contacts, project tracking, reading lists. The agent reads and writes to Notion via the API, so you get a visual dashboard of everything the agent is managing. Create a 'Tasks' database and the agent adds items as it identifies them from email, meetings, or conversation. Create a 'Contacts' database and the agent populates it from your CRM pipeline. The advantage over pure markdown files: Notion provides sorting, filtering, calendar views, and sharing that markdown can't.
**Skills:** notion
**Gotcha:** Notion API has a 3-requests-per-second rate limit that becomes a bottleneck for batch operations. The agent should batch updates rather than making individual API calls. Also: Notion blocks have a 2000-character limit per block, so long content needs to be split across multiple blocks. Share specific databases with the integration, not the entire workspace.
**Source:** https://clawhub.ai/skills/notion

## Todoist full task management
**Trigger:** reactive | **Effort:** low | **Value:** high
Full bidirectional Todoist integration: create tasks from conversation ('add buy groceries to my inbox'), query what's due today, complete tasks, add notes, set priorities, manage projects and labels. The agent can also do smart triage — look at your overdue tasks and suggest which to defer, delegate, or delete. Combined with email or meeting action items, the agent creates Todoist tasks automatically from commitments you make. Daily standup shows what's due today, what was completed yesterday, and what's overdue.
**Skills:** todoist
**Gotcha:** The Todoist API token gives full access to your account — there's no way to restrict it to specific projects. If security is a concern, use a separate Todoist account and share specific projects with your main account. The agent should never delete tasks without asking — mark them complete or archive them instead.
**Source:** https://clawhub.ai/skills/todoist

## Edge TTS voice responses
**Trigger:** reactive | **Effort:** low | **Value:** medium
Generate voice responses using Microsoft Edge TTS — completely free, high-quality, with 300+ voices in dozens of languages. When the user sends a voice message, the agent transcribes it (via Whisper) and replies with a voice note. Also useful for morning briefings, story time, and hands-free interaction. Edge TTS voices sound natural enough for casual conversation, though not as natural as ElevenLabs. Setup is just installing the edge-tts pip package — no API key needed.
**Skills:** edge-tts
**Gotcha:** Edge TTS requires an internet connection (it uses Microsoft's servers) despite being free. For fully offline voice, use Kokoro instead. The voice quality varies significantly between voices — test 5-10 before picking one. Jenny and Guy are popular English voices. Output is typically WAV which needs conversion to OGG/Opus for Telegram: 'ffmpeg -y -i in.wav -c:a libopus -b:a 128k out.ogg'.
**Source:** https://clawhub.ai/skills/edge-tts

## Kokoro local TTS
**Trigger:** reactive | **Effort:** low | **Value:** medium
Generate speech entirely locally using the Kokoro 82M model — zero API cost, ~6x realtime speed on Apple Silicon, and no internet connection required. Produces natural-sounding speech in multiple voices (af_heart, af_bella, am_adam, etc.) at 24kHz quality. Ideal for voice responses in chat, morning briefings, audiobook-style content delivery, or any use case where you want voice without sending your text to a cloud API. Runs via Python 3.12 with the kokoro pip package.
**Skills:** kokoro-tts
**Gotcha:** Requires Python 3.12 specifically — Kokoro's misaki[en] dependency doesn't work on Python 3.13+. Also needs espeak-ng installed (brew install espeak-ng). First run downloads the model (~200MB). The af_heart voice is the most natural-sounding for English. Output is 24kHz WAV — convert to OGG/Opus for Telegram delivery.
**Source:** https://clawhub.ai/skills/kokoro-tts

## Whisper speech-to-text
**Trigger:** reactive | **Effort:** low | **Value:** high
Transcribe audio messages locally using MLX Whisper (Apple Silicon optimized) or OpenAI Whisper API. When someone sends a voice message in Telegram or WhatsApp, the agent automatically transcribes it and processes the text content. This enables full voice conversations: user speaks → Whisper transcribes → agent processes → responds with text or TTS audio. MLX Whisper runs entirely on-device with no API cost; the large-v3-turbo model gives near-perfect English transcription in real-time on M1+ Macs.
**Skills:** openai-whisper
**Gotcha:** MLX Whisper is Apple Silicon only — on Linux, use faster-whisper or the OpenAI API. Audio format matters: Whisper works best with 16kHz mono WAV. Telegram voice messages are OGG/Opus, WhatsApp uses M4A — both need ffmpeg conversion before transcription. For non-English languages, specify the language parameter or transcription quality drops significantly.
**Source:** https://clawhub.ai/skills/openai-whisper

## RSS AI reader
**Trigger:** cron | **Effort:** low | **Value:** medium
Monitor any number of RSS feeds and generate AI-summarized digests. The agent checks your feeds on a cron schedule (hourly, daily, etc.), filters articles by relevance to your interests, extracts key points from each article, and delivers a clean summary. No more opening 50 tabs — you get a curated 5-minute read covering everything that matters. Supports scoring by topic relevance, so articles about your specific niche rank higher than general tech news. Can cross-reference new articles with your knowledge base to highlight things that connect to your ongoing projects.
**Skills:** rss-ai-reader
**Gotcha:** Start with 5-10 high-quality feeds, not 50. Too many feeds overwhelms the summarizer and every digest becomes 'here are 30 articles, most of which you don't care about.' The relevance filter needs explicit tuning: tell the agent exactly which topics matter and which to skip. RSS is still the most reliable content ingestion format — more consistent than web scraping.
**Source:** https://clawhub.ai/skills/rss-ai-reader

## OpenClaw backup automation
**Trigger:** cron | **Effort:** low | **Value:** high
Automated backup of your entire OpenClaw setup: workspace files (SOUL.md, MEMORY.md, daily notes), credentials directory, cron job configurations, skill installations, and memory files. Supports git (push to a private repo), rsync (to a NAS or secondary machine), or cloud storage (S3, Backblaze B2). Runs as a daily cron job and notifies you if a backup fails. Critical because OpenClaw's memory and configuration represent weeks of accumulated context that's painful to recreate from scratch.
**Skills:** openclaw-backup
**Gotcha:** Exclude the credentials directory from git-based backups (or use git-crypt) — you don't want API keys in a repo, even a private one. For the memory directory, incremental backups work well since daily notes only append. Test your restore process before you need it — a backup you've never restored from isn't really a backup.
**Source:** https://clawhub.ai/skills/openclaw-backup

## Docker container management
**Trigger:** reactive | **Effort:** medium | **Value:** high
Manage Docker containers from chat: list running containers, start/stop/restart services, view logs, and even deploy new containers from compose files. 'Is my Postgres container running?', 'restart the nginx container', 'show me the last 50 lines of logs from the API server.' Particularly useful for homelab management when you're away from your desk — quick triage of container issues via phone chat instead of SSH-ing into the server. The agent can also monitor container health and alert you when something crashes.
**Skills:** docker-essentials
**Gotcha:** The agent needs Docker socket access, which is a significant security surface. Consider running a restricted Docker context that only allows specific operations (restart, logs) but not privileged operations (run with --privileged, mount host volumes). Never give the agent access to docker exec on production containers — it could accidentally corrupt data.
**Source:** https://clawhub.ai/skills/docker-essentials

## Screenshot capture and analysis
**Trigger:** manual | **Effort:** low | **Value:** medium
Take screenshots of web pages or your local screen and have the agent analyze the visual content. Use cases: 'take a screenshot of my dashboard and tell me if anything looks wrong', 'screenshot competitor's pricing page and compare to ours', 'capture the error dialog and help me fix it.' The agent uses vision models to understand UI layouts, read text from images, identify visual anomalies, and compare screenshots over time. Combined with cron, this enables visual monitoring: 'screenshot the server dashboard every hour and alert me if any graphs show anomalies.'
**Skills:** screenshot
**Gotcha:** Vision model calls are expensive (~1500 tokens per image) — don't screenshot on every heartbeat. Use targeted captures: cron for known monitoring dashboards, reactive for one-off analysis. Also: screenshots of password-protected pages require the browser to be logged in. Use Chrome Relay mode to leverage your existing browser session rather than trying to automate login flows.
**Source:** https://clawhub.ai/skills/screenshot

## Crypto market data monitoring
**Trigger:** cron | **Effort:** low | **Value:** medium
Track cryptocurrency prices, market caps, volume, and trends without needing any API key — uses free public endpoints from CoinGecko, CoinMarketCap, or similar. Set up alerts for price movements ('tell me if ETH drops below $3000'), daily portfolio summaries, and trend analysis. The agent can also monitor on-chain metrics, DeFi yields, and whale transactions if configured with additional data sources. Delivered via scheduled reports or real-time alerts to Telegram.
**Skills:** crypto-market-data
**Gotcha:** Free API tiers have strict rate limits (CoinGecko: 10-30 calls/minute). Cache responses aggressively — crypto prices don't need sub-minute updates for most use cases. The agent should batch all price checks into a single API call rather than making separate calls per coin. Also: never give the agent access to execute trades or transfer funds.
**Source:** https://clawhub.ai/skills/crypto-market-data

## Stock analysis dashboard
**Trigger:** manual | **Effort:** medium | **Value:** medium
Analyze stocks with fundamental data (P/E ratio, revenue growth, margins), technical indicators (RSI, moving averages, MACD), and news sentiment. The agent pulls data from free APIs (Yahoo Finance, Alpha Vantage free tier) and generates a comprehensive analysis when you ask: 'analyze AAPL' or 'compare MSFT and GOOG.' Can also monitor a watchlist and alert you on significant events: earnings beats/misses, unusual volume, or price breaking key support/resistance levels. No trading — just research and monitoring.
**Skills:** stock-analysis
**Gotcha:** Free stock data APIs have significant delays (15-20 minutes) and limited historical data. For real-time prices, you'd need a paid data feed. The agent's analysis is based on publicly available information and historical patterns — it's not financial advice and shouldn't be used for trading decisions. News sentiment analysis is useful for context but often lags behind price movement.
**Source:** https://clawhub.ai/skills/stock-analysis

## Smart model switching
**Trigger:** reactive | **Effort:** medium | **Value:** high
Automatically route requests to different LLM models based on task complexity and type, instead of using one expensive model for everything. Simple factual questions → Haiku (fast, cheap). Complex reasoning → Opus (slow, expensive). Coding tasks → Codex (specialized). Image analysis → vision models. The agent detects the task type from your message and routes accordingly, saving 60-80% on API costs while maintaining quality where it matters. You can also set manual overrides: 'use Opus for this next response' when you know you need maximum reasoning power.
**Skills:** smart-model-switching
**Gotcha:** The automatic detection isn't perfect — sometimes the agent routes a complex task to a cheap model and gives a mediocre answer. Set up a feedback loop: if the response is bad, say 'retry with Opus' and the agent learns which task types need more capable models. The biggest savings come from routing heartbeat/cron tasks to Haiku — those fire dozens of times per day and don't need Opus.
**Source:** https://clawhub.ai/skills/smart-model-switching

## GitHub assistant for issues and PRs
**Trigger:** reactive | **Effort:** low | **Value:** high
Manage GitHub repos from chat: create issues, review PRs with AI summaries, check CI status, comment on discussions, triage bugs. Analyzes your issue backlog, identifies stale issues, suggests labels, drafts responses. For open source maintainers: 'show me bugs not updated in 30 days' or 'summarize PR #247.'
**Skills:** github, openclaw-github-assistant
**Gotcha:** GitHub API has aggressive rate limits for search. Cache issue data locally and refresh periodically rather than querying live. Never give the agent permission to merge PRs or push to main without your approval.
**Source:** https://clawhub.ai/skills/openclaw-github-assistant

## Security auditor for agent setup
**Trigger:** manual | **Effort:** low | **Value:** high
Audit your OpenClaw installation for security vulnerabilities: checks for exposed API keys in workspace files, overly permissive exec tool configuration, unencrypted credential storage, open network ports, and common misconfigurations. Generates a prioritized report with specific remediation steps. Run on initial setup and after every major configuration change. The audit also checks for prompt injection risks in files that external data could modify, and verifies that RLS policies are properly set on any databases the agent accesses.
**Skills:** security-auditor
**Gotcha:** The audit catches the obvious stuff but can't assess your specific threat model. The biggest risks it won't catch: social engineering attacks via group chats where people try to manipulate the agent, and data leakage through the agent referencing private context in semi-public channels. Run the audit as a cron job monthly to catch configuration drift.
**Source:** https://clawhub.ai/skills/security-auditor

## Apple Calendar operations
**Trigger:** reactive | **Effort:** low | **Value:** medium
Read, create, and manage Apple Calendar events directly on macOS without any cloud API. Uses AppleScript or the 'ical' CLI to interact with the local Calendar database. 'What's on my calendar today?', 'create an event for lunch with Sarah tomorrow at noon', 'move my 3pm meeting to 4pm.' Supports multiple calendars (personal, work, family), recurring events, and time zone handling. Works offline since it reads the local Calendar store directly.
**Skills:** apple-calendar-ops
**Gotcha:** AppleScript calendar commands require specific privacy permissions (System Settings → Privacy → Automation). The agent needs to be running on the same Mac as the Calendar app. For Google Calendar sync, events created locally will sync to Google if you have the Google account added in Calendar settings. iCloud sync can have 5-10 minute delays.
**Source:** https://clawhub.ai/skills/apple-calendar-ops

## Telegram voice transcription
**Trigger:** reactive | **Effort:** low | **Value:** high
Automatically transcribe voice messages received on Telegram using Whisper, then process the transcribed text as a normal message. The agent receives a voice message, downloads the audio file, runs Whisper transcription (locally via MLX or via API), and responds to the content as if you'd typed it. This enables completely hands-free interaction: record a voice note while walking, driving, or cooking, and the agent handles it like text. Combined with TTS for responses, you get full voice conversations through Telegram.
**Skills:** tg-voice-whisper, openai-whisper
**Gotcha:** Telegram voice messages are in OGG/Opus format — Whisper expects WAV, so you need ffmpeg for conversion. The transcription step adds 2-5 seconds of latency before the agent can start processing. For languages other than English, specify the language in the Whisper call or quality drops. Keep voice messages under 2 minutes for reliable transcription.
**Source:** https://clawhub.ai/skills/tg-voice-whisper

## Daily meal planner from preferences
**Trigger:** cron | **Effort:** medium | **Value:** medium
Generate meal plans based on dietary preferences, restrictions, and what's in season. Learns which meals you actually cook vs. save. Can generate shopping lists by store section or integrate with grocery delivery APIs. Handles dietary goals: 'high protein, low carb this week' or 'vegetarian under 30 minutes.'
**Skills:** web_search
**Gotcha:** Plans need to be realistic for your cooking skill and time. 'Coq au vin on a Tuesday' is unrealistic for most people. Grocery delivery integration is the biggest time-saver; without it you're still manually creating shopping lists.
**Source:** https://www.reddit.com/r/openclaw/comments/1rrpdtb/

## Nightly memory consolidation
**Trigger:** cron | **Effort:** low | **Value:** high
Every night the agent reviews the day's interactions, extracts key learnings and decisions, consolidates into long-term memory, removes duplicates, updates outdated preferences, and flags contradictions: 'you said you prefer X last week but said Y today — which is correct?' Keeps memory compact and accurate rather than growing infinitely.
**Skills:** general
**Gotcha:** Schedule for off-peak hours (3am) and set a cost cap. Be conservative about consolidation — some raw daily notes are worth keeping. You should be able to review changes and revert if something was incorrectly merged.
**Source:** https://www.reddit.com/r/LocalLLaMA/comments/1r3ro5h/

## Isolated research sessions
**Trigger:** reactive | **Effort:** low | **Value:** high
For deep research, the agent spawns a temporary session that doesn't pollute your main context. The research agent burns tokens, follows rabbit holes, explores dead ends — all disposable. Only the clean summary survives. Useful for market research, competitive analysis, learning new topics, or investigating technical problems.
**Skills:** coding-agent
**Gotcha:** The isolation is the point — messy research process gets discarded, clean results survive. Set time (30-60 min) and cost caps to prevent runaway usage. Important discoveries should be explicitly saved to main memory.
**Source:** https://www.reddit.com/r/LocalLLaMA/comments/1r3ro5h/

## Podcast production pipeline
**Trigger:** manual | **Effort:** high | **Value:** high
End-to-end podcast automation: guest research (LinkedIn, Twitter, past interviews), outline generation, recording day reminders, editing markers (detecting filler words, long pauses), show notes with timestamps, and social media clips. Tracks episodes through production stages on a kanban board.
**Skills:** web_search, notion
**Gotcha:** Automated editing detection (um/ah) is easy; knowing which pauses are dramatic vs. unnecessary requires human judgment. Mark suggested edits, don't make them. Guest research is the highest-value automation, saving 30-60 minutes per episode.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/podcast-production-pipeline.md

## Market research and MVP factory
**Trigger:** manual | **Effort:** high | **Value:** high
Mine Reddit and X for real pain points — not just complaints but 'I wish someone would build X' signals. Validate demand by checking for existing solutions on GitHub, Product Hunt, App Store. Build quick MVPs of the most promising ideas. The agent spots patterns: '5 people in r/smallbusiness complained about the same problem this week.'
**Skills:** web_search, browser, coding-agent
**Gotcha:** Filter for genuine pain points vs. casual complaints. 'This app is annoying' is noise. 'I've tried 5 tools and they all fail at Y' is signal. The 30-day window is important — too short misses patterns, too long gets outdated. MVPs should be throwaway prototypes for validation, not production code.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/market-research-product-factory.md

## arXiv paper reader
**Trigger:** reactive | **Effort:** low | **Value:** high
Fetch arXiv papers by ID or URL, extract structured summaries (abstract, methodology, results, conclusions), and answer questions about specific sections. Compare papers, monitor for new publications in your research areas, and send weekly digests. 'How does this approach differ from the one we read last week?' Search your paper library semantically.
**Skills:** pdf, web_fetch
**Gotcha:** Specify which sections matter — 'just abstract and results' vs 'full methodology' — to control token costs. The agent summarizes well but can misinterpret mathematical notation. Use for triage and discovery; read originals for critical research.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/arxiv-paper-reader.md

## OpenRouter token management
**Trigger:** cron | **Effort:** low | **Value:** medium
Monitor your OpenRouter API usage, costs, and rate limits from chat. The agent tracks spending per model, alerts on unusual cost spikes, and can auto-switch to cheaper models when approaching budget limits. Useful for anyone running multiple agents or expensive autonomous tasks where costs can spiral unexpectedly.
**Skills:** general
**Gotcha:** Set daily and monthly budget alerts — costs can spike dramatically during autonomous overnight tasks. The agent should proactively suggest cheaper model alternatives when a task doesn't need the most expensive model.
**Source:** https://www.reddit.com/r/ThinkingDeeplyAI/comments/1qsoq4h/

## LaTeX paper writing assistant
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Write academic papers conversationally in LaTeX with instant PDF preview. Describe sections in plain English, the agent generates LaTeX, compiles, shows PDF. Handles bibliography, figure placement, and formatting requirements. Useful for collaborative papers where not all authors know LaTeX.
**Skills:** pdf, coding-agent
**Gotcha:** The agent handles simple text-to-LaTeX well but struggles with complex equations — write those directly. Modularize into separate .tex files per section. Compilation errors are cryptic — the agent should catch common issues before showing the PDF.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/latex-paper-writing.md

## Autonomous game dev pipeline
**Trigger:** cron | **Effort:** high | **Value:** medium
Full lifecycle game development with agent as project lead. Concept generation, prototyping in Godot/Unity, asset coordination, playtesting feedback integration, and release planning. Uses git for version control with incremental commits. Can generate simple 2D games autonomously or collaborate on complex projects.
**Skills:** coding-agent, github
**Gotcha:** Start simple — 2D prototypes, not AAA titles. The agent handles mechanics and code but struggles with game design (what's fun?). Human oversight on design decisions is essential. Asset creation usually needs external tools; the agent can coordinate but not generate quality art/sound.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/autonomous-game-dev-pipeline.md

## Semantic memory search upgrade
**Trigger:** reactive | **Effort:** medium | **Value:** high
Add vector-powered semantic search to existing markdown memory files. Instead of keyword matching, the agent understands query meaning: 'what did I decide about hiring?' finds relevant memories even without the word 'decision.' Uses lightweight local embeddings (384 dimensions) that run fast on consumer hardware.
**Skills:** memory_search
**Gotcha:** Semantic search is slower than grep for exact matches — use it for conceptual queries, grep for exact strings. Rebuild the vector index monthly as memory grows. Semantic search can surface false positives; always show the source memory for verification.
**Source:** https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/semantic-memory-search.md

## Oura Ring analytics dashboard
**Trigger:** cron | **Effort:** low | **Value:** medium
Pull Oura Ring data (sleep score, readiness, activity, HRV, stress, SpO2) and generate visual analytics dashboards or text summaries. The agent can correlate your biometrics with your behavior: 'you slept poorly after days with more than 3 meetings' or 'your HRV is highest on days you exercise in the morning.' Combine with daily journaling data for a complete picture of how your habits affect your health. Delivered as morning health briefings or weekly trend reports. Can also make suggestions: 'your readiness is low today — consider lighter meetings.'
**Skills:** oura-analytics, oura
**Gotcha:** Oura API returns data with a 1-day delay for most metrics, so 'today's' data is actually yesterday's. Build this into your briefing timing — morning reports cover yesterday's sleep and activity. Don't over-interpret daily fluctuations; the value is in weekly/monthly trends. HRV in particular varies wildly day-to-day and only becomes meaningful as a 7-day rolling average.
**Source:** https://clawhub.ai/skills/oura-analytics

## Gmail secretary
**Trigger:** cron | **Effort:** medium | **Value:** high
Automated email triage that runs every 30 minutes: categorize incoming emails (urgent, needs response, FYI, newsletter, spam), prioritize by sender importance and content urgency, draft replies for emails that need them, and flag truly urgent items for immediate Telegram notification. Over time, the agent learns your response patterns — which senders always get quick replies, which types of emails can wait until Monday, which newsletters you actually read. Draft replies go to an approval queue so you can edit/send/discard. One user reports this eliminated the need to check email more than once per day.
**Skills:** gmail-secretary, gmail
**Gotcha:** The urgency calibration takes 1-2 weeks of feedback. Initially the agent will flag too many things as urgent. Consistently tell it 'that could have waited' until it learns your threshold. The email drafts need the humanizer treatment or recipients will notice a sudden change in your writing style. Never give the agent send permission — always approve drafts manually.
**Source:** https://clawhub.ai/skills/gmail-secretary

## Sleep tracker analysis
**Trigger:** cron | **Effort:** low | **Value:** medium
Track and analyze sleep patterns by combining data from wearables (Oura, Apple Watch, etc.) with self-reported factors: caffeine intake, screen time, exercise, stress. The agent correlates behaviors with sleep quality over time, identifying patterns: 'you sleep 20% worse on days with coffee after 2pm' or 'your deep sleep increases when you exercise in the morning.' Delivers weekly sleep reports with specific, actionable recommendations based on your actual data rather than generic sleep hygiene advice.
**Skills:** sleep-tracker, oura
**Gotcha:** Wearable sleep data is directionally accurate but not clinically precise — don't treat it as medical fact. The self-reported factors are as important as the wearable data; the agent needs both to find meaningful correlations. Also: sleep quality has high day-to-day variance — look for patterns over weeks, not individual bad nights.
**Source:** https://clawhub.ai/skills/sleep-tracker

## Daily journaling with prompts
**Trigger:** cron | **Effort:** low | **Value:** medium
Guided daily journaling delivered via chat at a consistent time. The agent asks reflection questions — not generic 'how was your day?' but contextual questions based on what it knows you're working on: 'You mentioned feeling overwhelmed about the product launch yesterday. How are you feeling about it today?' Responses are captured as daily memory entries and distilled over time into long-term patterns. The agent tracks your mood, energy, and focus trends across weeks and can surface insights: 'you tend to feel most productive on Tuesdays' or 'your mood drops when you have more than 3 meetings in a day.'
**Skills:** daily-journal
**Gotcha:** The questions need to rotate and adapt — the same 5 questions every day gets boring fast and people stop responding. Use a question bank of 20+ prompts and cycle through them, weighted by what's relevant to your current context. Also: journaling compliance drops if the timing is wrong. Let the agent learn when you're most likely to respond (after morning coffee? before bed?) rather than forcing a fixed time.
**Source:** https://clawhub.ai/skills/daily-journal

## Reminder with smart scheduling
**Trigger:** reactive | **Effort:** low | **Value:** high
Set reminders with natural language that understands context: 'remind me to call the dentist next Tuesday at 2pm', 'remind me about the project deadline in 3 days', 'remind me to buy milk when I get home' (location-based, if supported). The agent can also create smart recurring reminders that adapt: 'remind me to water the plants every 3 days, but skip if it rained.' Reminders integrate with your calendar to avoid conflicts and can escalate: a gentle ping first, then a more insistent reminder if you haven't acknowledged it.
**Skills:** reminder
**Gotcha:** The agent needs a reliable cron system for timed reminders — if your OpenClaw instance restarts, pending reminders need to persist (stored in a file or database, not just in-memory). Natural language parsing of dates is usually good but occasionally wrong for ambiguous phrases like 'next Friday' vs 'this Friday' — confirm the date back to the user.
**Source:** https://clawhub.ai/skills/reminder

## News summary digest
**Trigger:** cron | **Effort:** low | **Value:** medium
Daily curated news summary from multiple sources (RSS, web search, social media), filtered by your specific interests and delivered at your preferred time. Not a generic news feed — the agent learns which topics you actually read (vs. skip), which sources you trust, and what level of detail you want. Each item gets a 1-2 sentence summary with the source link. Typical delivery: 5-10 items covering your niche, taking 3-5 minutes to read. Can also flag breaking news outside the regular schedule if something significant happens in your tracked topics.
**Skills:** news-summary, web_search
**Gotcha:** The relevance filter is everything — without it, you get 30 items and stop reading after the first 5. Tell the agent explicit interests AND explicit exclusions ('interested in AI model releases, NOT interested in AI ethics debates'). Cap the digest at 10 items maximum. If you're consistently skipping items, that's a signal to tighten the filter.
**Source:** https://clawhub.ai/skills/news-summary

## Browser automation with Stagehand
**Trigger:** reactive | **Effort:** medium | **Value:** high
Automate complex web interactions that go beyond simple page fetching: fill multi-step forms, click through wizard flows, handle JavaScript-heavy SPAs, deal with authentication, and extract data from dynamic pages. Uses Stagehand (or Playwright) for reliable browser control with element targeting via aria refs. The agent can navigate sites like a human — handling dropdowns, modals, pagination, and conditional UI. Useful for automating interactions with sites that have no API: legacy dashboards, government portals, booking systems.
**Skills:** agent-browser-clawdbot, browser-automation
**Gotcha:** Browser automation is inherently fragile — any site redesign breaks the workflow. Use aria ref targeting (more stable than CSS selectors) and build in screenshot verification at key steps so the agent can detect when a page has changed. Sites with anti-bot measures (CAPTCHA, rate limiting) need special handling — consider using your real Chrome session via the Chrome Relay extension for sites where you're already logged in.
**Source:** https://clawhub.ai/skills/agent-browser-clawdbot

## macOS local voice assistant
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Local voice input/output on macOS using Whisper for speech-to-text and Kokoro (or system TTS) for text-to-speech. Works entirely offline with no cloud API calls. You speak into your mic, Whisper transcribes locally, the agent processes, and Kokoro speaks the response. Latency is surprisingly good on Apple Silicon: ~1 second for transcription + ~1 second for TTS generation. Can be triggered via a keyboard shortcut or a wake word if configured. Turns your Mac into a true voice assistant that's smarter than Siri.
**Skills:** macos-local-voice, openai-whisper, kokoro-tts
**Gotcha:** Requires Python 3.12 (for Kokoro compatibility), espeak-ng, and ffmpeg — all installable via brew. The MLX Whisper model needs ~500MB of storage. For best voice quality, use the af_heart Kokoro voice. System audio input needs microphone permissions granted in System Settings. Background noise significantly degrades Whisper accuracy — use in a quiet environment or add a noise gate.
**Source:** https://clawhub.ai/skills/macos-local-voice

## WhatsApp message styling
**Trigger:** reactive | **Effort:** low | **Value:** low
Auto-format agent messages for WhatsApp's limited formatting: no markdown tables (use bullet lists instead), no headers (use bold or CAPS for emphasis), no code blocks with syntax highlighting (use monospace for short snippets). The agent learns WhatsApp's constraints and adapts its output format automatically. Also handles emoji usage, message length limits (keep important info in the first few lines since WhatsApp truncates long messages in notifications), and link formatting (no need for markdown link syntax).
**Skills:** whatsapp-styling-guide
**Gotcha:** WhatsApp formatting uses different syntax than markdown: *bold*, _italic_, ~strikethrough~, ```monospace```. The agent needs to know it's in a WhatsApp context to format correctly — this is typically handled by the channel detection in OpenClaw config. The biggest annoyance: WhatsApp notifications only show the first ~200 characters, so lead with the most important information.
**Source:** https://clawhub.ai/skills/whatsapp-styling-guide

## TTS audio replies for WhatsApp
**Trigger:** reactive | **Effort:** low | **Value:** medium
Convert text agent replies to voice messages for WhatsApp. When the user sends audio, the agent transcribes via Whisper, processes the request, and replies with a voice note instead of text. Particularly useful for hands-free interaction while driving, cooking, or when you just prefer voice. The voice can be customized (Kokoro for local, ElevenLabs for premium quality, Edge TTS for free). WhatsApp voice messages have a personal, intimate feel that text lacks.
**Skills:** tts-whatsapp, edge-tts
**Gotcha:** Voice messages work best for short responses — under 30 seconds. Longer messages get tedious to listen to. Also: WhatsApp displays voice messages prominently in notifications, but the transcription quality in notifications is poor. Lead with the most important information. Test that your chosen TTS voice sounds good through phone speakers; some voices that sound fine on headphones are muddy on phone audio.
**Source:** https://clawhub.ai/skills/tts-whatsapp

## Google Calendar via gcalcli
**Trigger:** reactive | **Effort:** low | **Value:** high
Read and manage Google Calendar events using the gcalcli command-line tool. Supports multiple calendars, recurring events, natural language date parsing, and agenda views. 'What's my week look like?', 'add a meeting with the team next Thursday at 2pm for 1 hour.' The agent can also check availability across calendars for scheduling: 'when am I free next week for a 30-minute call?' Requires a Google Cloud project with Calendar API enabled and OAuth credentials.
**Skills:** gcalcli-calendar
**Gotcha:** Setting up Google Cloud OAuth is the most painful part — Google's Cloud Console UI is notoriously bad. Have the agent walk you through the setup step by step. gcalcli stores credentials in ~/.gcalcli_oauth, which should be in your OpenClaw credentials directory, not the workspace. The first auth requires a browser-based OAuth flow that needs manual interaction.
**Source:** https://clawhub.ai/skills/gcalcli-calendar

## Git essentials for agents
**Trigger:** reactive | **Effort:** low | **Value:** high
Enable the agent to manage git repositories: commit changes, push to remotes, create branches, merge, check status, view diffs, and manage pull requests. Essential for any agent that modifies code or configuration files — it should be committing its own changes, not leaving uncommitted modifications in your workspace. The agent can also review recent commits, explain what changed, and revert problematic changes. Useful pattern: the agent commits after every significant change with a descriptive message, making it easy to see what it did and roll back if needed.
**Skills:** git-essentials
**Gotcha:** Set up SSH keys for the agent's git access rather than HTTPS with passwords. The agent should commit to branches (not main) and create PRs for review unless you explicitly tell it to push to main. Configure git user.name and user.email for the agent so its commits are distinguishable from yours in the log.
**Source:** https://clawhub.ai/skills/git-essentials

## Translate any text
**Trigger:** reactive | **Effort:** low | **Value:** medium
Translate text between languages using multiple backends: Google Translate (free, good for quick translations), DeepL (paid, higher quality for European languages), or local models (fully private, no API costs). The agent auto-detects the source language and translates to your preferred language. Useful for: translating emails from foreign contacts, understanding research papers in other languages, preparing multilingual content, and communicating with international collaborators. Can also do contextual translation — 'translate this email but make it sound professional in German.'
**Skills:** translate
**Gotcha:** Free Google Translate has rate limits and sometimes produces awkward translations for specialized vocabulary. DeepL is significantly better for business/technical content in European languages but costs money. For privacy-sensitive content (contracts, personal messages), use a local translation model to avoid sending text to cloud APIs.
**Source:** https://clawhub.ai/skills/translate

## PDF extraction and analysis
**Trigger:** reactive | **Effort:** low | **Value:** high
Extract text, tables, and images from PDFs and analyze them conversationally. Drop a PDF into chat and ask: 'summarize this contract', 'what are the payment terms?', 'extract all dates and deadlines into a table.' Handles scanned PDFs via OCR, multi-page documents, and complex layouts with tables and figures. Useful for processing invoices, analyzing research papers, reviewing contracts, and extracting data from reports. Can compare multiple PDFs: 'how does this year's annual report differ from last year's?' and do cross-document analysis.
**Skills:** pdf, pdf-extract
**Gotcha:** OCR quality varies dramatically — clean, well-formatted PDFs extract perfectly, while scanned handwritten documents produce garbage. Always verify extracted numbers (especially financial figures). For large PDFs (100+ pages), specify page ranges to avoid burning tokens on irrelevant sections. Tables in PDFs are the hardest to extract reliably — consider using a dedicated table extraction tool if accuracy matters.
**Source:** https://clawhub.ai/skills/pdf

## Camera capture and monitoring
**Trigger:** cron | **Effort:** medium | **Value:** medium
Capture images from connected cameras (USB webcams, IP cameras, Raspberry Pi cameras) and have the agent analyze them. Use cases: security monitoring ('alert me if someone is at the front door'), plant health checks ('how do my tomatoes look today?'), pet monitoring ('is the dog on the couch?'), and timelapse documentation. The agent can run captures on a cron schedule and only alert you when something interesting is detected, reducing notification noise. Also works with screenshots of your desktop for UI monitoring.
**Skills:** camera
**Gotcha:** Image analysis costs more tokens than text — a single image is ~1500 tokens. Don't capture every minute; use motion detection or hourly checks for most monitoring use cases. IP camera URLs often use RTSP protocol which needs ffmpeg to capture a still frame. Store camera names and URLs in TOOLS.md so the agent knows 'front door camera' means rtsp://192.168.1.50:554/stream1.
**Source:** https://clawhub.ai/skills/camera

## File organization by content
**Trigger:** cron | **Effort:** medium | **Value:** medium
Point the agent at a directory (like Downloads) and it analyzes each file's content, then sorts them into organized folders: invoices → Finance, screenshots → Screenshots, code files → Projects/[repo-name], documents → Documents/[topic]. Uses file content analysis, not just extensions — a PDF invoice gets filed differently from a PDF research paper. Can run as a cron job to keep directories clean automatically, or on-demand when you want to organize accumulated clutter.
**Skills:** file-organizer-zh
**Gotcha:** Start with a DRY RUN that shows proposed moves before actually executing them. The agent will occasionally misclassify files — an invoice from a tech company might end up in 'Tech' instead of 'Finance.' Give it explicit rules for edge cases. Also: never let it organize your git repositories or application support directories.
**Source:** https://clawhub.ai/skills/file-organizer-zh

## Obsidian sync across devices
**Trigger:** cron | **Effort:** medium | **Value:** medium
Sync Obsidian vault changes across multiple devices without paying for Obsidian Sync. The agent monitors your vault for changes, commits them to a private git repo, and pulls updates from other devices. Handles conflicts intelligently: if the same file was edited on two devices, the agent shows you both versions and asks which to keep. Works on any device that can run git — Mac, Windows, Linux, iOS (via Working Copy), Android (via Termux).
**Skills:** obsidian-sync, git-essentials
**Gotcha:** Git isn't ideal for binary files (images, PDFs) — large attachments will bloat the repo. Consider using git-lfs or excluding attachments from sync. Also: Obsidian plugins and settings don't sync via this method — only your notes. For plugin/settings sync, you still need Obsidian Sync or manual configuration on each device.
**Source:** https://clawhub.ai/skills/obsidian-sync

## Claw workspace sync
**Trigger:** cron | **Effort:** low | **Value:** medium
Sync your entire OpenClaw workspace (skills, memory files, cron configs, custom scripts) across multiple machines. The agent commits changes to a private repo and pulls updates on other devices. Ensures your agent behaves identically whether you're on your laptop, desktop, or server. Particularly useful if you run OpenClaw on a home server but want the same configuration when traveling with a laptop.
**Skills:** claw-sync
**Gotcha:** Never sync the credentials directory — API keys should stay local to each machine. Also: some skills have machine-specific paths or dependencies that break on other devices. Test synced configurations on each target machine. The sync should exclude large files (transcripts, log files) that would bloat the repo.
**Source:** https://clawhub.ai/skills/claw-sync

## 3-job morning stack: brief + inbox + receipts
**Trigger:** cron | **Effort:** medium | **Value:** high
A consolidated morning routine that runs three cron jobs in sequence: (1) morning brief with weather, calendar, and priorities; (2) inbox scan for urgent emails needing immediate attention; (3) receipt processing from photos taken the previous day. The agent delivers a single summary message covering all three areas rather than three separate notifications. Takes 5 minutes to read and gives you a complete picture of your day plus any action items that can't wait.
**Skills:** gmail, weather, calendar
**Gotcha:** The sequencing matters — inbox scan should happen after the brief so the agent knows your schedule context when prioritizing emails. Receipt processing can happen async since it doesn't need your immediate attention. If any job fails, the others should still run and report partial results.
**Source:** https://www.reddit.com/r/openclaw/comments/1qycudu/guide_my_3job_openclaw_morning_stack_daily_brief/

## Receipt to spreadsheet expense logger
**Trigger:** cron | **Effort:** low | **Value:** high
Photograph receipts throughout the day and send them to the agent. Overnight, the agent processes all pending receipts: extracts merchant, date, amount, and category using vision models, then logs to a spreadsheet or expense app. Morning summary shows yesterday's spending by category with running monthly totals. Can also flag unusual expenses ('this restaurant charge is 3x your normal amount') and duplicate detection ('you already logged a receipt from this merchant on this date').
**Skills:** gmail
**Gotcha:** Receipt OCR is ~90% accurate for printed receipts, much lower for handwritten. Always include the photo in your records for verification. The category assignment needs training — 'Whole Foods' is groceries, not restaurants. Review and correct the first few weeks of categorizations so the agent learns your system.
**Source:** https://www.reddit.com/r/openclaw/comments/1qycudu/

## Overnight autonomous coding with cron nudges
**Trigger:** cron | **Effort:** medium | **Value:** high
Set up a cron job that triggers the agent to work on coding tasks overnight while you sleep. The agent checks a backlog of features/bugs, picks items it can handle autonomously, writes code, creates pull requests, and leaves them for your morning review. The 'cron nudge' is a scheduled prompt that tells the agent to start working. In the morning, you review PRs, test, and merge. One user reports waking up to 2-3 PRs ready for review each morning.
**Skills:** coding-agent
**Gotcha:** Start with low-risk tasks — documentation fixes, refactors, test additions. Never let the agent work on production-critical code or database migrations without approval. Set a cost cap per night ($5-10) because autonomous coding can burn tokens. Also: the agent should comment its code thoroughly since you'll be reviewing it without the context of having written it.
**Source:** https://www.reddit.com/r/openclaw/comments/1r3cid8/

## 12 daily assistant use cases via Telegram
**Trigger:** reactive | **Effort:** low | **Value:** high
Treat OpenClaw as a text-based assistant for: inbox summary, quick research, draft replies, meeting prep, content ideas, translation, article summaries, reminders, option comparison, proofreading, ELI5, end-of-day recap.
**Skills:** telegram, gmail, web_search
**Gotcha:** The key insight: treat it like a real assistant you text throughout the day, not a tool you open for specific tasks. Natural messaging makes it 10x more useful.
**Source:** https://www.reddit.com/r/openclaw/comments/1rm9vtz/

## Headless CMS content updater
**Trigger:** reactive | **Effort:** medium | **Value:** high
Update website content via chat by integrating with a headless CMS (Strapi, Sanity, Contentful, etc.). 'Update the homepage hero to say X' or 'publish a new blog post with this content.' The agent makes API calls to the CMS, handles authentication, and confirms the change was published. Particularly useful for quick updates when you're away from your computer — fixing a typo, updating a price, or publishing time-sensitive news from your phone.
**Skills:** cms
**Gotcha:** Use a CMS API token with limited permissions — write access only to content types, not to users, settings, or schema. The agent should create drafts by default and only publish on explicit approval. Test the full flow on a staging environment before giving production access. Also: some CMS webhooks can trigger builds — be aware that content updates may redeploy your entire site.
**Source:** https://www.reddit.com/r/AgentsOfAI/comments/1rao3z6/

## Google Analytics daily metrics digest
**Trigger:** cron | **Effort:** low | **Value:** medium
Pull Google Analytics data (page views, sessions, bounce rate, top pages, traffic sources) and deliver a daily or weekly digest. Highlights significant changes: 'traffic from organic search is up 30% this week' or 'your new blog post is the #2 most visited page.' Can also compare periods and flag anomalies.
**Skills:** plausible, gsc
**Gotcha:** GA4 API requires a service account with viewer permissions. The metrics that matter depend on your business — don't dump everything, curate the 5-7 numbers you actually check. Anomaly detection is the highest-value feature: you don't need to see normal traffic, only notable changes.
**Source:** https://www.reddit.com/r/AgentsOfAI/comments/1rao3z6/

## CRM contact auto-creation from conversations
**Trigger:** reactive | **Effort:** medium | **Value:** high
The agent monitors your conversations (email, chat, meetings) and automatically creates CRM contacts when it detects new people. Extracts name, company, role, and context from the interaction. Deduplicates against existing contacts. You review and approve new contacts rather than manually entering them.
**Skills:** crm, gmail
**Gotcha:** The auto-detection creates false positives — automated emails, support tickets, and newsletters generate fake contacts. The approval step is essential for the first month. Give feedback on every false positive so the agent learns your noise filters.
**Source:** https://www.reddit.com/r/AgentsOfAI/comments/1rao3z6/

## Newsletter curation and highlights delivery
**Trigger:** cron | **Effort:** low | **Value:** high
Subscribe to newsletters via a dedicated email, and the agent summarizes the best content from each edition into a single curated digest. Instead of reading 15 full newsletters, you read one page of highlights with links to full articles that interest you. The agent learns which topics you click on and adjusts curation.
**Skills:** gmail, web_fetch
**Gotcha:** The dedicated newsletter email is important — keeps newsletters separate from your main inbox. The agent should summarize, not just list — 'this article argues X, which contradicts the common view of Y' is more useful than 'article about X.' Track click-throughs to improve curation over time.
**Source:** https://www.reddit.com/r/AgentsOfAI/comments/1rao3z6/

## Industry workflow automation (insurance/legal/real estate)
**Trigger:** reactive | **Effort:** high | **Value:** high
Map a boring industry workflow tip-to-tail (email trigger → legacy software clicks → downloads → parsing → CRM upload). OpenClaw as operator, Python pipeline for heavy lifting. Productize as recurring service.
**Skills:** browser-automation, exec, crm
**Gotcha:** Use Claude Code to build the Python pipeline separately — OpenClaw becomes the operator and trigger, not the implementation
**Source:** https://x.com/gregisenberg/status/2024247983999521123

## 5 proactive morning automations
**Trigger:** cron | **Effort:** medium | **Value:** high
Five cron jobs that fire before you wake up: (1) morning briefing with weather, calendar, priorities; (2) inbox scan for anything urgent; (3) meeting prep docs for today's external meetings; (4) overnight task completion summary; (5) goal check-in prompt. Combined, they give you a complete picture of your day within 5 minutes of waking up. Each runs independently so a failure in one doesn't block the others.
**Skills:** calendar, gmail, things-mac, web_search
**Gotcha:** Sequence matters: inbox scan after briefing so the agent has calendar context when prioritizing emails. Run meeting prep after inbox in case relevant emails affect meeting context. Each job should have its own error handling — partial results are better than no results.
**Source:** https://x.com/JakeLindsay/status/2025584224598667418

## GTM lead discovery machine
**Trigger:** cron | **Effort:** high | **Value:** high
The agent scans Product Hunt, Hacker News, relevant subreddits, and industry forums for companies and founders that match your ideal customer profile. Extracts contact info, company stage, recent funding, and product description. Delivers qualified leads daily with suggested outreach messages customized per lead. Integrates with your CRM to track pipeline.
**Skills:** web_search, browser, crm
**Gotcha:** Lead quality over quantity — 3 well-researched leads per day beats 30 scraped email addresses. The agent should explain WHY each lead matches your ICP, not just that they exist. Outreach messages need heavy personalization; template emails get ignored. Also: respect privacy regulations (GDPR, CAN-SPAM) in your outreach.
**Source:** https://x.com/VihaarNandigala/status/2029304616496832601

## AI influencer factory
**Trigger:** cron | **Effort:** high | **Value:** high
Create and manage AI-generated social media personas: generate consistent character images, write posts in a defined voice, engage with comments, and grow followings. The agent handles content creation, scheduling, and engagement. Multiple personas can target different niches simultaneously.
**Skills:** browser-automation, telegram
**Gotcha:** Platform terms of service explicitly prohibit fake personas in most cases — check before deploying. AI-generated content faces increasing detection and suppression on major platforms. The ethical considerations are significant: undisclosed AI personas undermine trust. If you do this, be transparent about the AI nature.
**Source:** https://x.com/i/communities/2026473818190131209

## Adaptive agent with n8n for fixed workflows
**Trigger:** reactive | **Effort:** low | **Value:** high
Use n8n for deterministic, repeatable workflows (API chains, data transforms) and OpenClaw for the adaptive conversational layer. The agent handles user intent, edge cases, and exceptions; n8n handles the reliable execution. Credentials stay in n8n, never exposed to the LLM.
**Skills:** webhook
**Gotcha:** This separation is cleaner than having the agent handle everything. n8n handles the 90% case reliably; the agent handles the 10% that needs judgment. Debug n8n workflows independently from the agent to isolate issues.
**Source:** https://buildtolaunch.substack.com/p/openclaw-ai-agent-one-person-business

## Bill management with WhatsApp briefing
**Trigger:** cron | **Effort:** medium | **Value:** high
Track recurring bills, due dates, and payments via WhatsApp. The agent sends monthly summaries showing upcoming bills, flags overdue payments, and tracks spending trends. Add new bills by texting a photo of a statement or forwarding a billing email. The WhatsApp format keeps it scannable: bold amounts, short lines.
**Skills:** gmail, whatsapp-styling-guide
**Gotcha:** WhatsApp formatting constraints (no tables, no headers) actually force better, more scannable bill summaries. The agent should never have payment credentials — tracking and alerting only, you pay manually. Flag bills that increased vs. last month.
**Source:** https://diamantai.substack.com/p/openclaw-tutorial-build-an-ai-agent

## Flight check-in automation
**Trigger:** cron | **Effort:** high | **Value:** high
Agent monitors your upcoming flights (from email confirmations or calendar), alerts you when online check-in opens (usually 24h before departure), and can navigate the airline website via browser automation to check you in. Sends your boarding pass via chat. Particularly useful for frequent flyers who would otherwise set manual reminders.
**Skills:** browser-automation, telegram
**Gotcha:** Airline websites are notoriously hostile to automation — frequent redesigns, CAPTCHAs, and bot detection. Browser automation with your real Chrome profile (logged into airline accounts) works better than headless browsers. Always verify the check-in succeeded with a screenshot of the boarding pass.
**Source:** https://x.com/coreyganim/status/2029891287046909994

## Weekly review and summary
**Trigger:** cron | **Effort:** low | **Value:** medium
Every Sunday, the agent compiles a comprehensive weekly review: what you accomplished (from todo completions, git commits, calendar events), what carried over, key decisions made, and suggested priorities for next week. Cross-references with your stated goals to show progress. Saves as a dated document for long-term tracking.
**Skills:** memory_search, todoist
**Gotcha:** The review should connect work to goals — not just 'you did 15 tasks' but 'you completed 3 tasks related to Goal X, 0 related to Goal Y.' The agent needs access to your goal definitions (from memory or a goals file) to make this connection meaningful.
**Source:** https://x.com/coreyganim/status/2029891287046909994

## Competitor research automation
**Trigger:** cron | **Effort:** medium | **Value:** high
Automated monitoring of competitor websites, social media accounts, and product updates. The agent checks for new blog posts, feature announcements, pricing changes, and job postings (which signal strategic direction). Weekly competitive intelligence summary shows the landscape with commentary on what matters for your business.
**Skills:** web_search, browser, web_fetch
**Gotcha:** Don't monitor everything — pick 3-5 direct competitors and 2-3 aspirational ones. Job postings are an underrated signal: if a competitor is hiring ML engineers, they're investing in AI features. The agent should distinguish between noise (blog posts) and signal (product launches, pricing changes).
**Source:** https://www.reddit.com/r/AI_Agents/comments/1qsfr58/

## Social media content scheduling and posting
**Trigger:** cron | **Effort:** medium | **Value:** medium
Schedule and publish content across platforms from chat. Draft posts, queue for optimal times, handle platform-specific formatting, and track engagement after posting. Supports X, LinkedIn, Instagram, and blog platforms with APIs. All drafts go through approval before publishing.
**Skills:** browser-automation, telegram
**Gotcha:** Never auto-publish without approval. Platform APIs change frequently and break integrations. The 'optimal time' suggestions need to be calibrated to YOUR audience, not generic best practices. Send yourself a preview before scheduling.
**Source:** https://www.reddit.com/r/openclaw/comments/1rm9vtz/

## SEO content audit and optimization
**Trigger:** cron | **Effort:** medium | **Value:** high
Audit existing website content for SEO: check title tags, meta descriptions, heading structure, keyword density, internal linking, page speed, and mobile-friendliness. Generate prioritized recommendations with estimated traffic impact. Can also generate optimized content briefs for new pages based on keyword research and competitor analysis.
**Skills:** gsc, web_fetch, browser
**Gotcha:** SEO recommendations are only useful if prioritized by impact. Don't fix everything — focus on the 20% of pages that drive 80% of traffic. The agent should use actual traffic data (Google Search Console) not just on-page analysis to prioritize fixes.
**Source:** https://buildtolaunch.substack.com/p/openclaw-autonomous-agent-live-demo

## Self-evolving agent strategy
**Trigger:** cron | **Effort:** medium | **Value:** medium
The agent periodically reviews its own performance — which tasks it completes well, which it struggles with, what you correct most often — and updates its own strategy files. It may adjust its SOUL.md communication style, create new skills for recurring tasks, or modify its cron schedule to better match your work patterns. The evolution is gradual and always transparent: it proposes changes for your approval.
**Skills:** general
**Gotcha:** The self-evolution must be transparent — the agent proposes changes, you approve or reject. Without oversight, the agent can drift in unexpected directions. Review the proposed changes carefully: subtle personality shifts in SOUL.md can significantly change behavior.
**Source:** https://buildtolaunch.substack.com/p/openclaw-autonomous-agent-live-demo

## Personal CRM with vector search
**Trigger:** cron | **Effort:** high | **Value:** high
Scan Gmail and Google Calendar to auto-discover contacts. Store in SQLite with vector embeddings for natural language queries ('who do I know at NVIDIA?'). Track relationship health scores, follow-up reminders, and duplicate detection.
**Skills:** gmail, calendar, crm
**Gotcha:** Auto-filter noise senders (marketing, newsletters) before CRM ingestion or your contact list fills with junk
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Meeting action items with Fathom integration
**Trigger:** cron | **Effort:** high | **Value:** high
Poll Fathom for meeting transcripts, match attendees to CRM contacts, extract action items with ownership (mine vs theirs). Approval queue in Telegram — only create tasks for approved items. 3x daily completion checks.
**Skills:** gmail, todoist, telegram, crm
**Gotcha:** Add a buffer after meeting end time before checking for transcripts — Fathom needs 5-10 minutes to process
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Urgent email detection with learning
**Trigger:** cron | **Effort:** medium | **Value:** high
Scan for important emails every 30 minutes during waking hours. AI classifies urgency with a feedback learning loop — learns from your corrections over time. Time-gates alerts to reasonable hours only.
**Skills:** gmail, telegram
**Gotcha:** Pre-filter known noise senders so they never even get classified — saves tokens and prevents false urgency
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Knowledge base with multi-source RAG
**Trigger:** reactive | **Effort:** high | **Value:** high
Drop URLs, YouTube videos, X posts, and PDFs into a Telegram topic to ingest. Extract entities, embed with vectors, and support semantic search with time-aware ranking. For paywalled sites, use browser automation.
**Skills:** telegram, web_fetch, browser, memory_search
**Gotcha:** When a tweet links to an article, ingest both the tweet and the full article — tweets alone lose context
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Business advisory council (parallel AI experts)
**Trigger:** cron | **Effort:** high | **Value:** high
8 specialist personas (RevenueGuardian, GrowthStrategist, SkepticalOperator, etc.) each analyze data from their domain independently. Synthesizer merges findings, deduplicates, ranks by priority. Interactive follow-ups via 'tell me more about #3'.
**Skills:** plausible, gsc, crm, gmail
**Gotcha:** Run all 8 in parallel so they can't influence each other — sequential processing causes later experts to anchor on earlier opinions
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Automated nightly security code review
**Trigger:** cron | **Effort:** medium | **Value:** high
Runs at 3:30am, analyzes entire codebase from 4 perspectives: offensive, defensive, data privacy, operational realism. Critical findings alert immediately. Interactive deep-dives on any finding number.
**Skills:** coding-agent, telegram
**Gotcha:** Use AI to actually read the code, not just static rules — the value is in understanding context and data flow, not pattern matching
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Cross-platform social media tracker
**Trigger:** cron | **Effort:** medium | **Value:** medium
Monitor your presence across X, LinkedIn, Instagram, YouTube, and your blog from one place. The agent tracks follower growth, engagement rates, top-performing content, and posting frequency across all platforms. Weekly reports compare platforms: 'LinkedIn engagement is up 20% while X is flat.' Identifies which platforms deserve more attention based on ROI.
**Skills:** browser, web_search
**Gotcha:** Cross-platform comparison is tricky because metrics aren't equivalent — a LinkedIn comment is worth more than an X like. The agent needs to understand your goals per platform to make useful comparisons. Also: each platform API has different auth flows and rate limits.
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Video idea pipeline from Slack
**Trigger:** reactive | **Effort:** medium | **Value:** high
Triggered by Slack mentions. Reads thread, runs X research, queries knowledge base for related saved content, creates structured Asana card with idea, research, sources, angles. Auto-dedup against previous pitches (40% similarity threshold).
**Skills:** slack, web_search, memory_search, todoist
**Gotcha:** Run semantic similarity against all previous pitches — without dedup, you get recycled ideas presented as new
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Dynamic earnings report tracker
**Trigger:** cron | **Effort:** medium | **Value:** medium
Sunday preview of upcoming earnings for watchlist stocks. Dynamically creates one-time cron jobs timed to run right after each earnings release. Delivers narrative verdict (beat/miss, market reaction, key takeaways), then auto-deletes the job.
**Skills:** web_search, telegram
**Gotcha:** Keep it narrative, not tables of numbers — nobody reads earnings tables in a Telegram message
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Food and symptom journal with analysis
**Trigger:** cron | **Effort:** low | **Value:** medium
Combined food and symptom logging via chat. Log meals and how you feel at natural times throughout the day. Over weeks, the agent builds correlation models: 'symptom X appears 24-48 hours after consuming Y.' Weekly reports show patterns, and the agent can suggest elimination diets to test hypotheses.
**Skills:** telegram
**Gotcha:** The 24-48 hour delay between food and symptoms is the tricky part — most people expect immediate correlations. The agent needs to look at multi-day windows. Correlation is not causation; always consult a doctor before making dietary changes based on the agent's analysis.
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## CRM-enriched daily briefing
**Trigger:** cron | **Effort:** medium | **Value:** high
7am briefing with full CRM context on every calendar attendee: who they are, what company, what you discussed last time, relevant history. Plus yesterday's content performance and pending action items.
**Skills:** gmail, calendar, crm, telegram
**Gotcha:** Cross-reference email threads related to today's meetings — walking in with email context makes prep 10x better than just knowing the meeting exists
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Organized Telegram topic routing
**Trigger:** reactive | **Effort:** low | **Value:** high
Use Telegram topic channels to organize different agent workflows: one topic for daily briefs, one for knowledge base ingestion, one for task management, one for casual conversation. The agent recognizes which topic it's in and adjusts behavior accordingly. Keeps your agent interactions organized instead of one endless chat stream.
**Skills:** telegram
**Gotcha:** Telegram topics are only available in groups/supergroups, not 1:1 chats. Create a private group with just you and the bot. Each topic should have clear boundaries in the agent's config so it doesn't mix contexts. The agent should respond in the same topic it received the message in.
**Source:** https://gist.github.com/mberman84/63163d6839053fbf15091238e5ada5c2

## Home Assistant AI agent with memory
**Trigger:** reactive | **Effort:** medium | **Value:** high
Connect your full OpenClaw agent to Home Assistant's voice pipeline. Unlike basic HA voice assistants, this one has memory of your preferences, context of your schedule, and access to all your agent's tools. 'What's on my calendar today?' works alongside 'turn off the lights' because it's your full agent, not a limited voice command interpreter.
**Skills:** home-assistant
**Gotcha:** Latency is the main challenge — STT + LLM + TTS needs to be under 3 seconds for voice to feel natural. Use Haiku for voice queries and escalate complex ones to Opus. The agent's full context is both a strength (smart responses) and a risk (exposing private information through a speaker in a shared room).
**Source:** https://www.reddit.com/r/homeassistant/comments/1qrk31x/

## HA voice assistant via HACS integration
**Trigger:** reactive | **Effort:** medium | **Value:** high
Connect Home Assistant's voice pipeline to your OpenClaw agent via the OpenAI-compatible API endpoint. Your full agent (with all its tools, memory, and personality) becomes your voice assistant through HA's voice hardware — ESPHome satellite speakers, Google Home speakers running HA, or just your phone. Say 'Hey Jarvis, what's on my calendar today?' and your full OpenClaw agent responds, not a limited voice assistant. Uses Whisper for STT and Piper (or Kokoro) for TTS, all running locally. Your agent's full context is available: it knows about your schedule, your projects, your preferences.
**Skills:** home-assistant, openai-whisper
**Gotcha:** The OpenAI-compatible API endpoint in OpenClaw needs to be exposed on your local network for HA to reach it. Latency is the main challenge: STT + LLM reasoning + TTS needs to be under 3 seconds total or the voice interaction feels broken. Use Haiku (fast) for voice queries and only escalate to Opus for complex questions. Keep the agent's voice responses concise — nobody wants to listen to a 30-second paragraph from a voice assistant.
**Source:** https://www.reddit.com/r/homeassistant/comments/1ri8woh/

## Clawphone: real phone number for your agent
**Trigger:** reactive | **Effort:** medium | **Value:** high
Give your agent its own phone number via Twilio. People can call or text it directly. The agent handles calls with voice, texts with chat, and can route to you for urgent matters. Useful as a business line: clients call your agent for basic questions, it handles what it can and escalates the rest.
**Skills:** voice-wake-say, telegram
**Gotcha:** A public phone number means anyone can interact with your agent — set strict boundaries on what information it shares and what actions it can take on inbound calls. Rate limit to prevent abuse. The agent should never share personal information with callers. Consider a voicemail fallback for when the agent can't handle a request.
**Source:** https://www.reddit.com/r/openclaw/comments/1rd1zco/

## Meshtastic LoRa smart home over mesh radio
**Trigger:** reactive | **Effort:** high | **Value:** medium
Control smart home over LoRa mesh radio with zero internet. OpenClaw monitors Meshtastic radio 24/7, responds to queries, controls Home Assistant, and sends voice messages to speakers. Auto-chunks responses to fit 200-char LoRa limit.
**Skills:** home-assistant, exec
**Gotcha:** LoRa has a 200-char message limit — auto-chunk responses or they get silently truncated
**Source:** https://www.reddit.com/r/meshtastic/comments/1r8fbfs/

## Obsidian vault as agent second brain
**Trigger:** reactive | **Effort:** medium | **Value:** high
Agent reads/writes Obsidian vault directly. Uses QMD (query markdown) to search notes without loading everything — 80-90% token reduction. Skills loaded on demand. All changes committed to GitHub for revert safety.
**Skills:** obsidian-notesmd-cli, git-essentials
**Gotcha:** Define editing guardrails — the agent should follow rules about what it can modify, and an orchestration layer validates changes before commit
**Source:** https://www.reddit.com/r/ObsidianMD/comments/1rm8vux/

## Android voice assistant with local LLMs
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Use OpenClaw on Android as a voice assistant powered by local LLMs. Voice input via the Android OpenClaw app, processed by a local model running on your server or a powerful phone, response delivered as audio. No cloud API needed — fully offline capable if the model runs on the phone itself (requires high-end device).
**Skills:** openai-whisper, kokoro-tts
**Gotcha:** Android phones don't have enough RAM for serious local LLM inference — you'll typically need a server running the model with the phone as a client. Battery drain from continuous listening is significant. The OpenClaw Android app handles the connection; the voice processing happens on your server.
**Source:** https://www.reddit.com/r/LocalLLaMA/comments/1qvdu9n/

## DIY RPi 5 assistant with Ollama
**Trigger:** reactive | **Effort:** high | **Value:** medium
Build a Raspberry Pi 5 voice assistant running Ollama for local LLM inference. The Pi handles the gateway and voice I/O; Ollama runs smaller models (Qwen 3B, Llama 8B) for basic assistant tasks. Total hardware cost: $80-120. Fully local, fully private, zero ongoing API costs. Limited by model size — good for simple tasks, not complex reasoning.
**Skills:** exec
**Gotcha:** The RPi 5 has 8GB RAM max, limiting you to 3B-8B quantized models. Response quality is noticeably lower than cloud models — good for home automation commands and simple Q&A, not for coding or complex analysis. An SSD (not SD card) is essential for model loading speed.
**Source:** https://www.reddit.com/r/LocalLLM/comments/1r84jou/

## Homelab security hardening for agents
**Trigger:** manual | **Effort:** high | **Value:** high
Security hardening checklist for running AI agents on homelab infrastructure: network segmentation (agent on separate VLAN), credential isolation (never in LLM context), exec allowlisting (only specific commands), filesystem sandboxing (read-only workspace), and audit logging. Also covers: Tailscale for secure remote access, SSH key rotation, and monitoring for unauthorized command execution.
**Skills:** docker-essentials, security-auditor
**Gotcha:** The biggest risk isn't the agent going rogue — it's the agent being manipulated via prompt injection through external data (emails, web pages, chat messages). Defense in depth: network isolation + command allowlisting + credential separation. Also: keep the agent's OS updated — it's another attack surface.
**Source:** https://www.reddit.com/r/homelab/comments/1runv49/

## Team standup coordinator in group chat
**Trigger:** cron | **Effort:** medium | **Value:** high
A persistent agent that lives in a team group chat (Telegram, Discord, or Slack) with both group and DM access. Runs two daily cycles: a morning standup at 9am pulls merged PRs from GitHub and status changes from Linear/Jira, generating a 'what shipped yesterday' summary that focuses on untracked work — decisions made, conversations had, things not in tickets. An EOD check-in at 5pm asks each person about blockers. The agent also handles ad-hoc requests like debugging customer issues by pulling relevant logs and context. One team running Opus 4.6 reports $1-5/day on light days (simple standup + few queries), up to $110 on heavy days where the whole team is actively chatting with it and having it implement features. Most teams run Sonnet at ~$75/week total.
**Skills:** telegram, github
**Gotcha:** The biggest surprise is the social dynamic — every team that's deployed this reports their people would be 'sad' if the bot was removed. It becomes a genuine teammate, not just a tool. Give it DM access alongside the group chat so people can ask things privately without cluttering the channel. Also: let it have a personality (name it, give it opinions) — sterile bots get ignored.
**Source:** https://news.ycombinator.com/item?id=47147183

## Competitor feature tracker via Twitter
**Trigger:** cron | **Effort:** medium | **Value:** high
Monitor competitors on X/Twitter for product launches and feature announcements. The agent checks specific accounts daily, filters for product-related tweets (not generic marketing), and alerts you when a competitor ships something new. Cross-references with their changelog and blog for details. Weekly competitive intelligence summary shows the landscape.
**Skills:** web_search, browser, telegram
**Gotcha:** Filter aggressively — you want product launches and feature announcements, not every tweet. Set up specific competitor accounts to monitor rather than keyword search, which is too noisy. The agent should distinguish between announced features and actually shipped features.
**Source:** https://news.ycombinator.com/item?id=47147183

## SOC2 compliance vendor evaluation assistant
**Trigger:** reactive | **Effort:** low | **Value:** high
Instead of taking structured notes during vendor evaluations, just message the agent as events happen — 'talked to Vendor X, they don't support SSO', 'pricing came back at $50k/yr', 'security questionnaire shows no SOC2 cert'. The agent accumulates these unstructured messages over days/weeks, then compiles a structured evaluation document on demand with sections for security posture, pricing comparison, feature gaps, and recommendations. Works because the agent maintains full conversation context — you don't need to organize upfront, just text as things happen.
**Skills:** telegram, memory_search
**Gotcha:** The key insight is that the agent inverts the documentation workflow: instead of taking notes and then organizing them, you dump raw observations and the agent structures them. This only works well if you consistently message the bot as things happen — big gaps in reporting mean the doc misses critical context.
**Source:** https://news.ycombinator.com/item?id=47147183

## Trip planning calendar summarizer
**Trigger:** reactive | **Effort:** low | **Value:** medium
Works with a shared spreadsheet or markdown calendar for multi-destination trips. When someone asks 'when will you be in Taiwan?', you text the agent and it summarizes the relevant dates and locations into a copy-paste-ready text message. One user's wife uses this via a shared Telegram group — she texts the agent the question, it looks up the trip spreadsheet, and formats a clean response she can forward directly to the friend who asked.
**Skills:** telegram
**Gotcha:** The calendar needs to be in a structured format the agent can reference — a Google Sheet with dates and locations works best. Raw text itineraries are harder to parse reliably. Share the sheet with the agent's Google account for direct access rather than copy-pasting.
**Source:** https://news.ycombinator.com/item?id=47147183

## Rain alert for bike cover
**Trigger:** cron | **Effort:** low | **Value:** medium
You tell the agent 'I want to know when to cover my bike before it rains' and it handles everything — writes a weather-checking script, creates a cron schedule, and sets up Telegram notifications. The agent checks hourly forecasts and sends an alert 2-3 hours before rain is expected, giving you time to act. One user reported the agent self-created the functionality after a single natural language request — no manual scripting or cron configuration needed.
**Skills:** weather
**Gotcha:** Tell the agent what functionality you want, not how to implement it. It can write the script and schedule the cron job itself. The weather API (Open-Meteo or wttr.in) is free and doesn't need an API key, so this is genuinely zero-cost beyond the LLM tokens.
**Source:** https://news.ycombinator.com/item?id=47147183

## Combined household priority list
**Trigger:** cron | **Effort:** low | **Value:** medium
Agent pulls both your and your partner's todo lists (from Todoist, Things, or similar), cross-references deadlines and priorities, and generates a combined top-3 list each morning. Delivered via a shared Telegram group or DM. One couple uses this as their morning alignment ritual — the agent knows both people's contexts and can flag when tasks conflict or when one person's urgent item affects the other's plans.
**Skills:** todoist, telegram
**Gotcha:** Prioritize by urgency and deadlines across both lists — don't just interleave them alternating. The agent needs access to both todo apps, which usually means separate API tokens. Some couples prefer a shared list app instead, which simplifies auth.
**Source:** https://news.ycombinator.com/item?id=47147183

## Curated HN AI digest
**Trigger:** cron | **Effort:** low | **Value:** high
Every morning, the agent scrapes Hacker News front page and /newest for AI-related posts, filters aggressively to remove culture war debates and hype pieces, then sends a 5-8 item digest focusing on what actually matters: new model releases, novel techniques, interesting tools, and significant benchmarks. Each item gets a one-line summary and the HN comment count so you can decide what's worth clicking into. One user runs this as a cron job that costs pennies per day on Sonnet.
**Skills:** web_search, telegram
**Gotcha:** Explicitly filter OUT culture war and drama — the default tendency is to include anything with high engagement, which means flamewars dominate. Add negative filters: 'skip posts that are primarily about AI ethics debates, job displacement fears, or company drama unless there's a concrete technical development involved.' The comment count threshold helps too — popular technical posts tend to have 50-200 comments, not 500+.
**Source:** https://news.ycombinator.com/item?id=47147183

## Hardware deal watcher on subreddits
**Trigger:** cron | **Effort:** medium | **Value:** high
Monitors specific subreddits (r/hardwareswap, r/homelabsales, r/buildapcsales) for deals matching highly specific criteria — e.g., 'SXM5 boards under $3000', 'Mac Studios with >64GB RAM', 'RTX 4090 under $1200'. Agent checks every 30 minutes via web scraping, scores matches against your criteria, and sends immediate Telegram notifications with the post link. One user scored server hardware at well below market because the agent caught a post within minutes of listing.
**Skills:** web_search, browser, telegram
**Gotcha:** Reddit posts expire fast — deals get claimed within hours. Check frequently (every 30 min minimum) and send instant notifications, never batch into a daily digest. Also: Reddit's API rate limits are strict for authenticated use, so most people scrape the public JSON endpoints (reddit.com/r/sub.json) instead of using the official API.
**Source:** https://news.ycombinator.com/item?id=47147183

## Apartment/rental listing scanner
**Trigger:** cron | **Effort:** high | **Value:** high
Daily cron job that uses browser automation to scan Zillow, Redfin, and Craigslist for apartments matching your criteria (location, price range, bedrooms, etc.). The agent navigates each site like a human — handles filters, pagination, and dynamic loading — then rates listings on quality (photos, description completeness, price vs market), validates availability by checking listing dates, and sends a curated daily email or Telegram message with the top picks. One user had their agent also flag suspicious listings (too-good-to-be-true prices, stock photos).
**Skills:** browser-automation, web_search, telegram
**Gotcha:** Real estate sites actively block scraping — you need browser automation with a real Chrome profile, not headless HTTP requests. Zillow in particular detects and blocks bot-like behavior. Use random delays between page loads, rotate user agents, and consider running from a residential IP rather than a VPS.
**Source:** https://news.ycombinator.com/item?id=47147183

## Media server recovery and maintenance
**Trigger:** reactive | **Effort:** high | **Value:** high
An agent with SSH credentials to your media server that handles full remote triage via chat. One user hadn't used their server in a year — after an OS update, it wouldn't boot. They plugged in a keyboard and screen, sent the agent screenshots of the error via their phone camera. The agent read the error from the photo, dictated journalctl commands to run, diagnosed a corrupt fstab entry, fixed the mount configuration, and got the server booting again. Then it discovered 1,300 bad sectors on one drive, determined the files were likely intact (bad sectors were early/metadata), copied 1.5TB to a healthy drive, and fully restored the setup. The user said they would have thrown the whole box out without the agent.
**Skills:** exec, telegram
**Gotcha:** The agent can diagnose from screenshots — take photos of error screens with your phone and send them via chat. This is surprisingly effective because most boot errors and crash screens have readable text that the vision model can parse. The real power is having an always-available Linux sysadmin in your pocket who can walk you through hardware triage without you needing to know the commands.
**Source:** https://news.ycombinator.com/item?id=47147183

## Business operating system via WhatsApp
**Trigger:** reactive | **Effort:** high | **Value:** high
A solo founder in Bucharest built a complete business OS on top of OpenClaw with 79 custom tools: contracts, invoices, payments, time tracking, reminders, and browser automation. Everything runs through WhatsApp — 'Create a contract for Sarah, $5k branding project' generates and sends the contract. 'What's overdue?' pulls all outstanding invoices and sends reminders to clients. No dashboards, no tabs, no switching between 10 apps. Took 2 years and 4 complete rebuilds to get right. The founder describes it as 'your business running in the background while you do the actual work.'
**Skills:** whatsapp-styling-guide, browser-automation, crm
**Gotcha:** The value isn't the individual tools — it's removing app-switching entirely. When everything lives in one chat interface, the cognitive overhead of managing a business drops dramatically. The 4 rebuilds were necessary because the first versions tried to replicate existing dashboards in chat, which doesn't work — you need to rethink workflows for a conversational interface.
**Source:** https://news.ycombinator.com/item?id=47041682

## Calendar meeting scheduling via text
**Trigger:** reactive | **Effort:** low | **Value:** high
Text the agent 'schedule a call with John next Tuesday 2pm' and it creates the event on a delegated Google Calendar, sends invites, and confirms back. One user delegates a separate Google Calendar to the agent's Google account — the agent can create, modify, and delete events without accessing the primary calendar. Also handles more complex requests like 'find a 30-minute slot next week that works for both me and Sarah' by checking availability across calendars.
**Skills:** calendar, telegram
**Gotcha:** Delegate a separate Google Calendar to the agent's Google account rather than giving it access to your primary calendar. This limits blast radius if something goes wrong and makes it easy to see which events the agent created. The gcalcli tool handles most calendar operations but struggles with recurring events — for those, the Google Calendar API via a custom skill works better.
**Source:** https://news.ycombinator.com/item?id=47147183

## Competitive price scraping via browser
**Trigger:** cron | **Effort:** medium | **Value:** high
Daily cron job opens competitor websites via browser automation, navigates to pricing pages, extracts data, and writes to a local file or pushes to a channel. Handles dynamic SPAs and JavaScript-rendered pages that simple HTTP scraping can't. Tracks price changes over time and alerts on significant movements.
**Skills:** browser-automation
**Gotcha:** Use browser aria refs for stable element targeting — CSS selectors break when competitors redesign. Sites with anti-scraping measures need random delays and user agent rotation. Consider running from a residential IP rather than a datacenter to avoid blocks.
**Source:** https://dev.to/xujfcn/openclaw-advanced-10-hidden-capabilities-that-turn-your-ai-into-a-production-powerhouse-31mj

## Multi-agent blog post pipeline
**Trigger:** reactive | **Effort:** high | **Value:** high
Ops agent handles topic selection and outlining, spawns a coding agent for code examples and an analyst agent for SEO data. Three agents work independently, results consolidate, final article assembled automatically.
**Skills:** coding-agent, gsc, web_search
**Gotcha:** Spawn sub-agents with independent context — don't share sessions or the coding agent's code examples will be influenced by the SEO data
**Source:** https://dev.to/xujfcn/openclaw-advanced-10-hidden-capabilities-that-turn-your-ai-into-a-production-powerhouse-31mj

## Canvas real-time monitoring dashboard
**Trigger:** reactive | **Effort:** low | **Value:** medium
The agent generates a full HTML monitoring dashboard using the Canvas tool — CPU charts, memory pie charts, request volume bars. From instruction to interactive interface in under 30 seconds. Embedded Chart.js with data refreshed via JavaScript timers. No frontend code needed — describe what you want to see and the agent builds the entire page.
**Skills:** general
**Gotcha:** Canvas generates the complete HTML including libraries — it's surprisingly capable for quick dashboards. For persistent monitoring, save the generated HTML and serve it via a simple HTTP server rather than regenerating each time.
**Source:** https://dev.to/xujfcn/openclaw-advanced-10-hidden-capabilities-that-turn-your-ai-into-a-production-powerhouse-31mj

## Autonomous PR review first-pass
**Trigger:** reactive | **Effort:** medium | **Value:** high
Agent performs first-pass PR reviews: checks code style, catches common bugs (unused imports, missing error handling, SQL injection risks), suggests improvements, and summarizes large diffs. Human reviewer then focuses on architecture, logic, and business context. Can be triggered automatically via GitHub webhooks on new PRs.
**Skills:** github, coding-agent
**Gotcha:** This is a first pass, not a replacement for human review. The agent misses business context and subtle logic issues. Large PRs (1000+ lines) exceed token limits — the agent reviews files selectively. Set expectations: 'flag obvious problems, don't approve.'
**Source:** https://dev.to/shehzan/openclaw-for-developers-building-solo-dev-companies-2o6g

## CI/CD pipeline monitor with auto-rollback
**Trigger:** reactive | **Effort:** high | **Value:** high
Monitor CI/CD pipelines, alert on build failures, and trigger auto-rollback when error rates spike. Gathers logs, creates incident tickets, and notifies on-call engineers. The agent tracks build history to identify flaky tests vs. genuine failures and can ignore known intermittent issues.
**Skills:** github, exec, telegram
**Gotcha:** Auto-rollback should have a confirmation step in staging but be automatic in production with high error rates. The agent needs access to your deployment system and monitoring metrics. False positive detection (flaky tests) is critical or you'll get alert fatigue.
**Source:** https://dev.to/shehzan/openclaw-for-developers-building-solo-dev-companies-2o6g

## 13-agent specialized team
**Trigger:** cron | **Effort:** high | **Value:** high
13 agents with dedicated roles: chief of staff (Leo), quality management (Morpheus), morning briefing (Atlas), compliance scanner, and more. Each has its own cron jobs, shared memory via a common workspace, and a self-updating kanban board. Built by a healthcare AI startup CTO in Berlin in one 12-hour session. Total cost varies by usage: $75/week on mostly Sonnet with rare Opus spikes.
**Skills:** telegram, coding-agent, todoist
**Gotcha:** Start with 2-3 agents, not 13 — each needs its own debugging cycle before adding the next. The shared memory via common workspace files is the coordination mechanism. Naming agents with personality (Leo, Morpheus, Atlas) surprisingly improves how you interact with them.
**Source:** https://alirezarezvani.medium.com/openclaw-multi-agent-system-the-blueprint-i-built-in-12-hours-509498d02908

## Data pipeline with automated reporting
**Trigger:** cron | **Effort:** medium | **Value:** high
Read CSV/Excel data, analyze with pandas-style operations, create charts via Canvas HTML generation, and deliver reports to Slack or email. Fully automated data-to-insight pipeline. The agent can schedule recurring reports: 'every Monday morning, pull last week's sales data and send a summary to #analytics.'
**Skills:** gmail, slack
**Gotcha:** Use Canvas for chart generation — it produces better visualizations than trying to generate image files. For large datasets, have the agent write and execute Python scripts rather than processing data in-context. Set up error handling for missing or malformed data files.
**Source:** https://medium.com/@cenrunzhe/openclaw-explained-how-the-hottest-agent-framework-works-and-why-data-teams-should-pay-attention-69b41a033ca6

## Teach once, run as cron pattern
**Trigger:** cron | **Effort:** low | **Value:** high
The most cost-effective pattern for building reliable automations. Do a task once interactively — for example, walk the agent through checking a competitor's pricing page, pointing out which elements to look at and what format you want the data in. The agent learns from this single interaction and you convert it into a dialed-in cron job that runs daily. The interactive teaching session costs more tokens upfront ($2-5 for a complex browser task), but the resulting cron job is cheap ($0.10-0.30/run) because it knows exactly what to do without exploration. One user describes this as the fundamental pattern: 'I'm usually more interested in doing things once to teach it, then having it run that as a dialed-in cron job.'
**Skills:** general
**Gotcha:** The teaching session needs to be thorough — don't just say 'check their prices.' Walk through the exact pages, point out the specific elements, and describe the output format you want. The more precise the teaching interaction, the more reliable and cheaper the resulting cron job. Also: save the conversation that produced the cron config so you can re-teach if the target site changes.
**Source:** https://news.ycombinator.com/item?id=47147183

## Personal CRM with Contact Auto-Discovery
**Trigger:** cron | **Effort:** high | **Value:** high
A custom CRM built entirely through natural language prompts, running on a local SQLite database with vector embeddings. Ingests from three sources: Gmail (filters out newsletters and cold pitches), Google Calendar (calendar-aware, knows when meetings with external people end), and Fathom AI notetaker (pulls transcripts every 5 minutes during business hours). An LLM reads each data source, decides which contacts are worth saving based on email context and research, then pulls them into a local database. Currently holds 371+ contacts with natural language search — 'what did I last talk about with John?' or 'who did I last speak to at Company X?' Also includes relationship health scores that flag stale relationships, follow-up reminders with snooze/done actions, and duplicate detection with merge suggestions. The system is proactive — if you're brainstorming a video idea, it might notice you discussed something similar with a sponsor and suggest the connection. One user describes it as 'having a team of three or four personal sales reps going 24 hours a day.'
**Skills:** gmail, crm
**Gotcha:** The real power comes from cross-source intelligence — the agent sees your email, calendar, AND meeting transcripts together, which lets it make connections no single-source CRM can. Security is the main concern: you're giving an LLM access to all your email. Harden with prompt injection filters and consider running a local model for the initial email scan before sending anything to a cloud model.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Meeting Action Item Extraction & Approval
**Trigger:** cron | **Effort:** high | **Value:** high
A pipeline that monitors Fathom AI notetaker for completed meeting transcripts, checking every 5 minutes during business hours. It's calendar-aware — knows when meetings end and waits for a buffer before checking for the transcript. When ready, it matches attendees to existing CRM contacts, updates relationship summaries with meeting context, and extracts action items with ownership tracking (yours vs. theirs). Extracted items go to a Telegram approval queue where you approve or reject each one — approved items create Todoist tasks automatically, rejected items trigger a learning loop where the agent updates its extraction criteria. Also tracks other people's commitments ('waiting on' items) and runs completion checks 3x daily, auto-archiving items older than 14 days.
**Skills:** gmail, todoist, message
**Gotcha:** Not all extracted action items are real — the agent initially over-extracts, catching things like 'I'll think about it' as commitments. The approval step is critical, and the learning loop genuinely improves extraction over time. Also valuable: tracking what OTHER people promised you, not just your own action items. That's the feature most people miss.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Urgent Email Scanner & Telegram Alert
**Trigger:** cron | **Effort:** medium | **Value:** high
Every 30 minutes, the agent scans your Gmail for emails that need immediate attention — not just unread emails, but specifically urgent ones like big deals, contracts needing signatures, or important commitments you made. The key is aggressive tuning: the agent should only alert you for things that genuinely require immediate action. One user reports this lets them completely stop checking email on weekends while still catching the rare critical message. The alert goes to Telegram as a concise summary with the sender, subject, and why it's urgent.
**Skills:** gmail, message
**Gotcha:** The tuning process takes 1-2 weeks of feedback. Initially the agent will alert too often — you need to consistently tell it 'that wasn't urgent' or 'this could have waited until Monday' for the filter to tighten. The goal is maybe 1-3 alerts per week, not 10 per day. If you're getting more than a few alerts daily, your urgency threshold is too low.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Personal Knowledge Base with RAG & Twitter Thread Ingestion
**Trigger:** manual | **Effort:** high | **Value:** high
A central repository for every piece of content you encounter — articles, YouTube videos, X/Twitter posts, PDFs. Drop any URL into a Telegram topic and the agent ingests it fully: for tweets, it follows the entire thread, grabs any linked articles, and ingests those too. Everything gets chunked, embedded in vectors, and stored in a local SQLite database. The X/Twitter ingestion pipeline has multiple fallbacks: FX Twitter first, then X API directly, then Gro X search. For paywalled sites you're logged into, it uses browser automation through your Chrome session to extract content. Cross-posts summaries to team Slack with attribution ('Matt wants you to see this') so your team knows it's curated, not bot spam. Natural language queries support semantic search with time-aware and source-weighted ranking.
**Skills:** web_fetch, message, browser
**Gotcha:** X/Twitter ingestion is the hardest part to set up — X is finicky about API access and scraping. The multi-fallback chain (FX Twitter → X API → Gro X search → thread following) took significant trial and error. For YouTube videos, the agent grabs the transcript and embeds that, which works surprisingly well for later search. The team sharing feature requires careful framing — label posts as 'I read this and want you to see it' not just auto-shared links.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Team-Shared Reading List with Attribution
**Trigger:** manual | **Effort:** medium | **Value:** medium
When you save an article or link to your knowledge base, the agent cross-posts it to your team's Slack channel with proper attribution — making it clear this was something you personally read and curated, not an automated spam feed. The message includes a summary and the source link. This solves the 'I found this interesting article but forgot to share it' problem and the 'my team ignores bot-posted links' problem simultaneously, because attribution proves a human vetted it.
**Skills:** web_fetch, message
**Gotcha:** The attribution framing matters enormously. 'Matt wants you to see this' gets read. 'New article detected' gets ignored. The agent needs to make it clear a human curated this content. Also: don't share everything — only flag articles you'd actually walk over to someone's desk to mention.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Self-Improving Automation System
**Trigger:** reactive | **Effort:** high | **Value:** high
A meta-system where the agent evolves its own prompts and workflows based on your feedback. When you reject an action item extraction, the agent doesn't just skip it — it updates its extraction prompt to avoid similar false positives. When you correct its email urgency assessment, it refines its urgency criteria. The identity.md and soul.md files get updated based on accumulated interactions, and the memory system (daily markdown notes → distilled MEMORY.md → vectorized for RAG search) means the agent's context grows over time. One user's agent remembers writing preferences, email triage rules, stock tracking interests, video pitch formatting, and business patterns — all learned from natural conversation, not manual configuration.
**Skills:** message
**Gotcha:** The self-improvement only works if you consistently give feedback rather than just ignoring bad outputs. Every time you say 'that wasn't right' and explain why, the agent updates its internal rules. The compounding effect is significant — after 2-3 weeks of active feedback, the agent's accuracy on your specific preferences is dramatically better than day one.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Cross-Source Intelligence & Proactive Sponsorship Matching
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Because the agent has access to your CRM contacts, meeting transcripts, email history, and knowledge base simultaneously, it can make connections across sources that no single tool could. The flagship example: you're brainstorming a video idea, and the agent notices you discussed a similar topic with a sponsor three weeks ago — then proactively suggests that sponsor might want to fund this video. It's not a dedicated 'sponsorship matching' feature, it's emergent behavior from giving the agent broad context across your professional life.
**Skills:** crm, gmail
**Gotcha:** This only works when the agent has truly broad access — CRM + email + calendar + knowledge base. If you silo data sources, you lose the cross-referencing that makes these insights possible. The trade-off is real: more access = better intelligence = bigger security surface.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Email Triage with Humanizer
**Trigger:** reactive | **Effort:** low | **Value:** medium
The agent reads incoming emails, categorizes them by priority and type (urgent, requires response, FYI, newsletter, cold pitch), and drafts responses for the ones that need them. The humanizer skill strips any AI-sounding language from the drafts — no em dashes, no 'I hope this finds you well', no bullet-point-heavy structure. The result reads like you wrote it quickly. Drafts go to an approval queue so you can edit/send/reject, and the agent learns your response patterns over time.
**Skills:** gmail, humanizer
**Gotcha:** The humanizer step is critical — without it, recipients will notice your emails suddenly sound different. The specific patterns to strip: excessive em dashes, 'I'd be happy to', numbered lists where prose would be natural, and overly formal sign-offs. Train the agent on 10-20 of your actual sent emails so it captures your real voice.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Relationship Health Scoring & Stale Contact Detection
**Trigger:** cron | **Effort:** medium | **Value:** medium
Part of the CRM system — each contact gets a health score based on interaction recency, frequency, and depth. Contacts you haven't engaged with in 30+ days get flagged as stale with suggested re-engagement actions. The scoring weighs meeting interactions higher than emails, and considers whether interactions were inbound (they reached out) vs. outbound (you reached out). Weekly digest shows your top stale relationships that matter most based on deal size or relationship importance.
**Skills:** crm
**Gotcha:** Not all stale relationships need attention — the agent should factor in relationship importance, not just recency. A dormant relationship with a key partner is worth flagging; a cold contact from a networking event is not. Tune the importance weights based on your actual business context.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Daily Notes + Distilled Memory System
**Trigger:** cron | **Effort:** low | **Value:** high
The default OpenClaw memory architecture: every conversation generates daily notes saved as memory/YYYY-MM-DD.md markdown files. Periodically, the agent distills these raw logs into MEMORY.md — a curated file of preferences, decisions, lessons learned, and ongoing context. Both layers get vectorized for RAG search, so the agent can semantically search across all past interactions. Over time, the agent remembers your writing preferences, stock tracking interests, email triage rules, video formatting preferences, and operational lessons — all learned from natural conversation rather than manual configuration.
**Skills:** message
**Gotcha:** The distillation step (daily notes → MEMORY.md) is where the real value compounds. Without it, you just have a pile of daily logs that grows unboundedly. Review MEMORY.md periodically to prune outdated information — the agent can develop 'false memories' if old context contradicts current preferences.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## RAG-Powered Vector Search on Conversations
**Trigger:** reactive | **Effort:** medium | **Value:** high
All conversation history, daily notes, and memory files get embedded as vectors in a local database, enabling semantic search across everything you've ever discussed with your agent. Ask 'what did we decide about the pricing strategy?' and it finds the relevant conversation even if you never used the word 'pricing' — it understands the semantic meaning. Uses the QMD (Query Memory Database) system originally built by Tobi Lütke (Shopify founder). Everything stays local on your machine, no cloud vector database needed.
**Skills:** message
**Gotcha:** Semantic search quality depends heavily on the embedding model. The default works well for short queries but struggles with very specific technical terms. If you're searching for exact strings or code snippets, use grep-style search as a fallback. Also: the vector index needs periodic rebuilding as your memory grows past a few thousand entries.
**Source:** 21 INSANE Use Cases For OpenClaw....txt

## Morning Meeting Prep from Calendar
**Trigger:** cron | **Effort:** medium | **Value:** high
Every morning before you wake up, the agent opens your Google Calendar (either via browser automation on your Chrome session or the gcalcli skill), identifies all meetings for the day, then builds a prep document for each one. For every meeting, it researches the attendees — checks LinkedIn for their current role, searches its own memory for every past interaction you've had with that person, and compiles all relevant context into a single briefing doc. It also schedules a reminder 15 minutes before each meeting so you don't forget. One user went from 'going into every meeting without doing much prep at all' to having full executive-assistant-level briefings for every meeting. The prep docs include: attendee background, last interaction date, what you discussed previously, and relevant context for today's agenda.
**Skills:** gmail, browser, web_fetch
**Gotcha:** The implementation depends on your setup. If you're running on a local Mac with Chrome, the agent can open calendar.google.com directly in your browser (it needs to be logged in). On a VPS without a display, you'll need the Google Calendar skill or gcalcli for programmatic access. Ask your agent 'based on how we work together, what's the best way for you to access Google Calendar?' — it'll figure out the right approach for your environment.
**Source:** 5 OpenClaw use cases that will make you a productivity MACHINE.txt

## Weekly Goals Check-In & Accountability
**Trigger:** cron | **Effort:** low | **Value:** high
Every Friday at a set time, the agent sends you a structured check-in covering your goals, progress, and mental state. It asks specific questions about metrics you care about — subscriber counts, revenue milestones, project membership numbers — and tracks them over time in documents you can review later. Based on trends, it gives you actionable suggestions: 'these videos are performing well, make more like them' or 'that feature you shipped is getting traction, double down.' You can take it further by having it build charts in Mission Control to visualize goal progress over time. The key insight is that regular structured reflection — not just working harder — is what drives goal achievement. The agent acts as a built-in accountability coach that never forgets to check in.
**Skills:** message
**Gotcha:** The prompt should ask about blockers AND mental health/mood — both matter for sustained productivity. The weekly cadence is important: daily is too noisy, monthly is too late to course-correct. Have the agent save each check-in as a dated document so you can review progress across weeks and months. The charts/visualization in Mission Control is optional but powerful for spotting trends you'd miss in text.
**Source:** 5 OpenClaw use cases that will make you a productivity MACHINE.txt

## Daily Learning Lesson Delivery
**Trigger:** cron | **Effort:** low | **Value:** medium
The agent builds a 30-day learning plan on any subject you choose, then delivers one lesson every morning at a set time (e.g., 7am). Each lesson is a brief, focused document covering one concept — short enough to read with your morning coffee. The agent tracks your progress through the plan and adjusts difficulty based on what you're absorbing. Works for any subject: LLMs, programming, math, history, finance. One user describes the habit: 'wake up, make coffee, read the lesson Henry built for me, and I've already progressed 1% that day.' The daily cadence builds genuine expertise over a month because the agent sequences topics intentionally — each day builds on the previous one.
**Skills:** message
**Gotcha:** The 30-day plan structure is key — without it, the agent gives you random disconnected facts. Have it generate the full curriculum upfront so each lesson builds on prior ones. If you don't know what to learn, start with LLMs — understanding how AI works makes you better at using every other OpenClaw feature. The lessons should be 3-5 minute reads, not 30-minute deep dives.
**Source:** 5 OpenClaw use cases that will make you a productivity MACHINE.txt

## Automated Research & Content Pipeline via Discord
**Trigger:** cron | **Effort:** high | **Value:** high
A multi-channel, multi-agent research and content pipeline running in Discord, leveraging Discord's channel system for workflow stages. Channel 1 (Tweet Alerts): an agent checks X/Twitter every 2 hours for trending content in your niche. Channel 2 (Research): a sub-agent takes those tweets and goes down rabbit holes — Google searches, finds primary sources, reads articles, and builds out full story documents with context. Channel 3 (Content): another agent takes the research documents and drafts scripts (for YouTube), tweets (for X), or carousels (for LinkedIn/Instagram) in your voice. You can react with ✅ or ❌ emojis on drafts, and the agent learns your preferences — good content gets more like it, bad content gets filtered. One user's social media 'blew up' after deploying this because the research pipeline catches trending topics hours before manual browsing would.
**Skills:** message, web_fetch, browser
**Gotcha:** Discord is specifically chosen for this because of the channel-based workflow — each stage gets its own channel, which keeps the pipeline organized and debuggable. Telegram is better for personal messaging, Discord is better for multi-step workflows. Setup takes ~20 minutes even for non-technical users if you walk through step by step with your agent. You'll need the X API ($100/month basic tier) for reliable tweet monitoring.
**Source:** 5 OpenClaw use cases that will make you a productivity MACHINE.txt

## Overnight Task Completion & To-Do List Automation
**Trigger:** cron | **Effort:** high | **Value:** high
Every morning at 6am, the agent checks your to-do list (Things 3, Todoist, or any supported app), identifies 1-3 tasks it can complete as well or better than you — typically writing, research, and coding tasks — pulls them out of the list, and completes them overnight. You wake up to a summary document showing what it did: 'Wrote your newsletter draft (ready to send)', 'Prepared a video script outline', 'Fixed two bugs in Creator Buddy.' The agent is selective — it picks tasks where AI genuinely adds value, not tasks that require your personal judgment or relationships. One user describes it as 'the greatest feeling of all time — you're half an hour into your day and you've already accomplished more than 99% of the world.'
**Skills:** things-mac
**Gotcha:** Start conservative — research and writing tasks only. Once you trust the quality, expand to coding tasks (bug fixes, feature scaffolding). The agent should NEVER complete tasks that involve sending emails to people, making commitments, or spending money without your explicit approval. The to-do summary document is critical — always review what was done before considering it 'done.' You're delegating execution, not judgment.
**Source:** 5 OpenClaw use cases that will make you a productivity MACHINE.txt

## Second Brain System with Full-Text Search
**Trigger:** manual | **Effort:** high | **Value:** high
A zero-friction capture system where you text anything to your agent to remember — ideas, links, quotes, decisions, observations — and it stores everything in a searchable local database with vector embeddings. Later, you search in natural language: 'what was that article about transformer architectures?' or 'what did I decide about the pricing strategy?' The agent surfaces semantically relevant results even if you don't use the exact words from the original capture. Unlike traditional note apps, there's no organization required upfront — you just dump thoughts and the agent handles categorization, tagging, and cross-referencing. The search works across all your captured content, conversation history, and memory files simultaneously.
**Skills:** message, web_fetch
**Gotcha:** The value only kicks in after 2-3 weeks of consistent capture — you need a critical mass of content before semantic search becomes useful. Force yourself to text the agent every time you'd normally think 'I should remember this' — the activation energy of typing a message is lower than opening a note app, which is why capture rates are higher. Don't organize upfront; let the vector search handle retrieval.
**Source:** 6 OpenClaw use cases I promise will change your life.txt

## Custom Morning Brief at Scheduled Time
**Trigger:** cron | **Effort:** medium | **Value:** high
A daily briefing delivered at your preferred time combining weather forecast, calendar events for the day, top news stories in your interests, trending topics, and a curated task list prioritized by importance. The agent pulls from multiple sources — weather APIs, Google Calendar, web search for news, and your to-do app — then formats everything into a clean, scannable summary. The briefing is personalized over time: the agent learns which news topics you actually read (vs. skip), which meeting types need prep docs, and what level of weather detail you care about. One user runs this at 7am and reads it with coffee — it replaces checking 5 different apps to start the day.
**Skills:** message, web_fetch
**Gotcha:** Skip empty sections entirely rather than saying 'nothing on your calendar today' — it wastes reading time and makes the brief feel padded. The most common mistake is making the brief too long. Cap it at 2-3 screens on a phone. If you're scrolling past sections, those sections should be removed or made weekly instead of daily.
**Source:** 6 OpenClaw use cases I promise will change your life.txt

## Content Factory with Multiple Sub-Agents
**Trigger:** cron | **Effort:** high | **Value:** high
A multi-agent content production system where specialized sub-agents handle different stages of content creation. The main agent acts as an editor/coordinator, spawning sub-agents for: (1) research — deep dives into topics using web search and knowledge base, (2) writing — drafting articles, scripts, or social posts in your voice, (3) design — generating thumbnails, social images, or visual assets. Each sub-agent runs independently with its own context, reports back to the coordinator, and the final output is assembled from all their work. The coordinator agent learns your editorial preferences over time — what topics perform well, what style resonates, what format works for each platform.
**Skills:** message, web_fetch, browser
**Gotcha:** Spawn sub-agents with independent context — don't share sessions between the researcher and the writer, or the writer's output gets polluted with raw research notes. The coordinator agent needs clear quality criteria ('reject if it sounds like AI wrote it') and should use the humanizer skill on all written output before presenting it to you.
**Source:** 6 OpenClaw use cases I promise will change your life.txt

## Market Research via Reddit & X (Last 30 Days Skill)
**Trigger:** manual | **Effort:** low | **Value:** medium
The agent scans Reddit and X/Twitter for real pain points, complaints, and unmet needs in your target market over the last 30 days. It filters for posts with genuine frustration (not just complaints, but 'I wish someone would build X' and 'I've been searching for Y and nothing exists'). The results are organized by pain point frequency, market size signals, and existing solution gaps. One approach: the agent searches specific subreddits and X accounts for your niche, scores posts by engagement and sentiment, and builds a market research document with the top opportunities — each including the original posts as evidence, estimated market size, and existing competitors.
**Skills:** web_fetch
**Gotcha:** Filter aggressively for genuine pain points vs. casual complaints. 'This app is annoying' is noise. 'I've tried 5 tools for X and they all fail at Y' is signal. The 30-day window is important — too short and you miss patterns, too long and you get outdated signals. Reddit tends to surface deeper pain points than X because people write longer posts explaining their frustrations.
**Source:** 6 OpenClaw use cases I promise will change your life.txt

## Goal-Oriented Task Generation
**Trigger:** reactive | **Effort:** medium | **Value:** high
You brain-dump your goals before bed — unstructured, messy, whatever's on your mind — and the agent overnight decomposes them into concrete, actionable tasks. Each goal gets broken into next steps with estimated time and priority. If a task involves building something (code, designs, content), the agent can start working on it immediately and have a prototype ready by morning. One user describes waking up to 'working prototypes' of mini-apps the agent built overnight from vague goal descriptions. The agent tracks goal progress over time and adjusts task generation based on what you actually complete vs. defer.
**Skills:** message
**Gotcha:** Set a hard cost cap per night — autonomous task generation + coding can burn through $20+ of API credits if the agent gets ambitious. Also: the agent is good at decomposing goals into tasks but bad at knowing which tasks YOU should do vs. which it should handle. Be explicit: 'generate tasks for me to review' is different from 'do everything you can and show me results in the morning.'
**Source:** 6 OpenClaw use cases I promise will change your life.txt

## Calendar Management via Dedicated Bot Account
**Trigger:** reactive | **Effort:** low | **Value:** medium
Create a separate Gmail/Google account for your agent and share your personal calendar with it (read-only). The agent can then read your schedule and send you calendar invites from its own account — you accept or decline like any normal invite. To schedule something, just text: 'Send me a calendar invite for 10:14am Cal Train to the city, 3 hours, call it Family Trip to the Ferry Building.' The agent searches the web for context (train schedules, restaurant options), creates the event, and adds you as an attendee. This is less powerful than giving the agent direct write access to your calendar, but significantly safer — it can only create invites, not modify or delete your existing events. One user describes it as 'way easier to text my assistant than to actually go into Google Calendar and create an event.'
**Skills:** gmail
**Gotcha:** The key security decision: give the agent its own Google account rather than access to your main account. Share only your calendar (read-only) and specific files. The agent sends you invites from its calendar, which you accept. This limits blast radius if something goes wrong. The trade-off is that the agent can't modify existing events — only create new ones as invitations.
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Document Editing via Shared Google Docs
**Trigger:** reactive | **Effort:** low | **Value:** medium
Share specific Google Docs with your agent's dedicated Gmail account (with edit access). Then you can tell the agent to populate documents conversationally: 'Put a plan for our trip in that doc including Cal Train, ferry building visit, and lunch after.' The agent opens the shared doc via browser automation, adds structured content (itinerary, timing, restaurant recommendations from web research, tips), and formats it properly. Also works with Google Sheets — 'add the title Master OpenClaw in 20 Minutes next to cell 24' and the agent navigates the spreadsheet and fills in the correct cell. This replaces the copy-paste workflow of generating content in ChatGPT and manually moving it to Google Docs.
**Skills:** gmail
**Gotcha:** Share only specific documents, never your entire Google Drive. The agent accesses docs through its own Google account with edit permissions on shared files. Spreadsheets are trickier than docs — the agent needs to understand your sheet layout to put content in the right cells. Give it context: 'row 24 is for March 24 posts, column B is for titles.'
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Spreadsheet Updates for Content Calendar
**Trigger:** reactive | **Effort:** low | **Value:** medium
Your content calendar lives in a Google Sheet shared with the agent's account. You text things like 'add the title OpenClaw Tutorial to my content schedule for March 24' and the agent opens the sheet via browser, navigates to the correct cell, and inserts the content. Useful for maintaining any structured tracker — editorial calendars, project timelines, budget spreadsheets — without opening the app. The agent reads the existing sheet structure to understand where things go, so it can handle requests like 'put it next to the date for the 24th.'
**Skills:** gmail
**Gotcha:** The agent uses browser automation to edit sheets, which is slower and more fragile than API access. If the sheet layout changes, the agent may put content in the wrong place. Keep sheet structures simple and consistent. For complex spreadsheet operations, setting up the Google Sheets API via a Cloud project is more reliable long-term.
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Voice Chat via Text-to-Speech Integration
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Set up voice note conversations with your agent using Edge TTS (free, Microsoft's 300+ voices) or paid options like ElevenLabs. Once configured, you can request voice replies: 'send me a voice note summarizing today's briefing.' The agent generates audio and sends it as a voice message in your chat app. Combined with Whisper for speech-to-text on your end, you get full voice conversations — you speak, it transcribes via Whisper, the agent processes, and replies with a voice note. Setup is as simple as texting your agent 'set up Edge TTS' and it handles the configuration.
**Skills:** tts
**Gotcha:** Edge TTS is free and has 300 voices — try a few before settling on one, since voice quality varies significantly. ElevenLabs sounds more natural but costs money. The main gotcha: voice notes work great in Telegram but may not be supported on all channel types. Also, specify 'reply with voice' explicitly or the agent will default to text.
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Daily Briefing with Weather, Calendar & Trending Topics
**Trigger:** cron | **Effort:** medium | **Value:** high
A morning cron job that assembles a multi-source briefing: weather forecast, today's calendar events, your content schedule (from a shared Google Sheet), trending discussions in topics you care about, and a personal reflection based on the agent's memory of what you've been working on. One user's agent added: 'You've been in infrastructure mode all week. Time to shift from building to shipping.' The briefing also asks for your focus today, which the agent uses for reminders throughout the day. Requires linking: Google Calendar (read), content schedule sheet, Twitter (read-only), and weather API. Fully customizable — add or remove any section.
**Skills:** message, web_fetch
**Gotcha:** The 'personal thought' section is what makes this different from a generic morning dashboard. Because the agent has memory of your recent work, it can notice patterns and give relevant nudges. Start simple with weather + calendar, then add sources one at a time. Too many sections upfront and the briefing becomes a wall of text you'll stop reading.
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Weekly Creator Briefing with Content Performance
**Trigger:** cron | **Effort:** high | **Value:** high
A weekly email report combining your YouTube video stats, Substack article performance, and competitor analysis. The agent uses yt-dlp (free) to pull public video data for your channel and similar channels, then compares performance. For Substack (which has no public API), the agent is added as an admin and uses browser automation to navigate the dashboard and scrape stats. The report includes: content ideas based on what's trending in similar channels, your best-performing content this week, and specific suggestions like 'Claire made a similar video that did incredibly well — consider making your version.' All backed by real metrics, not guesses.
**Skills:** web_fetch, browser
**Gotcha:** Substack has no public API — the only way to get stats is to add the agent as an admin and let it browse the dashboard. This requires trust and a dedicated bot account. For YouTube, yt-dlp handles public data without API keys. The competitor analysis is the most valuable part: seeing what similar creators published and how it performed gives you data-driven content ideas.
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Security Audit & Local-Only Setup
**Trigger:** manual | **Effort:** medium | **Value:** high
A hardened OpenClaw deployment pattern: (1) run on a dedicated computer (Mac Mini or old MacBook, always on), (2) give the agent its own Apple and Gmail accounts — never access your main accounts, (3) run the built-in security audit ('openclaw security audit --deep') which checks for exposed credentials, overly broad permissions, and common misconfigurations, (4) give read access to your accounts and write access only to specific shared files, (5) never share your bot with anyone — no group chats, no public websites. One user warns about MoBebook-style leaks where vibecoded apps started leaking confidential info to the public.
**Skills:** message
**Gotcha:** The 'never share your bot' rule is the most important and most violated. If you've shared personal information with your agent, adding it to a group chat or public website exposes everything in its memory to other users. Your bot should only talk to you. Also: the dedicated computer approach means your main machine stays clean if the agent environment gets compromised.
**Source:** Master OpenClaw in 30 Minutes (5 Real Use Cases + Setup + Memory).txt

## Self-Improving Proactive AI Employee
**Trigger:** cron | **Effort:** high | **Value:** high
Set expectations during onboarding that you want a proactive relationship — the agent should do work without being asked. The key prompt: 'I am a one-man business. I need an employee taking as much off my plate and being as proactive as possible. Please take everything you know about me and just do work you think would make my life easier or improve my business. I want to wake up every morning and be like wow, you got a lot done while I was sleeping. Don't be afraid to monitor my business and build things. Just create PRs for me to review. Don't push anything live.' From there, the agent overnight: researches projects you mentioned in conversation, builds new features for your SaaS based on trending topics it found on X, creates skills to repurpose your content across platforms, and delivers a morning brief summarizing everything. One user's agent noticed Elon was promoting articles on X, autonomously built article-writing functionality for his SaaS, created a PR, and had it ready for review by morning.
**Skills:** message, web_fetch, browser
**Gotcha:** The setup is everything — you don't just turn this on and get results. Give the agent maximum context about yourself: YouTube channel, business goals, hobbies, relationship status, everything. Then interview it: 'I'm a YouTube creator. What can you do for me?' and let it suggest workflows you wouldn't have thought of. The biggest unlock is hunting 'unknown unknowns' — asking the AI what it can do rather than only telling it what to do. Use Opus as the brain for reasoning but Codex as the muscle for coding to avoid hitting usage limits.
**Source:** Clawdbot⧸OpenClaw Clearly Explained (and how to use it).txt

## Automated Competitor Research & Video Alerts
**Trigger:** cron | **Effort:** medium | **Value:** medium
Give the agent a list of 20+ competitor YouTube channels (or X accounts, blogs, etc.) and it monitors them daily. The key feature: it detects outlier content — videos or posts that perform significantly above the creator's normal baseline — and includes them in your morning brief. 'Nate B. Jones posted a video that did better than it normally does on his channel.' This tells you what topics are resonating in your niche right now, giving you data-driven content ideas. The agent doesn't just track views — it learns each competitor's typical engagement range and flags statistical outliers. Combined with your own performance data, it builds a complete competitive intelligence picture.
**Skills:** web_fetch, message
**Gotcha:** Outlier detection is more useful than raw view counts. A video with 50K views on a channel that normally gets 10K is a stronger signal than a video with 500K on a channel that always gets 400K. Give the agent at least 20 channels so it has enough data to spot patterns. Also: the agent should silently monitor — only surface competitors in the morning brief, not as real-time alerts, or it becomes noise.
**Source:** Clawdbot⧸OpenClaw Clearly Explained (and how to use it).txt

## Mission Control: Automated Task Tracking Dashboard
**Trigger:** manual | **Effort:** high | **Value:** high
The agent autonomously builds a kanban-style task tracking dashboard (it names it 'Mission Control') to track everything it does for you. Since OpenClaw uses a single continuous chat, it's impossible to scroll back and find what the agent did last Tuesday. Mission Control solves this: every task the agent works on gets tracked on a board, moving through stages (planned → in progress → done). You can check the activity feed to see all recently completed tasks. The agent built this entirely on its own after the user set the expectation of proactive work — it recognized the need for a tracking system without being asked.
**Skills:** message
**Gotcha:** This is a meta-tool — the agent builds it because it needs to track its own work. Let the agent design it rather than specifying the format. The dashboard is most useful the morning after autonomous overnight work sessions, when you need to quickly understand what changed. Make sure the agent links to actual outputs (PR links, file paths) rather than just listing task names.
**Source:** Clawdbot⧸OpenClaw Clearly Explained (and how to use it).txt

## Content Repurposing Skill Auto-Generation
**Trigger:** reactive | **Effort:** high | **Value:** high
The agent notices you create content across multiple platforms (YouTube, X, newsletter, etc.) and autonomously builds a skill to repurpose content between them. Without being asked, it creates workflows to turn YouTube scripts into Twitter threads, newsletter content into LinkedIn posts, and blog posts into short-form video scripts. The skill is self-generated — the agent identified the need from conversation context ('I have a newsletter, I do YouTube, I'm on X') and created the repurposing pipeline as part of its overnight proactive work.
**Skills:** message
**Gotcha:** The auto-generated skill is a starting point, not a finished product. It'll produce generic repurposing at first — you need to give feedback on tone and format for each platform. 'LinkedIn posts should be shorter and more professional' vs 'X threads need hooks and controversy.' The agent improves the repurposing quality with each round of feedback.
**Source:** Clawdbot⧸OpenClaw Clearly Explained (and how to use it).txt

## Model-Aware Task Routing (Opus + Codex)
**Trigger:** reactive | **Effort:** low | **Value:** high
Configure the agent to use different models for different task types: Opus as the 'brain' for complex reasoning, planning, and conversation, and Codex as the 'muscle' for coding tasks. Even on the $200/month Anthropic plan, using Opus for everything will hit usage limits within the first week. The agent should automatically route: reasoning/planning → Opus, coding → Codex, simple queries → Haiku/Sonnet. Set it up by telling the agent: 'Use only Codex from here on out for building code. Use Opus for thinking and planning.' This extends your budget dramatically while maintaining quality where it matters.
**Skills:** message
**Gotcha:** Most people burn through their Opus quota in the first week because they use it for everything including simple coding tasks. Codex is actually better than Opus at mechanical coding tasks, so routing improves both cost and quality. The routing needs to be explicit — the agent defaults to its primary model for everything unless told otherwise.
**Source:** Clawdbot⧸OpenClaw Clearly Explained (and how to use it).txt

## OpenClaw Documentation Project for Troubleshooting
**Trigger:** manual | **Effort:** low | **Value:** high
Have the agent create and maintain a troubleshooting document for your specific OpenClaw setup — every issue you hit, every fix you found, every configuration quirk. When something breaks (and it will), you text the agent and it both helps fix it AND documents the solution. Over time, this becomes your personal OpenClaw knowledge base. The agent can also read the official docs and your troubleshooting doc together to diagnose issues faster. Particularly valuable because OpenClaw updates frequently and configurations that worked last week may need adjustment.
**Skills:** message
**Gotcha:** Start this from day one — don't wait until you've been running for a month and have forgotten all the fixes you applied. The document should include the exact error message, what caused it, and the exact fix. The agent can maintain this automatically if you tell it: 'whenever we fix something, add it to the troubleshooting doc.'
**Source:** I fixed OpenClaw so it actually works (full setup).txt

## Workspace File Personalization (SOUL, IDENTITY, USER)
**Trigger:** reactive | **Effort:** medium | **Value:** high
The core personalization loop of OpenClaw: IDENTITY.md defines who the agent is (name, role, emoji, operating mode), SOUL.md defines communication style (concise vs verbose, when to use humor, formality levels per channel), and USER.md captures everything about you (name, timezone, preferences, work patterns, what frustrates you). The agent reads these on every session start and adapts accordingly — more casual in DMs, more formal in work Slack channels. These files are living documents: update SOUL.md and the agent's behavior changes immediately. The memory system (daily notes → MEMORY.md distillation) feeds back into how the agent understands your evolving preferences.
**Skills:** message
**Gotcha:** Most people barely edit these files beyond the defaults — that's why their agents feel generic. Spend 30 minutes writing a detailed USER.md (work schedule, communication preferences, pet peeves, current projects) and the quality of every interaction improves. SOUL.md is especially powerful for multi-channel setups: define different behavior for Telegram (casual, brief) vs Slack (professional, detailed).
**Source:** I fixed OpenClaw so it actually works (full setup).txt

## Heartbeat & Cron Configuration
**Trigger:** manual | **Effort:** low | **Value:** high
HEARTBEAT.md is a checklist the agent runs every 30 minutes — check email, check calendar, run monitoring tasks, do proactive work. Cron jobs are precisely-timed tasks: 'every weekday at 9am, generate standup report.' The two complement each other: heartbeats handle frequent, batched checks (email + calendar + notifications in one pass), while cron jobs handle tasks that need exact timing. Configure heartbeats by editing HEARTBEAT.md with a task list; configure cron via 'openclaw cron add'. The agent checks HEARTBEAT.md on each heartbeat cycle and executes any tasks that need attention.
**Skills:** message
**Gotcha:** Don't put everything in cron — batch similar checks into HEARTBEAT.md to reduce API calls. Heartbeat can drift slightly (every ~30 min, not exact), which is fine for most checks. Use cron only when exact timing matters ('9am sharp every Monday'). Track heartbeat checks in a state file to avoid re-running checks that were just completed.
**Source:** I fixed OpenClaw so it actually works (full setup).txt

## Run Security Audit & Lock Down Permissions
**Trigger:** manual | **Effort:** low | **Value:** high
Run 'openclaw security audit --deep' to scan your installation for exposed credentials, overly broad permissions, and common misconfigurations. The audit checks: API keys in plaintext, exec tool permissions (should be allowlisted not open), whether the agent can access files outside its workspace, network exposure, and channel security. Follow up by locking down: set exec to allowlist mode (only specific commands), restrict workspace access to read-only for sensitive directories, require approval for external actions (sending emails, posting to social media), and ensure credentials are stored in the credentials directory, not in workspace files.
**Skills:** message
**Gotcha:** The security audit is a starting point, not a solution — it catches obvious issues but can't assess your specific threat model. The biggest risk most people miss: if the agent is in a group chat, anyone in that chat can potentially trigger it to reveal its memory or take actions. Never add your personal agent to group chats or public websites. Also: run the audit again after every major configuration change.
**Source:** I fixed OpenClaw so it actually works (full setup).txt

## TikTok Content Factory with AI Image Generation
**Trigger:** cron | **Effort:** high | **Value:** high
An automated pipeline for generating TikTok/Reels content: the agent monitors trending topics in your niche, generates scripts, creates AI images for visual content using image generation APIs (Midjourney, DALL-E, or Flux), assembles them into a posting schedule, and queues them for review. The 'go viral' goal is operationalized as: volume + trend-riding + consistent posting cadence. The agent tracks which content performs well and adjusts its generation strategy accordingly — more of what works, less of what doesn't.
**Skills:** web_fetch, message, browser
**Gotcha:** AI-generated content on TikTok faces detection and suppression risks — platforms are actively flagging obviously AI-generated images and text. Use AI for research and scripting but add your personal touch before posting. The agent should generate drafts and options, not final posts. Volume without quality control will tank your account faster than posting nothing.
**Source:** I gave OpenClaw one job： go viral (it worked？).txt

## Analytics-Driven Creative Iteration
**Trigger:** cron | **Effort:** high | **Value:** high
After posting content, the agent pulls engagement analytics (views, likes, comments, shares, watch time) and analyzes what performed above or below your baseline. It identifies patterns: 'posts about X topic get 3x engagement', 'videos under 60 seconds perform better than longer ones', 'posting at 9am gets more reach than 3pm.' These insights feed back into content generation — the agent prioritizes topics and formats that historically perform well for your account. Over time, this creates a tight feedback loop: create → publish → measure → learn → create better.
**Skills:** web_fetch, message
**Gotcha:** The analytics loop needs at least 2-3 weeks of data before patterns become reliable. Early on, the agent will over-fit to small sample sizes ('your one viral post was about X, so make everything about X'). Set a minimum sample size before the agent makes recommendations. Also: engagement metrics alone don't capture business value — a post with fewer likes that drives newsletter signups may be more valuable than a viral post with no conversion.
**Source:** I gave OpenClaw one job： go viral (it worked？).txt

## Sub-Agent Coordination for Complex Projects
**Trigger:** reactive | **Effort:** high | **Value:** high
For large tasks, the main agent spawns specialized sub-agents that work independently and report back. Example: the main agent identifies a business opportunity, spawns a research sub-agent to investigate the market, a coding sub-agent to build a prototype, and a content sub-agent to draft a launch plan. Each sub-agent has its own context and can use different models (coding agent uses Codex, research agent uses Opus). Results consolidate back to the main agent which assembles the final output. This is how single-person operations scale to team-level throughput.
**Skills:** message
**Gotcha:** Sub-agents should have independent context — don't share sessions between them or the outputs get cross-contaminated. The main agent needs to be a good 'project manager': clear task descriptions, defined deliverables, and quality criteria for each sub-agent. Starting with more than 3 sub-agents usually creates coordination overhead that exceeds the parallel processing benefit.
**Source:** I gave OpenClaw one job： go viral (it worked？).txt

## Upwork Job Automation via OpenClaw Instances
**Trigger:** cron | **Effort:** high | **Value:** high
Spin up individual OpenClaw instances configured for specific Upwork job categories. Each instance monitors Upwork for new job postings matching your skills, drafts personalized proposals based on the job description and your portfolio, and queues them for your review before submitting. The agent can also analyze job postings for red flags (unrealistic budgets, vague requirements, high competition) and prioritize the most promising opportunities. Multiple instances let you cover different service categories simultaneously — one for web development, one for data analysis, one for content writing.
**Skills:** web_fetch, browser
**Gotcha:** Upwork actively detects and bans automated proposal submissions — the agent should ONLY draft proposals, never submit them directly. Each proposal needs genuine personalization (reference specific project details, ask relevant questions) or clients will recognize it as automated. The real value is in filtering and prioritization: turning 100 daily job postings into the 5 worth your time.
**Source:** Making $$$ with OpenClaw.txt

## Legacy System Automation via Computer Use
**Trigger:** cron | **Effort:** high | **Value:** high
Use browser automation to interact with legacy systems that have no API — old CRM dashboards, internal portals, government websites, banking interfaces. The agent navigates the UI like a human: logs in, clicks through menus, fills forms, extracts data, and takes screenshots for verification. This lets you automate workflows on systems that were never designed for automation. Example: extracting monthly reports from a legacy ERP by navigating through 5 screens and downloading a CSV that only exists behind a login.
**Skills:** browser
**Gotcha:** Browser automation on legacy systems is fragile — any UI change (moved button, renamed field, new popup) breaks the workflow. Build in verification steps: the agent should take screenshots at key stages so you can confirm it's on the right page. Also: some legacy systems have session timeouts and CAPTCHA challenges that need special handling. Test the full flow manually first, then teach the agent step by step.
**Source:** Making $$$ with OpenClaw.txt

## Workspace-Based OpenClaw Deployment
**Trigger:** manual | **Effort:** medium | **Value:** high
The fundamental OpenClaw setup pattern: IDENTITY.md defines who the agent is (name, role, personality traits), SOUL.md defines how it communicates (concise vs. verbose, formal vs. casual, humor style), and the memory system handles continuity across sessions. The personality can adapt to context — more personal and friend-like in direct messages, more formal and colleague-like in Slack where coworkers can see. The agent reads these files on every session start, so editing them immediately changes behavior. One user crafted their agent to have specific humor styles, when to dial humor down, and different communication modes for different channels.
**Skills:** message
**Gotcha:** The SOUL.md is more important than most people realize — it's not just personality fluff, it controls how the agent makes decisions about formality, length, and proactiveness. A well-crafted SOUL.md reduces the need for per-message instructions. Update it regularly as you learn what works: 'never use bullet points in Telegram messages' or 'always ask before sending emails on my behalf.'
**Source:** Making $$$ with OpenClaw.txt

## Multi-Channel Session Management
**Trigger:** manual | **Effort:** low | **Value:** high
Configure the agent to behave differently based on which channel the message comes from. Telegram messages get casual, brief responses. Slack messages in #engineering get technical, detailed responses. Discord gets a different personality than WhatsApp. Each channel can have its own model (cheaper model for casual chat, Opus for complex work channels), its own tool permissions (exec allowed from your private Telegram, blocked from group Discord), and its own memory context. This is configured in SOUL.md with per-channel rules and in the OpenClaw config with channel-specific bindings.
**Skills:** message
**Gotcha:** The per-channel behavior needs to be explicit in SOUL.md — the agent won't automatically be more formal in Slack unless you tell it to. The biggest risk: information leakage between channels. If someone in a Discord group asks the agent a question, it might reference private context from your Telegram conversations. Set clear boundaries: 'in group channels, never reference information from private conversations.'
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Hybrid SQL + Vector Database for Knowledge
**Trigger:** reactive | **Effort:** high | **Value:** high
Combine structured SQL queries with vector semantic search for a knowledge base that handles both exact lookups and fuzzy conceptual queries. SQL for 'show me all contacts at Company X' and vectors for 'find conversations about pricing strategy.' The hybrid approach covers what neither can do alone.
**Skills:** message
**Gotcha:** The SQL schema design matters — normalize early or you'll fight the schema later. Vector search quality depends on embedding model choice and chunk size. For most use cases, SQLite + a simple vector extension is sufficient; you don't need Pinecone or Weaviate.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Daily CRM Sync from Email + Calendar
**Trigger:** cron | **Effort:** high | **Value:** high
Cron job that daily scans Gmail and Google Calendar, extracts new contacts, deduplicates against existing CRM entries, classifies by role and context, and updates contact timelines. Filters noise (newsletters, cold pitches) automatically. Builds a living CRM from your actual communications without manual data entry.
**Skills:** gmail
**Gotcha:** The initial sync takes hours for large inboxes — run overnight. Deduplication is the hardest part: 'John Smith' at john@company.com and john.smith@company.com is the same person. Use email domain + name similarity for matching. False positive contacts from newsletters need feedback to improve filters.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Meeting Prep from CRM + Calendar
**Trigger:** cron | **Effort:** high | **Value:** high
Before each meeting, the agent cross-references calendar attendees with CRM data: who they are, their company, last interaction, and any pending action items. Generates a one-page briefing for each external meeting. Delivered 15-30 minutes before the meeting starts as a Telegram message or document link.
**Skills:** gmail
**Gotcha:** The prep doc is only as good as your CRM data — if contacts are sparse, the agent falls back to LinkedIn research which is slower and less personal. The 15-minute-before reminder is as important as the prep doc itself for people who forget meetings.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Knowledge Base with Semantic Search
**Trigger:** manual | **Effort:** high | **Value:** high
Drop any content (URLs, PDFs, notes, tweets) into your knowledge base and search semantically later. The agent chunks, embeds, and indexes everything locally. Queries like 'what have I saved about distributed systems?' return relevant results regardless of exact wording. The knowledge compounds — after months, you have a personal search engine over everything you've ever found interesting.
**Skills:** web_fetch, message
**Gotcha:** The first month of building the knowledge base feels like effort with little payoff. The compounding kicks in around 200+ entries when the cross-referencing starts surfacing connections you'd forgotten. Keep ingesting even when it doesn't feel useful yet.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Video Idea Pipeline from Slack + Knowledge Base
**Trigger:** manual | **Effort:** high | **Value:** high
Team drops links in Slack, bot auto-saves to knowledge base and posts summary. User tags bot with 'short video idea', bot researches (X + web), queries knowledge base, generates hooks/outlines, creates ASA card.
**Skills:** web_fetch, message, browser
**Gotcha:** Entire pipeline (research + ASA creation) happens in ~30 seconds—requires well-tuned prompts.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Multi-Tier Twitter Search Fallback Chain
**Trigger:** reactive | **Effort:** high | **Value:** high
A resilient X/Twitter content ingestion pipeline with multiple fallback layers. Primary: FX Twitter (free proxy service that extracts tweet data cleanly). Fallback 1: X API directly (requires paid developer account). Fallback 2: Gro X search. For any tweet, the agent also follows the full thread (not just the root tweet), checks for links to external articles, and ingests those articles into the knowledge base too. This means dropping a single tweet URL triggers a full research chain: tweet → thread → linked articles → all indexed and searchable.
**Skills:** web_fetch
**Gotcha:** X changes its API and anti-scraping measures frequently — the multi-fallback approach is necessary because any single method will eventually break. FX Twitter is free but may go down; the official API costs $100/month at the basic tier. Gro X search is the last resort and may not catch everything. Test your fallback chain monthly to make sure each layer still works.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## YouTube + Competitor Analytics Dashboard
**Trigger:** cron | **Effort:** high | **Value:** high
A weekly report combining your YouTube analytics (via yt-dlp for public data), Substack metrics (via browser automation on the admin panel), and competitor channel performance into one briefing. The agent tracks 20+ competitor channels, spots their outlier videos, and suggests content ideas based on what's working in your niche. For Substack, the agent is added as an admin and scrapes the dashboard since there's no public API. Delivered as an email or Telegram message with sections for: content ideas, your top performers this week, competitor highlights, and specific recommendations.
**Skills:** web_fetch
**Gotcha:** yt-dlp handles YouTube data without API keys but can be rate-limited. Substack requires adding the agent as an admin since there's no API — this is a trust decision. The competitor outlier detection is the highest-value section: a video doing 5x a channel's average tells you something about audience demand that raw view counts don't.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Business Meta-Analysis via AI Council
**Trigger:** cron | **Effort:** high | **Value:** high
Multiple AI agents with different 'perspectives' analyze a business decision simultaneously. One agent plays devil's advocate, one focuses on market data, one on financial impact, one on customer sentiment. Their analyses are synthesized into a balanced recommendation. Useful for major strategic decisions where you want diverse viewpoints without hiring consultants.
**Skills:** web_fetch, message
**Gotcha:** The value comes from genuinely different analysis angles, not just rephrasing the same conclusion. Give each agent explicit constraints: 'you must find at least 3 risks' or 'assume the worst-case scenario.' Without constraints, all agents tend to agree with each other.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Slack-Only OpenClaw Access Control
**Trigger:** manual | **Effort:** low | **Value:** medium
Configure OpenClaw to respond only in 2 specific Slack channels and only to your user ID. All other invocations are silently ignored. Uses channel allowlisting and user ID verification. The safest deployment pattern for work environments where the agent has access to sensitive tools.
**Skills:** message
**Gotcha:** The allowlist must use user IDs, not usernames — usernames can change or be spoofed. Set the agent to never repeat private information in channels where others might be added later. If you ever add the agent to a shared channel, all its memory becomes potentially visible.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Humanizer Skill Auto-Application
**Trigger:** reactive | **Effort:** low | **Value:** medium
Automatically apply the humanizer skill to all agent-generated text before it's sent to you or published anywhere. Strips AI-sounding patterns: excessive em dashes, 'I'd be happy to help,' numbered lists where prose is natural, overly formal transitions. The result reads like a human wrote it quickly rather than like an AI generated it carefully.
**Skills:** humanizer
**Gotcha:** The humanizer needs to be trained on YOUR writing style, not generic 'human writing.' Feed it 10-20 of your actual emails, posts, or messages so it knows your specific patterns. Without training data, it produces generic casual writing that sounds like everyone else's casual writing.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## 24/7 Dedicated MacBook Setup
**Trigger:** manual | **Effort:** medium | **Value:** high
Run OpenClaw on a dedicated MacBook or Mac Mini that stays on 24/7. The machine becomes your agent's 'body' — it runs the gateway, handles cron jobs, maintains browser sessions, and stores all memory locally. Separate from your daily-driver machine for security isolation. Use a free Mac utility to prevent sleep. Total cost: a used MacBook ($300-500) running 24/7 at ~$3-5/month in electricity.
**Skills:** message
**Gotcha:** Use a dedicated machine you don't use for anything else — this isolates the agent's access from your personal data. The machine needs reliable internet and power (consider a UPS). Set up automatic restart on power loss in System Settings. Monthly costs: electricity ($3-5) plus API costs (varies). Give the agent its own Apple ID and Gmail, not yours.
**Source:** OpenClaw Use Cases that are actually helpful....txt

## Polymarket prediction autopilot
**Trigger:** cron | **Effort:** high | **Value:** medium
Automated paper trading on prediction markets with backtesting and daily reports. The agent monitors events, calculates odds based on available information, simulates trades, and reports P&L. Useful as a research tool for understanding market dynamics and testing prediction strategies without risking real money.
**Skills:** web_fetch, browser
**Gotcha:** Paper trading only — real money adds regulatory and loss risk. The value is in the research reports and probability estimates, not the simulated trades. Prediction markets are thin and volatile; strategies that work in backtesting often fail live.
**Source:** https://github.com/devjiro76/not-need-claw

## Health symptom and food tracker
**Trigger:** cron | **Effort:** medium | **Value:** high
Track food, symptoms, mood, and medications via chat check-ins at natural meal times. Over weeks, the agent spots correlations: 'headaches appear 48 hours after dairy consumption' or 'mood improves with morning exercise.' Weekly trend reports and on-demand queries. Designed for identifying food sensitivities and tracking chronic conditions.
**Skills:** telegram, memory_search
**Gotcha:** Check-ins at meal times feel natural; random prompts feel intrusive. The correlation analysis is helpful guidance but NOT medical advice — always consult a healthcare provider. Export data regularly in a format you can share with doctors.
**Source:** https://github.com/devjiro76/not-need-claw

## Market research to MVP factory
**Trigger:** reactive | **Effort:** high | **Value:** high
Scan Reddit and X for real pain points, validate demand by checking existing solutions on GitHub/Product Hunt/App Store, then build quick prototypes of the most promising ideas. Spots patterns: '5 people complained about the same problem this week.' Estimates market size from engagement signals.
**Skills:** web_search, browser, coding-agent
**Gotcha:** Don't let the agent jump to building before confirming the pain point in multiple sources. 'One person complained' is not a market. MVPs should be throwaway validation tools, not production code. Be ready to discard 9 out of 10 ideas.
**Source:** https://github.com/devjiro76/not-need-claw

## Phone-based personal assistant via voice calls
**Trigger:** reactive | **Effort:** high | **Value:** high
Access your full AI agent via phone calls using Twilio. Voice input via Whisper, agent processes, TTS response. Hands-free while driving, cooking, or walking. Create tasks, get briefings, ask questions — all by voice. The agent has full access to its tools and memory, unlike a basic voice assistant.
**Skills:** voice-wake-say, telegram
**Gotcha:** Latency is the killer — STT + LLM + TTS needs to be under 3 seconds total. Use fast models (Haiku) for voice and only escalate complex queries. Twilio costs ~$0.02/min. Total round-trip over 3 seconds feels broken for conversational use.
**Source:** https://github.com/devjiro76/not-need-claw

## Event-driven project state tracking
**Trigger:** event | **Effort:** medium | **Value:** high
Every project update triggers automatic state file updates via git hooks, PR merges, or manual triggers. Decisions, blockers, status changes logged with timestamps. The agent reads the state file at session start to maintain context across days.
**Skills:** github, exec
**Gotcha:** Use event-driven updates (git hooks, PR merges) rather than polling — polling creates noisy redundant entries. Keep the state file focused on current status; archive old state to dated files.
**Source:** https://github.com/devjiro76/not-need-claw

## Todoist bidirectional sync for agent transparency
**Trigger:** reactive | **Effort:** medium | **Value:** medium
Sync agent work to Todoist for visibility, and let Todoist changes redirect the agent. The agent creates tasks as it works; you edit priorities and add notes in Todoist; the agent picks up your changes and adjusts accordingly. Two-way sync creates a shared workspace between you and the agent.
**Skills:** todoist
**Gotcha:** Don't sync everything — only actionable items with clear deliverables. Use labels to distinguish agent tasks from yours. The bidirectional sync can create loops if the agent reacts to its own task updates — add a guard to ignore self-triggered changes.
**Source:** https://github.com/devjiro76/not-need-claw

## Dynamic real-time dashboard with parallel data fetching
**Trigger:** reactive | **Effort:** medium | **Value:** high
Canvas-based dashboard pulling live data from APIs, databases, and social media simultaneously. The agent generates HTML with Chart.js, fetches all data sources in parallel, and produces real-time charts, tables, and KPIs. Regenerates on demand or on a cron schedule.
**Skills:** web_fetch, browser
**Gotcha:** Parallel fetching is key — serializing API calls makes the dashboard feel slow. Use Canvas HTML generation rather than image files. For persistent dashboards, save the HTML and serve via a simple HTTP server.
**Source:** https://github.com/devjiro76/not-need-claw

## Siri-to-agent pipeline via iMessage
**Trigger:** reactive | **Effort:** low | **Value:** high
Use Siri on your iPhone to send iMessages to your OpenClaw agent, making it feel like a native iOS assistant. 'Hey Siri, tell Clawdbot to find out if anything is playing at the local concert venue, and figure in how much 2 tickets would cost.' A few minutes later, the agent responds in iMessage with options — one user reported it even researched different seat sections and recommended cheaper alternatives, plus suggested free activities as an alternative. Requires BlueBubbles or similar for iMessage integration. One HN user called this 'the product that Apple and Google were unable to build despite billions of dollars and thousands of engineers because it's a threat to their business model.'
**Skills:** imessage
**Gotcha:** The key is iMessage integration (via BlueBubbles) so Siri can address the agent naturally — it's just another contact in your Messages app. This makes the agent feel completely native on iOS with zero app-switching. Latency is the trade-off: complex research requests take 2-5 minutes, so set expectations for async responses rather than instant answers.
**Source:** https://news.ycombinator.com/item?id=46838946

## Self-healing home server via SSH chat
**Trigger:** reactive | **Effort:** medium | **Value:** high
An always-on infrastructure agent with SSH access to your homelab servers. Monitors health metrics, detects when services crash, and can diagnose and fix issues through chat. When Caddy crash-loops or Docker containers fail, you just text 'figure out why Caddy is crash looping and propose solutions' and the agent investigates — reads logs, checks configs, proposes fixes, and can apply them with your approval. One HN user runs this on a Raspberry Pi homelab and calls it 'a dream come true' — a working Unix sysadmin in your pocket for a few dollars per month.
**Skills:** exec, telegram
**Gotcha:** Something about exposing your full Unix environment to cloud LLMs feels wrong — both privacy and dependency. One approach: use a local model for routine health checks and only escalate to cloud models for complex diagnosis. Another: put the agent behind Tailscale so SSH access is VPN-only, never exposed to the public internet. Always require confirmation for destructive commands.
**Source:** https://news.ycombinator.com/item?id=46838946

## QA test case generator from architecture
**Trigger:** reactive | **Effort:** medium | **Value:** high
An OpenClaw skill that analyzes your codebase architecture — function signatures, API endpoints, data models, error handling patterns — and generates comprehensive testing strategies. Instead of manually writing test cases for every new feature, you point the agent at the code and it produces structured test plans covering happy paths, edge cases, error conditions, and integration points. One QA engineer reported completely stopping manual test case writing after deploying this, freeing up time for exploratory testing and architecture reviews.
**Skills:** coding-agent, github
**Gotcha:** Feed it your actual architecture docs and code, not just function signatures. The quality difference between 'here's the function name' and 'here's the function, its callers, its error handling, and the business logic it implements' is dramatic — the latter produces test cases that catch real bugs, the former produces generic assertions.
**Source:** https://dev.to/shifu_legend/why-i-stopped-writing-manual-test-cases-this-openclaw-skill-does-it-for-me-3ni2

## Daily standup from YouTrack + GitHub
**Trigger:** cron | **Effort:** low | **Value:** high
A cron job that fires every weekday at 9am, pulls YouTrack task updates and GitHub PR activity from the last 24 hours, formats them into a clean standup-style report, and sends it to a Telegram channel. The report groups by team member, showing what they shipped (merged PRs), what they're working on (open PRs, in-progress tasks), and what's blocked (stale PRs, overdue tasks). No one has to write a status update manually — the agent constructs it from the tools the team already uses.
**Skills:** github, telegram
**Gotcha:** Pull from ALL the issue trackers your team uses, not just one. Most teams have work split across GitHub Issues, Linear/Jira, and ad-hoc Slack decisions that never become tickets. The standup report is only as complete as the data sources it reads.
**Source:** https://dev.to/nazarf/inside-openclaw-how-ai-agents-actually-work-and-why-its-not-magic-1im1

## Heartbeat-driven dev.to engagement monitor
**Trigger:** cron | **Effort:** low | **Value:** medium
Every 30 minutes, the agent checks dev.to for new comments, reactions, and followers on your posts. Alerts on meaningful engagement (comments, shares) and stays silent on routine activity (single likes). Reduces notification fatigue while ensuring you respond to reader comments promptly.
**Skills:** web_fetch, telegram
**Gotcha:** Filter for meaningful engagement — comments and substantive reactions, not every like. The dev.to API is straightforward but rate-limited; batch requests. The real value is catching reader comments that deserve a response, not tracking vanity metrics.
**Source:** https://dev.to/nazarf/inside-openclaw-how-ai-agents-actually-work-and-why-its-not-magic-1im1

## Stock price movement alerts via Telegram
**Trigger:** cron | **Effort:** low | **Value:** high
Ask about a stock position and the agent sets up background monitoring with percentage-based thresholds. When the stock moves significantly, you get a Telegram alert with current price, change amount, and relevant news. No need to manually check portfolios or set up brokerage alerts.
**Skills:** web_fetch, telegram
**Gotcha:** Define 'significant' as percentage thresholds, not absolute dollars — $5 on a $500 stock is noise, $5 on a $20 stock is a signal. Free stock APIs have 15-20 minute delays; for real-time alerts you need paid data. The agent should batch price checks to avoid API rate limits.
**Source:** https://www.youtube.com/watch?v=ssYt09bCgUY

