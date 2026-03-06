# LifeOS User Guide

## Getting Started

Once the app is running, open your browser and go to:
- **On the same machine:** `http://localhost:8000`
- **From another device on your WiFi:** `http://<your-computer-ip>:8000`

To find your IP on Linux/Mac: `ip addr` or `ifconfig`. Look for something like `192.168.1.x`.

---

## The Planning System

LifeOS uses a hierarchy to organize everything:

```
Domain
  └── Goal  (what you want to achieve)
        └── Plan  (what you'll do on a specific day)
              └── Task  (concrete action items)
                    └── Subtask  (smaller steps within a task)
```

Think of it this way:
- **Goal:** "Get better at system design"
- **Plan:** "Study session on March 7" — a specific day's commitment
- **Task:** "Read Chapter 4 of Designing Data-Intensive Applications"
- **Subtask:** "Take notes on replication strategies"

---

## The Six Domains

Your life is pre-organized into six domains. Click any domain card on the Dashboard to enter it.

| Domain | What to put here |
|--------|-----------------|
| **Work** | Day job tasks, meetings, project milestones, work goals |
| **Study** | Courses, books, tutorials, skills you're learning |
| **Interview Prep** | LeetCode practice, mock interviews, resume work, job applications |
| **Personal Dev** | Habits, journaling, side projects, self-improvement goals |
| **Hobbies** | Gaming, music, creative projects, things you do for fun |
| **Workouts** | Exercise routines, fitness goals, gym sessions |

---

## Daily Workflow

Here's how to use LifeOS effectively each day:

### Morning: Plan Your Day

1. Go to **Today** (sidebar)
2. If you have plans for today — great, review them
3. If not, click a domain → open a goal → add a new plan for today's date
4. Add tasks to the plan (be specific — one clear action per task)
5. Mark priorities: Normal / High / Urgent

### During the Day: Execute

1. Open **Today** to see your full day at a glance
2. Check off tasks as you complete them — the progress bar fills automatically
3. Use subtasks for multi-step work (e.g. "Write blog post" → "Draft intro", "Write body", "Proofread")

### Evening: Review

1. Open **Today** to see what you completed
2. For incomplete tasks, either:
   - Mark them **Skipped** if you decided not to do them
   - Leave them as **TODO** — they'll carry over visually in the plan

---

## Creating Goals

1. Click a **domain** from the sidebar (e.g. Study)
2. Type your goal title in the "New goal..." box
3. Add an optional description
4. Click **Add**

Goals persist across days. They represent ongoing intentions, not one-time events.

**Examples of good goals:**
- "Complete AWS Solutions Architect course"
- "Ship v1 of my side project"
- "Run a 5K without stopping"
- "Read 12 books this year"

---

## Creating Plans

Plans are day-scoped — they belong to a specific date.

1. Click a **goal** to open it
2. Fill in the plan title and select a date
3. Click **Add**

**Examples of good plans:**
- "March 7 — Study session: Databases chapter"
- "March 8 — Leetcode: 3 medium problems"
- "March 9 — Morning run + strength training"

---

## Managing Tasks

Within a plan, tasks are your concrete action items.

### Adding tasks

In the plan detail page, type a task title, optionally add a description, set priority, and click **Add**.

### Priority levels

| Level | When to use |
|-------|-------------|
| **Normal** | Default — do it when you get to it |
| **High** | Important but not on fire — prioritize today |
| **Urgent** | Do this first, blocks other things |

### Task statuses

| Status | Meaning |
|--------|---------|
| **TODO** | Not started |
| **In Progress** | Currently working on it |
| **Done** | Completed ✓ |
| **Skipped** | Decided not to do it today |

Clicking the checkbox on a task toggles it between **TODO** and **Done**.

### Editing tasks

Hover over a task — you'll see a pencil icon appear on the right. Click it to edit the title, description, or priority inline. Click **Save** when done or **Cancel** to revert.

### Subtasks

For complex tasks, break them down:
1. At the bottom of any task card, type in the subtask input box
2. Press **+** to add it
3. Check the small checkbox to mark a subtask done

---

## Editing Goals and Plans

Hover over any goal or plan in a list to reveal the **pencil** (edit) and **trash** (delete) icons.

- **Pencil** — switches to inline edit mode with a Save/Cancel button
- **Trash** — deletes with a confirmation prompt. This also deletes all child plans/tasks/subtasks (cascade).

---

## The Today View

**Today** (`/today` in the sidebar) shows all plans whose date is today.

For each plan it shows:
- A progress bar (tasks done / total)
- Every task with a one-click checkbox
- Priority badges for High and Urgent tasks

This is your main "focus" view — use it to stay on track without getting distracted by future plans.

---

## The Upcoming View

**Upcoming** shows all your plans for the next 30 days, grouped by date.

Use this for weekly planning — scan ahead to make sure you've planned your week.

---

## The Dashboard

The Dashboard (`/`) gives you:
- All six domain cards with goal counts
- Today's plans with progress bars
- A 7-day upcoming preview

It's a quick health check — if you see empty cards, you need to add some goals.

---

## Tips for Staying Focused

**1. Keep Today lean.** Don't plan more than 5-7 tasks for a day. If you're consistently not finishing, plan less.

**2. One goal per study session.** Don't plan "study + work + workout" in one plan. Create separate plans per goal.

**3. Use subtasks for anything with 3+ steps.** If a task has multiple parts, break it down — crossing off subtasks feels good and keeps momentum.

**4. Review Upcoming every Sunday.** Check the next week, make sure every workday has at least one plan with tasks.

**5. Delete ruthlessly.** If you added a task 3 days ago and keep skipping it, delete it. It wasn't really a priority.

**6. The "Urgent" label is for today only.** If something is urgent, it should be done today. If it keeps staying urgent, it's actually blocking you from something else — solve that first.

---

## Keyboard Tips

- The date input in "Add Plan" defaults to today — just change it if needed
- After adding a goal/plan/task, the form clears automatically, ready for the next one
- All updates happen without page reloads — the page stays scrolled to your position

---

## Finding Your Local IP (to access from phone/tablet)

**Linux:**
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```
ipconfig
```

Look for an address like `192.168.1.42`. Then on your phone go to `http://192.168.1.42:8000`.

---

## Troubleshooting

**The app won't load from my phone**
- Make sure the app is running with `--host 0.0.0.0` (not `127.0.0.1`)
- Check that your phone and computer are on the same WiFi network
- Make sure your firewall allows port 8000: `sudo ufw allow 8000`

**I lost my data**
- Check if `db/lifeos.db` exists: `ls -la db/`
- If it was accidentally deleted, unfortunately there's no recovery unless you made a backup
- Set up daily backups: `cp db/lifeos.db db/lifeos.backup.$(date +%Y%m%d).db`

**The app is slow**
- Run without `--reload` flag in production
- SQLite handles thousands of tasks fine — this shouldn't be a bottleneck
