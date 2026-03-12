#!/usr/bin/env python3
"""GoHighLevel MCP Server — connects Claude Code to the GHL v2 API."""

import os
from typing import Optional
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


if __name__ == "__main__":
    mcp.run()
