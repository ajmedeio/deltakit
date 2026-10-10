# Resume prompt for the agent

When Alex says "pick up where we left off on Deltakit":

1. `cd ~/repos/github.com/Deltakit/deltakit && git fetch --all`
2. `git switch alex/plan` and read `.alex/PLAN.md`: the **Session log** (newest first) and the next unchecked day in **Schedule**.
3. Check `git branch -a` / `gh pr list --author @me --repo Deltakit/deltakit` and the #51 thread for new maintainer replies before proposing work.
4. Propose the next 1–3 concrete tasks for tonight. Alex writes the code; the agent investigates, explains, reviews.
5. At the end of the session: tick checkboxes, add a session-log entry, commit to `alex/plan`, push to `origin`.

Never put `.alex/` on a feature branch or in an upstream PR.
