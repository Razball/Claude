#!/usr/bin/env python3
"""GoHighLevel MCP Server — connects Claude Code to the GHL v2 API."""

import os
from typing import Optional
from datetime import datetime, timezone, timedelta
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL     = os.getenv("GHL_BASE_URL", "https://services.leadconnectorhq.com")
API_KEY      = os.getenv("GHL_API_KEY") or os.getenv("GHL_ACCESS_TOKEN")
LOCATION_ID  = os.getenv("GHL_LOCATION_ID")
API_VERSION  = "2021-04-15"
CHARACTER_LIMIT = 25_000

if not API_KEY:
    raise RuntimeError("Set GHL_API_KEY (or GHL_ACCESS_TOKEN) in your .env file.")

mcp = FastMCP("gohighlevel")

# ── Shared HTTP helper ────────────────────────────────────────────────────────

def _headers() -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Version": API_VERSION,
        "Content-Type": "application/json",
    }


async def _get(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        r = await client.get(path, headers=_headers(), params=params or {})
        r.raise_for_status()
        return r.json()


async def _post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        r = await client.post(path, headers=_headers(), json=body)
        r.raise_for_status()
        return r.json()


async def _put(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        r = await client.put(path, headers=_headers(), json=body)
        r.raise_for_status()
        return r.json()


async def _delete(path: str) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        r = await client.delete(path, headers=_headers())
        r.raise_for_status()
        return r.json()


def _truncate(text: str) -> str:
    if len(text) > CHARACTER_LIMIT:
        return text[:CHARACTER_LIMIT] + "\n...[truncated]"
    return text


def _loc() -> str:
    if not LOCATION_ID:
        raise ValueError("GHL_LOCATION_ID is not set in .env")
    return LOCATION_ID


# ── CONTACTS ─────────────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
async def search_contacts(
    query: str = Field(description="Name, email, or phone to search for"),
    limit: int = Field(default=20, ge=1, le=100, description="Number of results (1-100)"),
) -> str:
    """Search contacts in GoHighLevel by name, email, or phone number.

    Returns a summary list. Use get_contact for full details on a specific contact.
    """
    data = await _get("/contacts/search", {"locationId": _loc(), "query": query, "limit": limit})
    contacts = data.get("contacts", [])
    if not contacts:
        return "No contacts found."
    lines = [f"Found {len(contacts)} contact(s):\n"]
    for c in contacts:
        lines.append(
            f"- {c.get('firstName','')} {c.get('lastName','')} | "
            f"Email: {c.get('email','—')} | Phone: {c.get('phone','—')} | ID: {c.get('id')}"
        )
    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def get_contact(contact_id: str = Field(description="The GHL contact ID")) -> str:
    """Get full details for a single GoHighLevel contact by ID."""
    data = await _get(f"/contacts/{contact_id}")
    c = data.get("contact", data)
    return _truncate(
        f"Contact: {c.get('firstName','')} {c.get('lastName','')}\n"
        f"Email: {c.get('email','—')}\nPhone: {c.get('phone','—')}\n"
        f"Tags: {', '.join(c.get('tags', []))}\n"
        f"Source: {c.get('source','—')}\nCreated: {c.get('dateAdded','—')}\n"
        f"Location ID: {c.get('locationId','—')}\nID: {c.get('id')}"
    )


@mcp.tool()
async def create_contact(
    first_name: str = Field(description="First name"),
    last_name: str = Field(default="", description="Last name"),
    email: str = Field(default="", description="Email address"),
    phone: str = Field(default="", description="Phone number (E.164 format, e.g. +14155552671)"),
    tags: list[str] = Field(default_factory=list, description="Tags to apply"),
    source: str = Field(default="", description="Lead source label"),
) -> str:
    """Create a new contact in GoHighLevel."""
    body: dict = {"locationId": _loc(), "firstName": first_name}
    if last_name: body["lastName"] = last_name
    if email:     body["email"] = email
    if phone:     body["phone"] = phone
    if tags:      body["tags"] = tags
    if source:    body["source"] = source
    data = await _post("/contacts/", body)
    c = data.get("contact", data)
    return f"Contact created — ID: {c.get('id')} | {c.get('firstName','')} {c.get('lastName','')}"


@mcp.tool()
async def update_contact(
    contact_id: str = Field(description="The GHL contact ID to update"),
    first_name: Optional[str] = Field(default=None),
    last_name: Optional[str] = Field(default=None),
    email: Optional[str] = Field(default=None),
    phone: Optional[str] = Field(default=None),
    tags: Optional[list[str]] = Field(default=None),
) -> str:
    """Update fields on an existing GoHighLevel contact."""
    body: dict = {}
    if first_name is not None: body["firstName"] = first_name
    if last_name  is not None: body["lastName"]  = last_name
    if email      is not None: body["email"]      = email
    if phone      is not None: body["phone"]      = phone
    if tags       is not None: body["tags"]       = tags
    data = await _put(f"/contacts/{contact_id}", body)
    return f"Contact {contact_id} updated successfully."


# ── OPPORTUNITIES ─────────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
async def list_opportunities(
    pipeline_id: str = Field(description="Pipeline ID to list opportunities from"),
    status: str = Field(default="open", description="Filter by status: open, won, lost, abandoned"),
    limit: int = Field(default=20, ge=1, le=100),
) -> str:
    """List opportunities (deals) in a GoHighLevel pipeline."""
    data = await _get(
        "/opportunities/search",
        {"location_id": _loc(), "pipeline_id": pipeline_id, "status": status, "limit": limit},
    )
    opps = data.get("opportunities", [])
    if not opps:
        return f"No {status} opportunities found in pipeline {pipeline_id}."
    lines = [f"{len(opps)} opportunities (status={status}):\n"]
    for o in opps:
        lines.append(
            f"- {o.get('name','Unnamed')} | Stage: {o.get('pipelineStageId','—')} | "
            f"Value: ${o.get('monetaryValue',0):,.2f} | ID: {o.get('id')}"
        )
    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def get_pipelines() -> str:
    """List all pipelines in the GoHighLevel location."""
    data = await _get("/opportunities/pipelines", {"locationId": _loc()})
    pipelines = data.get("pipelines", [])
    if not pipelines:
        return "No pipelines found."
    lines = ["Pipelines:\n"]
    for p in pipelines:
        stages = [s.get("name", "") for s in p.get("stages", [])]
        lines.append(f"- {p.get('name')} (ID: {p.get('id')}) | Stages: {', '.join(stages)}")
    return "\n".join(lines)


@mcp.tool()
async def create_opportunity(
    pipeline_id: str = Field(description="Pipeline ID"),
    pipeline_stage_id: str = Field(description="Stage ID within the pipeline"),
    name: str = Field(description="Opportunity name / deal title"),
    contact_id: str = Field(description="Associated GHL contact ID"),
    monetary_value: float = Field(default=0.0, description="Deal value in dollars"),
    status: str = Field(default="open", description="open | won | lost | abandoned"),
) -> str:
    """Create a new opportunity (deal) in a GoHighLevel pipeline."""
    body = {
        "locationId": _loc(),
        "pipelineId": pipeline_id,
        "pipelineStageId": pipeline_stage_id,
        "name": name,
        "contactId": contact_id,
        "monetaryValue": monetary_value,
        "status": status,
    }
    data = await _post("/opportunities/", body)
    o = data.get("opportunity", data)
    return f"Opportunity created — ID: {o.get('id')} | {name}"


# ── CONVERSATIONS ─────────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
async def scan_all_conversations(
    limit: int = Field(default=100, ge=1, le=100, description="Conversations to fetch per page (max 100)"),
    sort_by: str = Field(default="last_message_date", description="Sort by: last_message_date or created_date"),
    sort_order: str = Field(default="desc", description="asc or desc"),
    query: str = Field(default="", description="Optional keyword to filter conversations"),
) -> str:
    """Scan ALL conversations across the entire GoHighLevel account (not just one contact).

    Returns a paginated list of every conversation with the last message preview.
    Use get_conversation_messages with a conversation ID to read the full thread.
    Call multiple times with increasing offsets to page through all history.
    """
    params: dict = {
        "locationId": _loc(),
        "limit": limit,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    if query:
        params["query"] = query

    data = await _get("/conversations/search", params)
    convs = data.get("conversations", [])
    total = data.get("total", "?")

    if not convs:
        return "No conversations found."

    lines = [f"Total conversations in account: {total} | Showing {len(convs)}\n"]
    for cv in convs:
        contact_name = cv.get("contactName") or cv.get("fullName") or "Unknown"
        last_msg = (cv.get("lastMessageBody") or "")[:120]
        lines.append(
            f"[{cv.get('dateUpdated','—')}] {contact_name} | "
            f"Type: {cv.get('type','—')} | "
            f"Conv ID: {cv.get('id')} | "
            f"Last: {last_msg}"
        )
    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def get_conversations(
    contact_id: str = Field(description="GHL contact ID to fetch conversations for"),
    limit: int = Field(default=10, ge=1, le=50),
) -> str:
    """Get recent conversations for a GoHighLevel contact."""
    data = await _get("/conversations/search", {"locationId": _loc(), "contactId": contact_id, "limit": limit})
    convs = data.get("conversations", [])
    if not convs:
        return f"No conversations found for contact {contact_id}."
    lines = [f"{len(convs)} conversation(s):\n"]
    for cv in convs:
        lines.append(
            f"- ID: {cv.get('id')} | Type: {cv.get('type','—')} | "
            f"Last message: {cv.get('lastMessageBody','—')[:100]} | "
            f"Date: {cv.get('dateUpdated','—')}"
        )
    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def get_conversation_messages(
    conversation_id: str = Field(description="Conversation ID (from get_conversations)"),
    limit: int = Field(default=50, ge=1, le=100, description="Number of messages to fetch"),
) -> str:
    """Get the full SMS/email message thread for a conversation — shows back-and-forth texts.

    Use get_conversations first to find the conversation ID for a contact.
    Messages are returned in chronological order with sender direction (inbound/outbound).
    """
    data = await _get(f"/conversations/{conversation_id}/messages", {"limit": limit})
    messages = data.get("messages", {}).get("messages", data.get("messages", []))
    if not messages:
        return f"No messages found in conversation {conversation_id}."
    lines = [f"{len(messages)} message(s):\n"]
    for m in messages:
        direction = "→ OUT" if m.get("direction") == "outbound" else "← IN "
        msg_type  = m.get("messageType") or m.get("type", "")
        body      = m.get("body") or m.get("message", "")
        date      = m.get("dateAdded", "—")
        lines.append(f"[{date}] {direction} [{msg_type}] {body}")
    return _truncate("\n".join(lines))


@mcp.tool()
async def send_sms(
    contact_id: str = Field(description="GHL contact ID to send SMS to"),
    message: str = Field(description="SMS message body"),
) -> str:
    """Send an SMS message to a GoHighLevel contact."""
    body = {
        "type": "SMS",
        "contactId": contact_id,
        "locationId": _loc(),
        "message": message,
    }
    data = await _post("/conversations/messages", body)
    return f"SMS sent. Message ID: {data.get('messageId') or data.get('id','—')}"


@mcp.tool()
async def send_email(
    contact_id: str = Field(description="GHL contact ID"),
    subject: str = Field(description="Email subject line"),
    body: str = Field(description="Email body (plain text or HTML)"),
    from_email: str = Field(default="", description="Sender email (uses account default if omitted)"),
) -> str:
    """Send an email to a GoHighLevel contact."""
    payload: dict = {
        "type": "Email",
        "contactId": contact_id,
        "locationId": _loc(),
        "subject": subject,
        "body": body,
    }
    if from_email:
        payload["from"] = from_email
    data = await _post("/conversations/messages", payload)
    return f"Email sent. Message ID: {data.get('messageId') or data.get('id','—')}"


# ── CALENDARS / APPOINTMENTS ──────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
async def list_calendars() -> str:
    """List all calendars in the GoHighLevel location."""
    data = await _get("/calendars/", {"locationId": _loc()})
    cals = data.get("calendars", [])
    if not cals:
        return "No calendars found."
    lines = ["Calendars:\n"]
    for cal in cals:
        lines.append(f"- {cal.get('name')} (ID: {cal.get('id')}) | Type: {cal.get('calendarType','—')}")
    return "\n".join(lines)


@mcp.tool()
async def create_appointment(
    calendar_id: str = Field(description="Calendar ID"),
    contact_id: str = Field(description="GHL contact ID"),
    start_time: str = Field(description="Start time in ISO 8601 format, e.g. 2025-06-15T10:00:00-07:00"),
    end_time: str = Field(description="End time in ISO 8601 format"),
    title: str = Field(default="Appointment", description="Appointment title"),
) -> str:
    """Book an appointment on a GoHighLevel calendar for a contact."""
    body = {
        "calendarId": calendar_id,
        "locationId": _loc(),
        "contactId": contact_id,
        "startTime": start_time,
        "endTime": end_time,
        "title": title,
    }
    data = await _post("/calendars/events/appointments", body)
    appt = data.get("appointment", data)
    return f"Appointment booked — ID: {appt.get('id')} | {title} at {start_time}"


# ── TAGS ──────────────────────────────────────────────────────────────────────

@mcp.tool()
async def add_tags_to_contact(
    contact_id: str = Field(description="GHL contact ID"),
    tags: list[str] = Field(description="List of tags to add"),
) -> str:
    """Add tags to a GoHighLevel contact."""
    data = await _post(f"/contacts/{contact_id}/tags", {"tags": tags})
    return f"Tags added to contact {contact_id}: {', '.join(tags)}"


@mcp.tool()
async def remove_tags_from_contact(
    contact_id: str = Field(description="GHL contact ID"),
    tags: list[str] = Field(description="List of tags to remove"),
) -> str:
    """Remove tags from a GoHighLevel contact."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        r = await client.request(
            "DELETE",
            f"/contacts/{contact_id}/tags",
            headers=_headers(),
            json={"tags": tags},
        )
        r.raise_for_status()
    return f"Tags removed from contact {contact_id}: {', '.join(tags)}"


# ── NOTES ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def add_note_to_contact(
    contact_id: str = Field(description="GHL contact ID"),
    note: str = Field(description="Note text to add"),
) -> str:
    """Add a note to a GoHighLevel contact."""
    data = await _post(f"/contacts/{contact_id}/notes", {"body": note})
    return f"Note added to contact {contact_id}. Note ID: {data.get('note',{}).get('id','—')}"


@mcp.tool(annotations={"readOnlyHint": True})
async def get_contact_notes(contact_id: str = Field(description="GHL contact ID")) -> str:
    """Get all notes for a GoHighLevel contact."""
    data = await _get(f"/contacts/{contact_id}/notes")
    notes = data.get("notes", [])
    if not notes:
        return f"No notes found for contact {contact_id}."
    lines = [f"{len(notes)} note(s):\n"]
    for n in notes:
        lines.append(f"- [{n.get('dateAdded','—')}] {n.get('body','')[:200]}")
    return _truncate("\n".join(lines))


# ── SALES ANALYSIS ───────────────────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
async def analyze_unresponded_leads(
    hours_threshold: int = Field(default=24, description="Flag leads with no reply after this many hours"),
    limit: int = Field(default=100, ge=1, le=100),
) -> str:
    """Find leads with inbound messages that the sales team has NOT responded to.

    Identifies contacts who texted/emailed in but received no outbound reply —
    a key indicator of dropped leads and missed revenue.
    """
    data = await _get("/conversations/search", {
        "locationId": _loc(),
        "limit": limit,
        "sortBy": "last_message_date",
        "sortOrder": "desc",
    })
    convs = data.get("conversations", [])
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours_threshold)

    unresponded = []
    for cv in convs:
        last_direction = cv.get("lastMessageDirection") or cv.get("direction", "")
        last_date_str  = cv.get("dateUpdated") or cv.get("lastMessageDate", "")
        if last_direction == "inbound":
            try:
                last_date = datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))
                age_hours = (now - last_date).total_seconds() / 3600
                if last_date < cutoff:
                    unresponded.append((cv, age_hours))
            except Exception:
                unresponded.append((cv, -1))

    if not unresponded:
        return f"No unresponded inbound messages older than {hours_threshold}h. Team is on top of it!"

    lines = [f"⚠️  {len(unresponded)} leads waiting >{ hours_threshold}h for a reply:\n"]
    for cv, age in unresponded:
        name     = cv.get("contactName") or cv.get("fullName") or "Unknown"
        last_msg = (cv.get("lastMessageBody") or "")[:100]
        age_str  = f"{age:.0f}h ago" if age >= 0 else "unknown time ago"
        lines.append(f"- {name} | Conv ID: {cv.get('id')} | Waiting: {age_str} | \"{last_msg}\"")

    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def analyze_pipeline_health(
    pipeline_id: str = Field(description="Pipeline ID to analyze (use get_pipelines to find IDs)"),
) -> str:
    """Analyze a sales pipeline to find where deals stall and what's at risk.

    Shows deal count and total value per stage, flags deals with no activity,
    and surfaces bottlenecks where prospects stop progressing.
    """
    data = await _get("/opportunities/search", {
        "location_id": _loc(),
        "pipeline_id": pipeline_id,
        "limit": 100,
    })
    opps = data.get("opportunities", [])
    if not opps:
        return "No opportunities found in this pipeline."

    now = datetime.now(timezone.utc)
    stage_buckets: dict = {}
    stale = []

    for o in opps:
        stage = o.get("pipelineStageName") or o.get("pipelineStageId", "Unknown Stage")
        value = float(o.get("monetaryValue") or 0)
        stage_buckets.setdefault(stage, {"count": 0, "value": 0.0})
        stage_buckets[stage]["count"] += 1
        stage_buckets[stage]["value"] += value

        # Flag deals with no update in 7+ days
        updated_str = o.get("dateUpdated") or o.get("updatedAt", "")
        try:
            updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
            if (now - updated).days >= 7:
                stale.append((o.get("name", "Unnamed"), o.get("assignedTo", "—"), (now - updated).days))
        except Exception:
            pass

    lines = ["📊 Pipeline Health Report\n", "── Stage Breakdown ──"]
    total_value = sum(v["value"] for v in stage_buckets.values())
    for stage, stats in stage_buckets.items():
        lines.append(f"  {stage}: {stats['count']} deals | ${stats['value']:,.0f}")
    lines.append(f"\n  TOTAL: {len(opps)} deals | ${total_value:,.0f}\n")

    if stale:
        lines.append(f"── Stale Deals (no activity 7+ days) ── {len(stale)} deals at risk")
        for name, owner, days in sorted(stale, key=lambda x: -x[2]):
            lines.append(f"  ⏰ \"{name}\" | Assigned: {owner} | {days} days dormant")
    else:
        lines.append("✅ No stale deals — pipeline is active.")

    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def analyze_team_response_times(
    limit: int = Field(default=100, ge=1, le=100, description="Conversations to sample"),
) -> str:
    """Measure how fast the sales team responds to inbound leads.

    Samples recent conversations and calculates average/worst response times
    per assigned team member. Slow response times are one of the #1 causes of lost deals.
    """
    data = await _get("/conversations/search", {
        "locationId": _loc(),
        "limit": limit,
        "sortBy": "last_message_date",
        "sortOrder": "desc",
    })
    convs = data.get("conversations", [])
    if not convs:
        return "No conversations found to analyze."

    fast   = []  # < 5 min
    medium = []  # 5–60 min
    slow   = []  # 1–24 hrs
    dead   = []  # 24+ hrs or never replied

    for cv in convs:
        first_response_time = cv.get("firstResponseTime")  # seconds, if GHL provides it
        if first_response_time is not None:
            mins = first_response_time / 60
            entry = (cv.get("contactName") or "Unknown", mins)
            if mins < 5:        fast.append(entry)
            elif mins < 60:     medium.append(entry)
            elif mins < 1440:   slow.append(entry)
            else:               dead.append(entry)

    all_times = fast + medium + slow
    avg = sum(m for _, m in all_times) / len(all_times) if all_times else None

    lines = ["⚡ Team Response Time Analysis\n"]
    lines.append(f"Sample size: {len(convs)} conversations\n")

    if avg is not None:
        lines.append(f"Average first response: {avg:.0f} minutes")
        lines.append(f"  ✅ Under 5 min:   {len(fast)} conversations")
        lines.append(f"  🟡 5–60 min:      {len(medium)} conversations")
        lines.append(f"  🔴 1–24 hrs:      {len(slow)} conversations")
        lines.append(f"  💀 24+ hrs / none: {len(dead)} conversations\n")
        if slow or dead:
            lines.append("Slowest responses (need coaching):")
            for name, mins in sorted(slow + dead, key=lambda x: -x[1])[:10]:
                lines.append(f"  - {name}: {mins:.0f} min wait")
    else:
        # Fallback: use lastMessageDirection as proxy
        no_reply = sum(1 for cv in convs if cv.get("lastMessageDirection") == "inbound")
        replied  = len(convs) - no_reply
        lines.append(f"Conversations with team reply: {replied}/{len(convs)}")
        lines.append(f"Conversations awaiting reply:  {no_reply}/{len(convs)}")
        pct = (no_reply / len(convs) * 100) if convs else 0
        lines.append(f"\n{'🔴' if pct > 20 else '🟡' if pct > 10 else '✅'} "
                     f"{pct:.0f}% of recent leads have NOT been replied to.")

    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def analyze_lost_deals(
    pipeline_id: str = Field(description="Pipeline ID to analyze"),
    limit: int = Field(default=50, ge=1, le=100),
) -> str:
    """Analyze lost/abandoned deals to find patterns in why sales are failing.

    Shows which stages deals are lost from most often, common loss reasons,
    and which team members have the highest loss rates.
    """
    data = await _get("/opportunities/search", {
        "location_id": _loc(),
        "pipeline_id": pipeline_id,
        "status": "lost",
        "limit": limit,
    })
    lost_opps = data.get("opportunities", [])

    data2 = await _get("/opportunities/search", {
        "location_id": _loc(),
        "pipeline_id": pipeline_id,
        "status": "abandoned",
        "limit": limit,
    })
    abandoned_opps = data2.get("opportunities", [])

    all_dead = lost_opps + abandoned_opps
    if not all_dead:
        return "No lost or abandoned deals found — great sign!"

    stage_losses: dict[str, int] = {}
    owner_losses: dict[str, int] = {}
    lost_value = 0.0

    for o in all_dead:
        stage = o.get("pipelineStageName") or o.get("pipelineStageId", "Unknown")
        owner = o.get("assignedTo") or o.get("ownerName") or "Unassigned"
        stage_losses[stage]  = stage_losses.get(stage, 0) + 1
        owner_losses[owner]  = owner_losses.get(owner, 0) + 1
        lost_value += float(o.get("monetaryValue") or 0)

    lines = [
        f"💔 Lost Deal Analysis — {len(all_dead)} deals | ${lost_value:,.0f} lost revenue\n",
        "── Where deals are dying (stage) ──"
    ]
    for stage, count in sorted(stage_losses.items(), key=lambda x: -x[1]):
        pct = count / len(all_dead) * 100
        lines.append(f"  {stage}: {count} deals ({pct:.0f}%)")

    lines.append("\n── Lost deals by team member ──")
    for owner, count in sorted(owner_losses.items(), key=lambda x: -x[1]):
        lines.append(f"  {owner}: {count} lost deals")

    lines.append("\n── What to fix ──")
    top_stage = max(stage_losses, key=stage_losses.get)
    lines.append(f"  Most deals die at: \"{top_stage}\" — review scripts/objection handling at this stage.")
    top_loser = max(owner_losses, key=owner_losses.get)
    lines.append(f"  Most losses by: {top_loser} — consider 1:1 coaching session.")

    return _truncate("\n".join(lines))


@mcp.tool(annotations={"readOnlyHint": True})
async def analyze_contact_followup_gaps(
    days_since_contact: int = Field(default=7, description="Flag contacts with no activity for this many days"),
    limit: int = Field(default=100, ge=1, le=100),
) -> str:
    """Find leads in the system that haven't been followed up with recently.

    Surfaces contacts who were active but have gone cold — a sign the team
    is not nurturing leads consistently enough.
    """
    data = await _get("/contacts/", {
        "locationId": _loc(),
        "limit": limit,
        "sortBy": "date_updated",
        "sortOrder": "desc",
    })
    contacts = data.get("contacts", [])
    if not contacts:
        return "No contacts found."

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_since_contact)
    cold = []

    for c in contacts:
        updated_str = c.get("dateUpdated") or c.get("dateAdded", "")
        try:
            updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
            if updated < cutoff:
                days_cold = (now - updated).days
                cold.append((c, days_cold))
        except Exception:
            pass

    if not cold:
        return f"All contacts have activity within the last {days_since_contact} days. Great follow-up!"

    lines = [f"🥶 {len(cold)} contacts have gone cold (no activity in {days_since_contact}+ days):\n"]
    for c, days in sorted(cold, key=lambda x: -x[1])[:50]:
        name  = f"{c.get('firstName','')} {c.get('lastName','')}".strip() or "Unknown"
        email = c.get("email", "—")
        tags  = ", ".join(c.get("tags", []))
        lines.append(f"  - {name} | {email} | {days}d since last touch | Tags: {tags}")

    lines.append(f"\n💡 Recommendation: Create a re-engagement sequence for these {len(cold)} contacts.")
    return _truncate("\n".join(lines))


if __name__ == "__main__":
    mcp.run()
