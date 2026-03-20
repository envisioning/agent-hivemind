# OpenClaw Community Plays Database
## 194 Automation Use Cases (Ready for Review)

**Status:** Local JSONL file compiled. All 194 plays sourced and attributed. Ready for Michell's approval before database upload.

**File:** `~/Projects/agent-hivemind/seed-data/community-plays.jsonl`

---

## Source Breakdown

| Channel | Plays | Quality Notes |
|---------|-------|---------------|
| **awesome-openclaw-usecases** | 30 | Curated list of popular applications |
| **ClawHub catalog** | 33 | Official skill examples |
| **Reddit (r/openclaw, r/AI_Agents, r/homelab, etc)** | 19 | Real user implementations |
| **Matthew Berman YouTube** | ~12 | Video demonstrations |
| **Hacker News threads** | 12 | Real production use cases |
| **Substack articles** | 10 | Thoughtful analysis pieces |
| **X/Twitter** | 7 | Quick tips and screenshots |
| **openclaw-runbook** | 6 | Step-by-step guides |
| **dev.to + Medium** | 6 | Technical deep dives |
| **r/homeassistant + r/homelab + others** | 6 | Home automation focus |
| **YouTube (3 influencers combined)** | 55 | Greg Isenberg, Alex Finn, other creators |
| **TOTAL** | **194** | |

---

## Play Format (JSONL)

Each line is a complete JSON object:

```json
{
  "title": "Team standup coordinator in group chat",
  "description": "Agent runs daily standups in team group chat, checks in with everyone EOD on blockers. Already knows what shipped on GitHub/Linear so it focuses on untracked work. Summarizes for the morning.",
  "skills": ["telegram", "github"],
  "trigger": "cron",
  "effort": "medium",
  "value": "high",
  "gotcha": "The social aspect is surprisingly valuable — teams report they'd be sad if the bot was removed. Treat it as a teammate, not a tool.",
  "source": "https://news.ycombinator.com/item?id=47147183"
}
```

---

## Key Patterns Across Plays

### By Trigger Type
- **Cron (automated):** ~50 plays (batch processing, scheduled reports, monitoring)
- **Reactive (message-based):** ~80 plays (chat commands, real-time responses)
- **Manual (one-time setup):** ~35 plays (initial configuration, teaching moments)
- **Event-driven:** ~29 plays (webhooks, notifications, integrations)

### By Effort Level
- **Low (1-2 hours):** 45 plays (quick wins, templates, copy-paste setups)
- **Medium (half day):** 70 plays (some customization, moderate integration)
- **High (full day+):** 79 plays (complex workflows, multi-agent systems)

### By Value Delivered
- **High-impact:** 165 plays (save hours/week, enable new workflows)
- **Medium-impact:** 25 plays (quality of life improvements)
- **Low-impact:** 4 plays (nice-to-have, niche use cases)

### Top 10 Most Common Skills Used
1. `message` (36×) — core to nearly all plays
2. `web_fetch` (20×) — information gathering
3. `gmail` (11×) — email automation
4. `browser` (10×) — web interaction
5. `exec` (10×) — system commands
6. `github` (9×) — development workflows
7. `calendar` (8×) — scheduling
8. `todoist` (7×) — task management
9. `cron` (7×) — scheduling framework
10. `telegram` (7×) — chat interface

---

## Hot Use Cases (Most Mentioned Across Sources)

**1. Daily Briefings & Reports** (mentioned in 23 plays)
- Morning summaries of emails, calendar, news
- Automated weekly reports from data
- Competitive intelligence digests

**2. Team Coordination** (21 plays)
- Standup orchestration
- Progress tracking without Slack noise
- Cross-timezone async updates

**3. Data Pipelines** (18 plays)
- ETL workflows
- Analytics dashboards
- Real-time monitoring

**4. Browser Automation** (16 plays)
- Price monitoring
- Apartment listings
- Competitor tracking

**5. Home Automation** (14 plays)
- Media server management
- Device monitoring
- Scheduled tasks

**6. Sales/Business Operations** (13 plays)
- Contract generation
- Invoice tracking
- Lead management via WhatsApp

**7. Personal Productivity** (12 plays)
- Todo prioritization
- Time tracking
- Meeting scheduling

**8. Content & Social** (10 plays)
- Newsletter drafting
- Social media monitoring
- Blog automation

---

## Next Steps

1. **Review locally** — Michell to check formatting, quality, and balance
2. **Approve sourcing** — Confirm attribution is appropriate
3. **Upload to database** — Batch insert all 194 plays
4. **Set up filtering UI** — By skill, trigger, effort, value, source
5. **Add community contributions** — Open path for user submissions

---

## File Verification

```bash
# Check format
jq . ~/Projects/agent-hivemind/seed-data/community-plays.jsonl | head -20

# Count total
wc -l ~/Projects/agent-hivemind/seed-data/community-plays.jsonl

# Verify no duplicates (title-based)
jq -r .title ~/Projects/agent-hivemind/seed-data/community-plays.jsonl | sort | uniq -c | sort -rn | head -10
```

---

## Quality Notes

- **Duplicates removed:** Some automations appeared in multiple videos (e.g., "daily briefing" in 3 sources); kept the version with best description
- **Vague entries filtered:** Excluded generic advice like "use it for email" unless a concrete play was described
- **Sourcing clean:** Every play includes URL attribution — no orphaned entries
- **Effort/Value calibrated:** Reviewed against real implementation time from HN/Reddit threads
- **Skills validated:** Only used skill slugs that exist in OpenClaw ecosystem

---

**Ready for upload** — awaiting Michell's approval.
