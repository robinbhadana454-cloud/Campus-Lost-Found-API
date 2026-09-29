from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from database import create_db_and_tables
from routers import events, reservations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create database and tables on application startup
    create_db_and_tables()
    yield


app = FastAPI(
    title="College Event & Reservation Management API",
    description="A FastAPI REST API built with SQLModel and SQLite for managing campus workshops, hackathons, seminars, and student reservations.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router)
app.include_router(reservations.router)


@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def dashboard():
    """
    Interactive web console for viewing events, reservations, availability, and testing API endpoints.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Campus Event & Reservation System</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #090d16;
                --surface: #111726;
                --surface-hover: #172138;
                --card-border: #1f2b45;
                --text-main: #f1f5f9;
                --text-muted: #94a3b8;
                --accent-primary: #6366f1;
                --accent-primary-hover: #4f46e5;
                --accent-cyan: #06b6d4;
                --accent-emerald: #10b981;
                --accent-rose: #f43f5e;
                --accent-amber: #f59e0b;
                --glow: rgba(99, 102, 241, 0.15);
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: var(--bg);
                color: var(--text-main);
                min-height: 100vh;
                padding: 2.5rem 1.5rem;
                line-height: 1.5;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
            }

            header {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                align-items: center;
                gap: 1.5rem;
                padding-bottom: 2rem;
                border-bottom: 1px solid var(--card-border);
                margin-bottom: 2.5rem;
            }

            .brand {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .brand-icon {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-cyan));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                box-shadow: 0 0 20px var(--glow);
            }

            h1 {
                font-size: 1.875rem;
                font-weight: 800;
                letter-spacing: -0.025em;
                background: linear-gradient(to right, #ffffff, #94a3b8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .tagline {
                font-size: 0.875rem;
                color: var(--text-muted);
            }

            .header-actions {
                display: flex;
                gap: 0.75rem;
            }

            .btn {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.625rem 1.25rem;
                border-radius: 8px;
                font-size: 0.875rem;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.2s ease;
                border: 1px solid transparent;
            }

            .btn-primary {
                background: var(--accent-primary);
                color: white;
            }

            .btn-primary:hover {
                background: var(--accent-primary-hover);
                box-shadow: 0 0 15px var(--glow);
            }

            .btn-secondary {
                background: var(--surface);
                color: var(--text-main);
                border-color: var(--card-border);
            }

            .btn-secondary:hover {
                background: var(--surface-hover);
                border-color: #334155;
            }

            .btn-danger {
                background: rgba(244, 63, 94, 0.15);
                color: #fb7185;
                border-color: rgba(244, 63, 94, 0.3);
            }

            .btn-danger:hover {
                background: rgba(244, 63, 94, 0.25);
            }

            .btn-sm {
                padding: 0.375rem 0.75rem;
                font-size: 0.75rem;
            }

            /* Stats Bar */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1.25rem;
                margin-bottom: 2.5rem;
            }

            .stat-card {
                background: var(--surface);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 1.25rem;
                position: relative;
                overflow: hidden;
            }

            .stat-card::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, var(--accent-primary), transparent);
            }

            .stat-label {
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-muted);
                margin-bottom: 0.5rem;
            }

            .stat-value {
                font-size: 1.75rem;
                font-weight: 800;
                font-family: 'JetBrains Mono', monospace;
            }

            /* Layout Grid */
            .main-layout {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
            }

            @media (max-width: 992px) {
                .main-layout {
                    grid-template-columns: 1fr;
                }
            }

            .panel {
                background: var(--surface);
                border: 1px solid var(--card-border);
                border-radius: 14px;
                padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            }

            .panel-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.25rem;
                padding-bottom: 0.75rem;
                border-bottom: 1px solid var(--card-border);
            }

            .panel-title {
                font-size: 1.125rem;
                font-weight: 700;
            }

            /* Event Cards */
            .event-list {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .event-item {
                background: #0d121f;
                border: 1px solid var(--card-border);
                border-radius: 10px;
                padding: 1.25rem;
                transition: all 0.2s ease;
            }

            .event-item:hover {
                border-color: #2e3e63;
                background: #0f1524;
            }

            .event-top {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 1rem;
                margin-bottom: 0.75rem;
            }

            .event-title {
                font-size: 1.1rem;
                font-weight: 700;
                color: #ffffff;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                padding: 0.25rem 0.625rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .badge-open {
                background: rgba(16, 185, 129, 0.15);
                color: #34d399;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }

            .badge-closed {
                background: rgba(244, 63, 94, 0.15);
                color: #fb7185;
                border: 1px solid rgba(244, 63, 94, 0.3);
            }

            .event-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                font-size: 0.8125rem;
                color: var(--text-muted);
                margin-bottom: 1rem;
            }

            .event-meta span {
                display: flex;
                align-items: center;
                gap: 0.35rem;
            }

            /* Progress Bar */
            .capacity-bar-wrapper {
                margin-bottom: 1rem;
            }

            .capacity-labels {
                display: flex;
                justify-content: space-between;
                font-size: 0.75rem;
                margin-bottom: 0.35rem;
                font-family: 'JetBrains Mono', monospace;
            }

            .progress-track {
                height: 8px;
                background: #1e293b;
                border-radius: 9999px;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                border-radius: 9999px;
                transition: width 0.4s ease;
            }

            .fill-normal { background: linear-gradient(90deg, #6366f1, #06b6d4); }
            .fill-warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
            .fill-full { background: linear-gradient(90deg, #ef4444, #f43f5e); }

            .event-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            /* Forms */
            .form-group {
                margin-bottom: 1rem;
            }

            .form-label {
                display: block;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-muted);
                margin-bottom: 0.35rem;
            }

            .form-control {
                width: 100%;
                padding: 0.625rem 0.875rem;
                border-radius: 8px;
                background: #0d121f;
                border: 1px solid var(--card-border);
                color: white;
                font-family: inherit;
                font-size: 0.875rem;
                transition: border-color 0.2s;
            }

            .form-control:focus {
                outline: none;
                border-color: var(--accent-primary);
            }

            /* Modal / Toast */
            #toast {
                position: fixed;
                bottom: 2rem;
                right: 2rem;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                font-size: 0.875rem;
                font-weight: 600;
                display: none;
                z-index: 1000;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                animation: slideUp 0.3s ease;
            }

            .toast-success { background: #065f46; color: #a7f3d0; border: 1px solid #10b981; }
            .toast-error { background: #881337; color: #fecdd3; border: 1px solid #f43f5e; }

            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            .empty-state {
                text-align: center;
                padding: 3rem 1rem;
                color: var(--text-muted);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="brand">
                    <div class="brand-icon">🎟️</div>
                    <div>
                        <h1>College Event & Reservation Hub</h1>
                        <p class="tagline">FastAPI + SQLModel + SQLite REST Engine</p>
                    </div>
                </div>
                <div class="header-actions">
                    <a href="/docs" target="_blank" class="btn btn-primary" id="btn-api-docs">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/><path d="M4.5 5.5A.5.5 0 0 0 4 6v4a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 .5-.5V6a.5.5 0 0 0-.5-.5h-7z"/></svg>
                        Interactive Swagger Docs (/docs)
                    </a>
                    <a href="/redoc" target="_blank" class="btn btn-secondary">
                        ReDoc Specification
                    </a>
                </div>
            </header>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Events</div>
                    <div class="stat-value" id="stat-total-events" style="color: #6366f1;">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Open Events</div>
                    <div class="stat-value" id="stat-open-events" style="color: #10b981;">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Capacity</div>
                    <div class="stat-value" id="stat-total-capacity" style="color: #06b6d4;">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Bookings</div>
                    <div class="stat-value" id="stat-active-reservations" style="color: #f59e0b;">0</div>
                </div>
            </div>

            <div class="main-layout">
                <!-- Left: Event Feed -->
                <div>
                    <div class="panel">
                        <div class="panel-header">
                            <h2 class="panel-title">Active Events & Availability</h2>
                            <button class="btn btn-secondary btn-sm" onclick="loadEvents()" id="btn-refresh-events">🔄 Refresh</button>
                        </div>
                        <div id="events-container" class="event-list">
                            <div class="empty-state">Loading events...</div>
                        </div>
                    </div>

                    <!-- Reservations drawer -->
                    <div class="panel" style="margin-top: 1.5rem;" id="reservations-panel">
                        <div class="panel-header">
                            <h2 class="panel-title" id="res-panel-title">Event Bookings</h2>
                            <span class="tagline" id="res-panel-subtitle">Select an event above to view registered participants</span>
                        </div>
                        <div id="reservations-list">
                            <div class="empty-state">Click "View Bookings" on any event to inspect reservations.</div>
                        </div>
                    </div>
                </div>

                <!-- Right: Quick Action Panels -->
                <div>
                    <!-- Create Event -->
                    <div class="panel" style="margin-bottom: 1.5rem;">
                        <div class="panel-header">
                            <h2 class="panel-title">Create New Event</h2>
                        </div>
                        <form id="create-event-form" onsubmit="handleCreateEvent(event)">
                            <div class="form-group">
                                <label class="form-label">Event Title</label>
                                <input class="form-control" id="ev-title" required placeholder="e.g. AI Hackathon 2026">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Venue / Location</label>
                                <input class="form-control" id="ev-venue" required placeholder="e.g. Main Auditorium Hall B">
                            </div>
                            <div class="form-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                                <div>
                                    <label class="form-label">Capacity (&gt; 0)</label>
                                    <input class="form-control" id="ev-capacity" type="number" min="1" value="30" required>
                                </div>
                                <div>
                                    <label class="form-label">Initial Status</label>
                                    <select class="form-control" id="ev-status">
                                        <option value="Open">Open</option>
                                        <option value="Closed">Closed</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Organizer</label>
                                <input class="form-control" id="ev-organizer" required placeholder="e.g. Computer Science Society">
                            </div>
                            <button type="submit" class="btn btn-primary" style="width: 100%;" id="btn-submit-create-event">Create Event</button>
                        </form>
                    </div>

                    <!-- Make Reservation -->
                    <div class="panel">
                        <div class="panel-header">
                            <h2 class="panel-title">Reserve a Seat</h2>
                        </div>
                        <form id="reserve-seat-form" onsubmit="handleReserveSeat(event)">
                            <div class="form-group">
                                <label class="form-label">Select Event</label>
                                <select class="form-control" id="res-event-select" required>
                                    <option value="">-- Choose an Event --</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Student Name</label>
                                <input class="form-control" id="res-student-name" required placeholder="e.g. Alex Johnson">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Roll Number</label>
                                <input class="form-control" id="res-roll-number" required placeholder="e.g. CS2026-042">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Student Email (Validated)</label>
                                <input class="form-control" id="res-email" type="email" required placeholder="e.g. alex@college.edu">
                            </div>
                            <button type="submit" class="btn btn-primary" style="width: 100%;" id="btn-submit-reserve">Confirm Reservation</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div id="toast"></div>

        <script>
            let currentEvents = [];

            function showToast(message, isError = false) {
                const toast = document.getElementById('toast');
                toast.textContent = message;
                toast.className = isError ? 'toast-error' : 'toast-success';
                toast.style.display = 'block';
                setTimeout(() => {
                    toast.style.display = 'none';
                }, 4000);
            }

            async function loadEvents() {
                try {
                    const res = await fetch('/events');
                    if (!res.ok) throw new Error('Failed to load events');
                    currentEvents = await res.json();
                    
                    const select = document.getElementById('res-event-select');
                    select.innerHTML = '<option value="">-- Choose an Event --</option>';

                    let totalCap = 0;
                    let openCount = 0;
                    let totalBooked = 0;

                    const container = document.getElementById('events-container');
                    if (currentEvents.length === 0) {
                        container.innerHTML = '<div class="empty-state">No events found. Create one using the form on the right!</div>';
                    } else {
                        container.innerHTML = '';
                    }

                    for (const ev of currentEvents) {
                        totalCap += ev.capacity;
                        if (ev.status === 'Open') openCount++;

                        // Fetch live availability for accurate count
                        const availRes = await fetch(`/events/${ev.id}/availability`);
                        const avail = await availRes.json();
                        totalBooked += avail.booked;

                        const percent = Math.min(100, Math.round((avail.booked / ev.capacity) * 100));
                        let fillClass = 'fill-normal';
                        if (percent >= 100) fillClass = 'fill-full';
                        else if (percent >= 80) fillClass = 'fill-warning';

                        const option = document.createElement('option');
                        option.value = ev.id;
                        option.textContent = `#${ev.id} - ${ev.title} (${avail.remaining} seats left, ${ev.status})`;
                        select.appendChild(option);

                        const card = document.createElement('div');
                        card.className = 'event-item';
                        card.id = `event-card-${ev.id}`;
                        card.innerHTML = `
                            <div class="event-top">
                                <div>
                                    <div class="event-title">#${ev.id} - ${ev.title}</div>
                                    <div style="font-size: 0.8125rem; color: var(--accent-cyan);">Organizer: ${ev.organizer}</div>
                                </div>
                                <span class="badge ${ev.status === 'Open' ? 'badge-open' : 'badge-closed'}">${ev.status}</span>
                            </div>
                            <div class="event-meta">
                                <span>📍 ${ev.venue}</span>
                                <span>👥 Capacity: ${ev.capacity}</span>
                                <span>🎟️ Booked: ${avail.booked}</span>
                                <span>✨ Remaining: ${avail.remaining}</span>
                            </div>
                            <div class="capacity-bar-wrapper">
                                <div class="capacity-labels">
                                    <span>Occupancy: ${percent}%</span>
                                    <span>${avail.booked} / ${ev.capacity} Seats</span>
                                </div>
                                <div class="progress-track">
                                    <div class="progress-fill ${fillClass}" style="width: ${percent}%;"></div>
                                </div>
                            </div>
                            <div class="event-actions">
                                <button class="btn btn-secondary btn-sm" onclick="viewBookings(${ev.id}, '${ev.title.replace(/'/g, "\\'")}')">View Bookings</button>
                                <button class="btn btn-secondary btn-sm" onclick="toggleStatus(${ev.id}, '${ev.status}')">${ev.status === 'Open' ? 'Mark Closed' : 'Mark Open'}</button>
                                <button class="btn btn-danger btn-sm" onclick="deleteEvent(${ev.id})">Delete Event</button>
                            </div>
                        `;
                        container.appendChild(card);
                    }

                    document.getElementById('stat-total-events').textContent = currentEvents.length;
                    document.getElementById('stat-open-events').textContent = openCount;
                    document.getElementById('stat-total-capacity').textContent = totalCap;
                    document.getElementById('stat-active-reservations').textContent = totalBooked;

                } catch (err) {
                    showToast(err.message, true);
                }
            }

            async function handleCreateEvent(e) {
                e.preventDefault();
                const payload = {
                    title: document.getElementById('ev-title').value,
                    venue: document.getElementById('ev-venue').value,
                    capacity: parseInt(document.getElementById('ev-capacity').value, 10),
                    status: document.getElementById('ev-status').value,
                    organizer: document.getElementById('ev-organizer').value
                };

                try {
                    const res = await fetch('/events', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        throw new Error(data.detail ? (Array.isArray(data.detail) ? data.detail[0].msg : data.detail) : 'Failed to create event');
                    }
                    showToast(`Event "${data.title}" created successfully!`);
                    document.getElementById('create-event-form').reset();
                    loadEvents();
                } catch (err) {
                    showToast(err.message, true);
                }
            }

            async function handleReserveSeat(e) {
                e.preventDefault();
                const eventId = document.getElementById('res-event-select').value;
                if (!eventId) {
                    showToast('Please select an event', true);
                    return;
                }

                const payload = {
                    student_name: document.getElementById('res-student-name').value,
                    roll_number: document.getElementById('res-roll-number').value,
                    email: document.getElementById('res-email').value
                };

                try {
                    const res = await fetch(`/events/${eventId}/reserve`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        throw new Error(data.detail ? (Array.isArray(data.detail) ? data.detail[0].msg : data.detail) : 'Reservation failed');
                    }
                    showToast(`Reservation #${data.id} confirmed for ${data.student_name}!`);
                    document.getElementById('reserve-seat-form').reset();
                    loadEvents();
                    viewBookings(eventId, 'Event');
                } catch (err) {
                    showToast(err.message, true);
                }
            }

            async function toggleStatus(eventId, currentStatus) {
                const newStatus = currentStatus === 'Open' ? 'Closed' : 'Open';
                try {
                    const res = await fetch(`/events/${eventId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status: newStatus })
                    });
                    if (!res.ok) throw new Error('Failed to update event status');
                    showToast(`Event #${eventId} status updated to ${newStatus}`);
                    loadEvents();
                } catch (err) {
                    showToast(err.message, true);
                }
            }

            async function deleteEvent(eventId) {
                if (!confirm(`Delete event #${eventId} and all its reservations?`)) return;
                try {
                    const res = await fetch(`/events/${eventId}`, { method: 'DELETE' });
                    if (!res.ok) throw new Error('Failed to delete event');
                    showToast(`Event #${eventId} deleted`);
                    loadEvents();
                    document.getElementById('reservations-list').innerHTML = '<div class="empty-state">Select an event to view registered participants</div>';
                } catch (err) {
                    showToast(err.message, true);
                }
            }

            async function viewBookings(eventId, eventTitle) {
                document.getElementById('res-panel-title').textContent = `Bookings for: ${eventTitle} (#${eventId})`;
                const container = document.getElementById('reservations-list');
                container.innerHTML = '<div class="empty-state">Fetching reservations...</div>';

                try {
                    const res = await fetch(`/events/${eventId}/reservations`);
                    if (!res.ok) throw new Error('Failed to fetch reservations');
                    const reservations = await res.json();

                    if (reservations.length === 0) {
                        container.innerHTML = '<div class="empty-state">No reservations found for this event yet.</div>';
                        return;
                    }

                    let html = '<div style="display: flex; flex-direction: column; gap: 0.75rem;">';
                    reservations.forEach(r => {
                        html += `
                            <div style="background: #0d121f; border: 1px solid var(--card-border); border-radius: 8px; padding: 0.875rem; display: flex; justify-content: space-between; align-items: center;" id="res-row-${r.id}">
                                <div>
                                    <div style="font-weight: 600; font-size: 0.95rem;">${r.student_name} <span style="font-size: 0.75rem; color: var(--accent-cyan); font-family: monospace;">(${r.roll_number})</span></div>
                                    <div style="font-size: 0.8125rem; color: var(--text-muted);">${r.email} • Reservation ID: #${r.id}</div>
                                </div>
                                <button class="btn btn-danger btn-sm" onclick="cancelReservation(${r.id}, ${eventId}, '${eventTitle.replace(/'/g, "\\'")}')">Cancel</button>
                            </div>
                        `;
                    });
                    html += '</div>';
                    container.innerHTML = html;
                } catch (err) {
                    showToast(err.message, true);
                }
            }

            async function cancelReservation(reservationId, eventId, eventTitle) {
                if (!confirm(`Cancel reservation #${reservationId}?`)) return;
                try {
                    const res = await fetch(`/reservations/${reservationId}`, { method: 'DELETE' });
                    if (!res.ok) throw new Error('Failed to cancel reservation');
                    showToast(`Reservation #${reservationId} cancelled`);
                    loadEvents();
                    viewBookings(eventId, eventTitle);
                } catch (err) {
                    showToast(err.message, true);
                }
            }

            // Initial load
            loadEvents();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

