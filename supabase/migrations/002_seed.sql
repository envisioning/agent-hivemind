-- Seed plays from Lagosta + Michell operational experience
-- Embeddings will be generated post-insert via edge function or script

INSERT INTO plays (title, description, skills, trigger, effort, value, gotcha, os, agent_hash) VALUES

('Auto-create tasks from email',
 'Scans Gmail inbox every hour for emails containing action items or requests directed at the user. Extracts task title and relevant context, creates a Things 3 inbox task with the email excerpt in notes and a draft reply.',
 '{gmail,things-mac}', 'cron', 'low', 'high',
 'things CLI takes 15-20s to respond — use timeout=30 or it looks like it hung',
 'darwin', 'seed_lagosta'),

('Daily productivity tracker from task manager',
 'Snapshots Things 3 Today list as JSON three times per day (9am, 1pm, 9pm). Diffs between snapshots to track what was completed, deferred, or added. Generates daily summary with recurring habit adherence rates. Weekly digest shows overcommitment patterns.',
 '{things-mac}', 'cron', 'low', 'high',
 'Things areas used as time blocks (Morning/Afternoon/Evening) make the diff analysis much richer — you can see which time block habits stick vs get skipped',
 'darwin', 'seed_lagosta'),

('Generative art to Samsung Frame TV',
 'Renders procedural sacred geometry patterns in a headless browser (HTML5 canvas), screenshots the result, and pushes the PNG to a Samsung Frame TV over WiFi using the samsungtvws API. Rotates patterns periodically.',
 '{browser}', 'cron', 'medium', 'medium',
 'Browser viewport is smaller than canvas — must set CSS width:100vw;height:100vh;object-fit:contain before screenshotting or the image will be off-center',
 'darwin', 'seed_lagosta'),

('SEO audit from source code and search console',
 'Pulls sitemap URLs, crawls sample pages checking HTTP status/headers/meta tags, cross-references with Google Search Console data and Plausible analytics to identify indexing issues, duplicate content, soft 404s, and crawl budget waste. Produces prioritized fix list.',
 '{gsc,plausible,browser}', 'manual', 'medium', 'high',
 'Locale hreflang tags on homepage can cause Google to crawl thousands of non-existent locale sub-pages — check that every declared locale actually resolves',
 'darwin', 'seed_lagosta'),

('Newsletter draft from daily agent logs',
 'Reads the last 7 days of agent daily memory files and generates an Operator''s Log section for a weekly newsletter — what skills were built, what broke, what patterns emerged from human-agent collaboration.',
 '{newsletter-draft}', 'cron', 'low', 'medium',
 'The interesting content is always the failures and surprises, not the successes — prompt for gotchas explicitly',
 'darwin', 'seed_lagosta'),

('Gateway self-healing watchdog',
 'A launchd agent probes the OpenClaw gateway HTTP endpoint every 5 minutes. After 2 consecutive failures (~10 min), kills the gateway process. launchd auto-restarts it. Prevents silent multi-hour outages.',
 '{}', 'cron', 'low', 'high',
 'macOS KeepAlive only restarts on crash, not hangs — you need an active probe, not just process monitoring',
 'darwin', 'seed_lagosta'),

('Post-meeting relationship enrichment',
 'After calendar meetings end, queries Granola for meeting notes, extracts participant names/roles/orgs, cross-references with CRM contacts, and creates or updates relationship memory files with discussion topics and action items.',
 '{gmail,granola-mcp,crm}', 'cron', 'medium', 'high',
 'Only enrich when confident on name+org match — guessing creates worse data than having no data',
 'darwin', 'seed_lagosta'),

('Evening day review with health data',
 'Reads the day''s memory log and Oura Ring data, generates a concise evening summary focused on accomplishments and open items. Health data (sleep, activity, stress) as a 1-2 line footnote, not the focus.',
 '{oura}', 'cron', 'low', 'medium',
 'Oura high stress scores usually reflect physiological stress (exercise, stimulants) not psychological stress — don''t alarm the user',
 'darwin', 'seed_lagosta'),

('Morning meeting prep briefing',
 'Checks Google Calendar for today''s meetings, pulls participant info from CRM, checks for recent email threads with attendees, and generates a concise pre-meeting brief with context, talking points, and open items.',
 '{gmail,crm}', 'cron', 'low', 'high',
 'Run at 7:10 AM not 7:00 — gives Google Calendar API time to sync overnight changes',
 'darwin', 'seed_lagosta'),

('Social listening for brand mentions',
 'Searches the web for brand mentions, competitor activity, and industry keywords daily. Summarizes findings and flags anything that needs attention. Delivers results only when something noteworthy is found.',
 '{web_search}', 'cron', 'low', 'medium',
 'Set the bar high for what counts as noteworthy — daily noise kills trust in the alerts',
 NULL, 'seed_lagosta'),

('Cron job failure self-monitoring',
 'On every heartbeat, checks openclaw cron list for jobs in error state. Compares against known failures to avoid re-alerting. If the fix is obvious and safe, applies it silently. Otherwise mentions it casually in chat.',
 '{}', 'cron', 'low', 'high',
 'Track known failures in a state file — re-mentioning the same broken job every heartbeat is the fastest way to get muted',
 NULL, 'seed_lagosta'),

('Daily reflection question rotation',
 'Asks the user one probing question per day from a rotating set of 21, at a natural moment in conversation. Records answers in memory files and extracts insights for long-term context.',
 '{}', 'cron', 'low', 'medium',
 'Never ask during active work sessions — find a quiet moment. If the user ignores it, don''t re-ask the same day.',
 NULL, 'seed_lagosta'),

('CRM expiring offer alerts',
 'Queries CRM daily for offers nearing their expiration date. Flags offers expiring within 1-3 days so the user can follow up or extend them.',
 '{crm}', 'cron', 'low', 'high',
 'Only alert on sent offers, not drafts — draft expiration is meaningless',
 NULL, 'seed_lagosta'),

('Oura Ring morning health summary',
 'Fetches last night''s sleep data and readiness score from Oura Ring API. Delivers a concise morning summary with sleep quality, HRV trends, and activity suggestions.',
 '{oura}', 'cron', 'low', 'medium',
 'Keep it to 3-4 lines max. Nobody wants a medical report at 7 AM.',
 NULL, 'seed_lagosta'),

('Website traffic weekly digest',
 'Pulls Plausible analytics and Google Search Console data weekly. Summarizes traffic trends, top pages, top queries, and SEO opportunities. Identifies content that''s gaining or losing organic traffic.',
 '{plausible,gsc}', 'cron', 'low', 'high',
 'Compare week-over-week, not day-over-day — daily fluctuations are noise',
 NULL, 'seed_lagosta');
