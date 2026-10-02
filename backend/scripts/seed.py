import os
import sys
import datetime

# Ensure backend root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Base, engine
from app.models.models import (
    Event, Venue, Session as EventSession, Team, Member, Task,
    Dependency, Resource, VolunteerShift, Risk, ChangeLog, KnowledgeRecord
)

def run_seed():
    db = SessionLocal()
    print("🌱 Rebuilding database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    now = datetime.datetime.now(datetime.timezone.utc)
    base_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

    # 1. Event
    event_id = "evt-kiit-techfest-2026"
    event = Event(
        id=event_id,
        name="KIIT TECHNICAL FEST 2026",
        description="East India's premier annual engineering and technology symposium. 3 days of cutting-edge hackathons, keynotes, robotics arenas, and innovation showcases. (Sample Demo Data)",
        start_date=base_time,
        end_date=base_time + datetime.timedelta(days=3),
        status="ACTIVE",
        organizer_id="user-kiit-admin",
        notion_page_id="notion-kiit-techfest-2026-master"
    )
    db.add(event)

    # 2. Venues (3 Venues)
    venues_data = [
        {
            "id": "ven-aud-1",
            "name": "Auditorium 1 - Campus 6",
            "capacity": 500,
            "location": "Campus 6, Academic Block A, Level 1",
            "equipment": ["4K UHD LED Wall 30x12ft", "L-Acoustics Line Array", "8x Shure Axient Mics", "Motorized Stage Truss Rig", "Broadcast Multi-Cam Switcher"],
            "availability": True
        },
        {
            "id": "ven-hall-a",
            "name": "Convention Centre Hall A",
            "capacity": 220,
            "location": "Campus 6, Convention Centre, Wing B",
            "equipment": ["Dual 85-inch Sony Displays", "Podium Gooseneck Mics", "Digital Stage Spotlights", "Acoustic Drapes"],
            "availability": True
        },
        {
            "id": "ven-lab-3",
            "name": "Tech Hub Lab 3",
            "capacity": 80,
            "location": "Campus 12, Computer Science Block, 3rd Floor",
            "equipment": ["High-Density 10G Cisco Switch", "80 High-End Workstations", "Dual Laser Projectors", "Dedicated UPS Bank"],
            "availability": True
        }
    ]
    for v in venues_data:
        db.add(Venue(event_id=event_id, **v))

    # 3. Teams (6 Departments)
    teams_data = [
        {"id": "team-ops", "name": "Core Operations", "department": "Core Ops", "lead_id": "mem-arjun", "lead_name": "Arjun Mohanty"},
        {"id": "team-tech", "name": "Technical & AV Infrastructure", "department": "Tech & AV", "lead_id": "mem-devendra", "lead_name": "Devendra Rao"},
        {"id": "team-stage", "name": "Stage & Production Logistics", "department": "Logistics", "lead_id": "mem-simran", "lead_name": "Simran Kaur"},
        {"id": "team-marketing", "name": "Marketing & Communications", "department": "Marketing", "lead_id": "mem-sneha", "lead_name": "Sneha Mukherjee"},
        {"id": "team-hospitality", "name": "Hospitality & VIP Registration", "department": "Hospitality", "lead_id": "mem-rohan", "lead_name": "Rohan Verma"},
        {"id": "team-volunteers", "name": "Volunteer Operations", "department": "Volunteer Ops", "lead_id": "mem-tanya", "lead_name": "Tanya Sen"}
    ]
    for tm in teams_data:
        db.add(Team(event_id=event_id, **tm))

    # 4. Members (Team Leads + 20 Volunteers)
    leads_and_members = [
        {"id": "mem-arjun", "name": "Arjun Mohanty", "email": "admin@eventra.kiit.ac.in", "role": "ADMIN", "skills": ["INCIDENT_MANAGEMENT", "OPERATIONS", "DISPATCH"], "workload": 3},
        {"id": "mem-devendra", "name": "Devendra Rao", "email": "tech@eventra.kiit.ac.in", "role": "TECHNICAL", "skills": ["AV_SETUP", "STREAMING", "NETWORKING"], "workload": 4},
        {"id": "mem-simran", "name": "Simran Kaur", "email": "ops@eventra.kiit.ac.in", "role": "OPERATIONS", "skills": ["STAGE_OPS", "RAPID_LOGISTICS"], "workload": 2},
        {"id": "mem-sneha", "name": "Sneha Mukherjee", "email": "marketing@eventra.kiit.ac.in", "role": "MARKETING", "skills": ["COMMUNICATIONS", "SOCIAL_MEDIA"], "workload": 2},
        {"id": "mem-rohan", "name": "Rohan Verma", "email": "registration@eventra.kiit.ac.in", "role": "REGISTRATION", "skills": ["VIP_HANDLING", "REGISTRATION"], "workload": 3},
        {"id": "mem-tanya", "name": "Tanya Sen", "email": "volunteer@eventra.kiit.ac.in", "role": "VOLUNTEER_LEAD", "skills": ["CROWD_CONTROL", "COORDINATION"], "workload": 3},
    ]
    for lm in leads_and_members:
        db.add(Member(**lm))

    # 20 Realistic Volunteers
    volunteers_list = [
        ("vol-01", "Pooja Mishra", "pooja.m@kiit.ac.in", ["AV_SETUP", "STREAMING"], 1),
        ("vol-02", "Aakash Tripathy", "aakash.t@kiit.ac.in", ["STAGE_OPS", "RAPID_LOGISTICS"], 2),
        ("vol-03", "Rhea Sengupta", "rhea.s@kiit.ac.in", ["VIP_HANDLING", "COMMUNICATIONS"], 1),
        ("vol-04", "Karthik Nair", "karthik.n@kiit.ac.in", ["CROWD_CONTROL", "REGISTRATION"], 2),
        ("vol-05", "Ishaan Roy", "ishaan.r@kiit.ac.in", ["AV_SETUP", "RAPID_LOGISTICS"], 1),
        ("vol-06", "Ananya Das", "ananya.d@kiit.ac.in", ["REGISTRATION", "COMMUNICATIONS"], 0),
        ("vol-07", "Sourav Patnaik", "sourav.p@kiit.ac.in", ["STAGE_OPS", "CROWD_CONTROL"], 2),
        ("vol-08", "Meera Bhattacharya", "meera.b@kiit.ac.in", ["VIP_HANDLING", "REGISTRATION"], 1),
        ("vol-09", "Nikhil Chopra", "nikhil.c@kiit.ac.in", ["AV_SETUP", "STREAMING"], 0),
        ("vol-10", "Aditi Samantaray", "aditi.s@kiit.ac.in", ["CROWD_CONTROL", "RAPID_LOGISTICS"], 1),
        ("vol-11", "Vikram Jena", "vikram.j@kiit.ac.in", ["STAGE_OPS", "RAPID_LOGISTICS"], 2),
        ("vol-12", "Snehashis Panda", "snehashis.p@kiit.ac.in", ["REGISTRATION", "VIP_HANDLING"], 1),
        ("vol-13", "Kavya Murthy", "kavya.m@kiit.ac.in", ["AV_SETUP", "STAGE_OPS"], 0),
        ("vol-14", "Deepak Swain", "deepak.s@kiit.ac.in", ["CROWD_CONTROL", "REGISTRATION"], 2),
        ("vol-15", "Shreya Mohapatra", "shreya.m@kiit.ac.in", ["VIP_HANDLING", "COMMUNICATIONS"], 1),
        ("vol-16", "Ayush Pradhan", "ayush.p@kiit.ac.in", ["STAGE_OPS", "RAPID_LOGISTICS"], 1),
        ("vol-17", "Tanvi Agarwal", "tanvi.a@kiit.ac.in", ["REGISTRATION", "CROWD_CONTROL"], 0),
        ("vol-18", "Rajeshwari Rout", "rajeshwari.r@kiit.ac.in", ["AV_SETUP", "STREAMING"], 1),
        ("vol-19", "Abhinav Behera", "abhinav.b@kiit.ac.in", ["CROWD_CONTROL", "RAPID_LOGISTICS"], 2),
        ("vol-20", "Priyanka Sahoo", "priyanka.s@kiit.ac.in", ["VIP_HANDLING", "STAGE_OPS"], 1),
    ]
    for v_id, v_name, v_email, v_skills, v_load in volunteers_list:
        db.add(Member(
            id=v_id,
            name=v_name,
            email=v_email,
            role="VOLUNTEER",
            skills=v_skills,
            workload=v_load,
            availability=True
        ))

    # 5. Sessions (8 Sessions)
    sessions_data = [
        {
            "id": "sess-keynote",
            "title": "Opening Ceremony & Global Tech Keynote",
            "description": "Inaugural address on Frontier AI, agentic engineering, and autonomous systems.",
            "start_time": base_time + datetime.timedelta(hours=1),
            "end_time": base_time + datetime.timedelta(hours=2, minutes=30),
            "venue_id": "ven-aud-1",
            "speaker_id": "spk-01",
            "speaker_name": "Dr. Elena Vance (VP AI Research, DeepMind Alumni)",
            "expected_attendees": 480,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-robotics",
            "title": "Autonomous Robotics Arena Kickoff",
            "description": "High-speed obstacle navigation and multi-agent swarm robotics demonstration.",
            "start_time": base_time + datetime.timedelta(hours=3),
            "end_time": base_time + datetime.timedelta(hours=5),
            "venue_id": "ven-aud-1",
            "speaker_id": "spk-02",
            "speaker_name": "Prof. Ananya Roy (Lead Robotics Lab)",
            "expected_attendees": 420,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-web3",
            "title": "Decentralized Infrastructure & Web3 Security",
            "description": "Zero-knowledge proofs, smart contract fuzzing, and resilient distributed consensus.",
            "start_time": base_time + datetime.timedelta(hours=2),
            "end_time": base_time + datetime.timedelta(hours=3, minutes=30),
            "venue_id": "ven-hall-a",
            "speaker_id": "spk-03",
            "speaker_name": "Marcus Sterling (Founder CypherShield)",
            "expected_attendees": 190,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-edge-ai",
            "title": "Deep Learning on Edge Hardware Masterclass",
            "description": "Hands-on compilation with TensorRT and quantization for embedded systems.",
            "start_time": base_time + datetime.timedelta(hours=1, minutes=30),
            "end_time": base_time + datetime.timedelta(hours=3, minutes=30),
            "venue_id": "ven-lab-3",
            "speaker_id": "spk-04",
            "speaker_name": "Vikramaditya Patel (Principal Architect, NVIDIA)",
            "expected_attendees": 75,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-quantum",
            "title": "Quantum Algorithms Workshop: Qiskit in Action",
            "description": "Practical simulation of Grover's and Shor's algorithms on quantum cloud emulators.",
            "start_time": base_time + datetime.timedelta(hours=4),
            "end_time": base_time + datetime.timedelta(hours=6),
            "venue_id": "ven-lab-3",
            "speaker_id": "spk-05",
            "speaker_name": "Dr. Samantha Reed (Quantum Computing Fellow)",
            "expected_attendees": 65,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-hackathon",
            "title": "National AI Hackathon Grand Pitch Battles",
            "description": "Top 10 finalist teams present their production prototypes to venture jury.",
            "start_time": base_time + datetime.timedelta(hours=5, minutes=30),
            "end_time": base_time + datetime.timedelta(hours=8),
            "venue_id": "ven-aud-1",
            "speaker_id": "spk-06",
            "speaker_name": "Hackathon Venture Jury Panel",
            "expected_attendees": 450,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-fireside",
            "title": "Fireside Chat: Scaling From Campus to Unicorn",
            "description": "Pragmatic insights on fundraising, team culture, and zero-to-one product velocity.",
            "start_time": base_time + datetime.timedelta(hours=4),
            "end_time": base_time + datetime.timedelta(hours=5, minutes=15),
            "venue_id": "ven-hall-a",
            "speaker_id": "spk-07",
            "speaker_name": "Rajesh K. Nair (YC Alumni & Fintech CEO)",
            "expected_attendees": 210,
            "status": "SCHEDULED"
        },
        {
            "id": "sess-valedictory",
            "title": "Valedictory Ceremony & Award Presentation",
            "description": "Prize distribution of Rs. 10 Lakhs, felicitations, and closing address.",
            "start_time": base_time + datetime.timedelta(hours=8, minutes=30),
            "end_time": base_time + datetime.timedelta(hours=10),
            "venue_id": "ven-aud-1",
            "speaker_id": "spk-08",
            "speaker_name": "Chief Guest & University Chancellor",
            "expected_attendees": 500,
            "status": "SCHEDULED"
        }
    ]
    for s in sessions_data:
        db.add(EventSession(event_id=event_id, **s))

    # 6. Resources (5 Core Critical Assets)
    resources_data = [
        {"id": "res-led-wall", "name": "Main 4K LED Wall (30x12ft)", "category": "AV_GEAR", "quantity": 1, "availability": True, "assigned_venue_id": "ven-aud-1"},
        {"id": "res-mic-kit", "name": "Shure Wireless Axient Mic Kit A", "category": "AV_GEAR", "quantity": 8, "availability": True, "assigned_venue_id": "ven-aud-1"},
        {"id": "res-fiber-link", "name": "10Gbps Dedicated Symmetrical Fiber Link", "category": "NETWORK", "quantity": 1, "availability": True, "assigned_venue_id": "ven-aud-1"},
        {"id": "res-stage-rig", "name": "Vermilion Stage Lighting Rig & Spotlights", "category": "STAGE", "quantity": 12, "availability": True, "assigned_venue_id": "ven-aud-1"},
        {"id": "res-generator", "name": "Backup Diesel Generator 125kVA (Automatic Transfer)", "category": "POWER", "quantity": 1, "availability": True, "assigned_venue_id": "ven-aud-1"}
    ]
    for r in resources_data:
        db.add(Resource(event_id=event_id, **r))

    # 7. Operational Tasks (30 Real Tasks across statuses)
    tasks_data = [
        # Tech & AV
        ("task-01", "Calibrate 4K LED wall color profile & aspect ratios", "Perform latency calibration for keynote speaker slide clicker.", "mem-devendra", "Devendra Rao", "team-tech", "COMPLETED", "HIGH", 0, None),
        ("task-02", "Frequency scan for Shure wireless microphone banks", "Interference detected on 620MHz band from Campus 6 repeater.", "mem-devendra", "Devendra Rao", "team-tech", "BLOCKED", "CRITICAL", 2, "Campus 6 RF repeater causing heavy intermodulation on 620MHz band"),
        ("task-03", "Test 10Gbps redundant link failover to backup 1G WAN", "Verify RTMP live stream stability during active failover test.", "mem-devendra", "Devendra Rao", "team-tech", "IN_PROGRESS", "HIGH", 0, None),
        ("task-04", "Run stage monitors sound check with Dr. Elena Vance", "Validate in-ear monitor mix for opening keynote speaker.", "mem-devendra", "Devendra Rao", "team-tech", "TODO", "HIGH", 0, None),
        ("task-05", "Setup OBS broadcast switchboards for Youtube 4K Stream", "Configure multi-angle camera feeds and lower-third graphics.", "mem-devendra", "Devendra Rao", "team-tech", "IN_PROGRESS", "MEDIUM", 0, None),

        # Stage & Logistics
        ("task-06", "Position acoustic stage baffles and keynote podium", "Ensure sightlines from side balcony rows 4-12 are clear.", "mem-simran", "Simran Kaur", "team-stage", "COMPLETED", "MEDIUM", 0, None),
        ("task-07", "Mount KIIT Tech Fest 2026 Vermilion backdrop banners", "Fasten heavy vinyl banners to truss rig with safety steel cables.", "mem-simran", "Simran Kaur", "team-stage", "IN_PROGRESS", "HIGH", 0, None),
        ("task-08", "Coordinate green room catering delivery for VIP speakers", "Deliver continental breakfast and beverages to Academic Block B Lounge.", "mem-simran", "Simran Kaur", "team-stage", "COMPLETED", "MEDIUM", 0, None),
        ("task-09", "Inspect backup power automatic transfer switch (ATS)", "Simulate grid blackout to verify 8-second generator cutoff.", "mem-simran", "Simran Kaur", "team-stage", "COMPLETED", "CRITICAL", 0, None),
        ("task-10", "Assemble emergency acoustic spill barrier for Auditorium 1", "Keep rapid sound baffles on standby in loading dock.", "mem-simran", "Simran Kaur", "team-stage", "TODO", "LOW", 0, None),

        # Marketing & Comms
        ("task-11", "Push opening countdown notification to student app", "Dispatch notification to 2,400 registered students.", "mem-sneha", "Sneha Mukherjee", "team-marketing", "COMPLETED", "HIGH", 0, None),
        ("task-12", "Deploy live schedule widget onto campus digital screens", "Verify API feed sync on 14 digital totems across campuses.", "mem-sneha", "Sneha Mukherjee", "team-marketing", "IN_PROGRESS", "MEDIUM", 0, None),
        ("task-13", "Prepare emergency broadcast templates for room changes", "Draft SMS and in-app templates in case of room shifts.", "mem-sneha", "Sneha Mukherjee", "team-marketing", "COMPLETED", "CRITICAL", 0, None),
        ("task-14", "Coordinate official photography crew shot list", "Ensure coverage of Opening Keynote, Robotics arena, and Hackathon pitch.", "mem-sneha", "Sneha Mukherjee", "team-marketing", "TODO", "LOW", 0, None),
        ("task-15", "Publish social media highlight reel for morning sessions", "Cut 45s vertical reel for Instagram and LinkedIn handles.", "mem-sneha", "Sneha Mukherjee", "team-marketing", "TODO", "MEDIUM", 0, None),

        # Hospitality & Registration
        ("task-16", "Setup 6 barcode scanner desks at Gate 1 & 2", "Verify QR badge printing speed and offline sync cache.", "mem-rohan", "Rohan Verma", "team-hospitality", "COMPLETED", "HIGH", 0, None),
        ("task-17", "Dispatch airport escort convoy for Dr. Elena Vance", "Liaison car en route from Bhubaneswar BBI Airport.", "mem-rohan", "Rohan Verma", "team-hospitality", "IN_PROGRESS", "HIGH", 0, None),
        ("task-18", "Distribute VIP parking tags at Campus 6 security kiosk", "Reserved 25 bays for keynote speakers and jury delegates.", "mem-rohan", "Rohan Verma", "team-hospitality", "COMPLETED", "MEDIUM", 0, None),
        ("task-19", "Stage welcome kits and technical symposium brochures", "Pack 1,000 attendee conference bags in registration storage.", "mem-rohan", "Rohan Verma", "team-hospitality", "COMPLETED", "MEDIUM", 0, None),
        ("task-20", "Resolve badge reprint queue congestion at Desk 4", "Thermal printer 4 paper jam caused 12-minute backlog.", "mem-rohan", "Rohan Verma", "team-hospitality", "REVIEW", "HIGH", 1, "Thermal printer 4 roller jam (cleared, verifying prints)"),

        # Volunteer Ops
        ("task-21", "Conduct 08:00 AM general volunteer roll call", "Brief 20 volunteers on emergency exits and medical triage desk.", "mem-tanya", "Tanya Sen", "team-volunteers", "COMPLETED", "HIGH", 0, None),
        ("task-22", "Deploy 4 crowd marshals to Auditorium 1 foyer", "Prevent bottlenecks outside entry doors before 09:30 AM doors open.", "mem-tanya", "Tanya Sen", "team-volunteers", "IN_PROGRESS", "HIGH", 0, None),
        ("task-23", "Station 2 AV shadow volunteers at audio control console", "Pair volunteers with sound engineers for mic battery monitoring.", "mem-tanya", "Tanya Sen", "team-volunteers", "IN_PROGRESS", "MEDIUM", 0, None),
        ("task-24", "Relieve morning registration shift volunteers for lunch", "Rotate 6 volunteers at 12:30 PM with afternoon cohort.", "mem-tanya", "Tanya Sen", "team-volunteers", "TODO", "MEDIUM", 0, None),
        ("task-25", "Distribute walkie-talkie headsets to team captains", "Channel 1: Ops, Channel 2: AV, Channel 3: Volunteers.", "mem-tanya", "Tanya Sen", "team-volunteers", "COMPLETED", "HIGH", 0, None),

        # Core Ops
        ("task-26", "Review city fire marshal safety sign-off certificate", "Obtain final green light for Auditorium 1 occupancy load.", "mem-arjun", "Arjun Mohanty", "team-ops", "COMPLETED", "CRITICAL", 0, None),
        ("task-27", "Sync master operational manifest with Notion database", "Synchronize scheduled run of show to team Notion workspace.", "mem-arjun", "Arjun Mohanty", "team-ops", "COMPLETED", "MEDIUM", 0, None),
        ("task-28", "Monitor real-time attendee check-in velocity", "Check-in rate tracking at 180 attendees/10min across both gates.", "mem-arjun", "Arjun Mohanty", "team-ops", "IN_PROGRESS", "MEDIUM", 0, None),
        ("task-29", "Conduct 15-minute mid-morning command status huddle", "All leads assemble in Control Room B for rapid pulse check.", "mem-arjun", "Arjun Mohanty", "team-ops", "TODO", "HIGH", 0, None),
        ("task-30", "Prepare post-mortem incident documentation template", "Configure Notion post-event retrospective knowledge schema.", "mem-arjun", "Arjun Mohanty", "team-ops", "TODO", "LOW", 0, None),
    ]

    for t_id, title, desc, own_id, own_name, tm_id, status, prio, esc, blk in tasks_data:
        deadline = base_time + datetime.timedelta(hours=2)
        db.add(Task(
            id=t_id,
            event_id=event_id,
            title=title,
            description=desc,
            owner_id=own_id,
            owner_name=own_name,
            team_id=tm_id,
            deadline=deadline,
            priority=prio,
            status=status,
            blocker=blk,
            escalation_level=esc,
            comments=[]
        ))

    # 8. Volunteer Shifts (12 shifts mapped to sessions and roles)
    shifts_data = [
        ("shift-01", "vol-01", "sess-keynote", "AV_SUPPORT", base_time + datetime.timedelta(hours=1), base_time + datetime.timedelta(hours=3), "CONFIRMED", 92),
        ("shift-02", "vol-02", "sess-keynote", "STAGE_RUNNER", base_time + datetime.timedelta(hours=1), base_time + datetime.timedelta(hours=3), "CONFIRMED", 88),
        ("shift-03", "vol-04", "sess-keynote", "CROWD_FLOW", base_time + datetime.timedelta(hours=0, minutes=45), base_time + datetime.timedelta(hours=3), "CONFIRMED", 90),
        ("shift-04", "vol-03", "sess-keynote", "VIP_ESCORT", base_time + datetime.timedelta(hours=0, minutes=30), base_time + datetime.timedelta(hours=2, minutes=30), "CONFIRMED", 95),
        ("shift-05", "vol-05", "sess-robotics", "AV_SUPPORT", base_time + datetime.timedelta(hours=3), base_time + datetime.timedelta(hours=5), "CONFIRMED", 89),
        ("shift-06", "vol-07", "sess-robotics", "STAGE_RUNNER", base_time + datetime.timedelta(hours=3), base_time + datetime.timedelta(hours=5), "CONFIRMED", 86),
        ("shift-07", "vol-10", "sess-robotics", "CROWD_FLOW", base_time + datetime.timedelta(hours=2, minutes=45), base_time + datetime.timedelta(hours=5), "CONFIRMED", 87),
        ("shift-08", "vol-09", "sess-web3", "AV_SUPPORT", base_time + datetime.timedelta(hours=2), base_time + datetime.timedelta(hours=4), "PENDING", 0),
        ("shift-09", "vol-08", "sess-web3", "BADGE_CHECK", base_time + datetime.timedelta(hours=1, minutes=45), base_time + datetime.timedelta(hours=3, minutes=45), "CONFIRMED", 91),
        ("shift-10", "vol-13", "sess-edge-ai", "AV_SUPPORT", base_time + datetime.timedelta(hours=1, minutes=30), base_time + datetime.timedelta(hours=3, minutes=30), "PENDING", 0),
        ("shift-11", "vol-12", "sess-fireside", "VIP_ESCORT", base_time + datetime.timedelta(hours=3, minutes=45), base_time + datetime.timedelta(hours=5, minutes=30), "CONFIRMED", 93),
        ("shift-12", "vol-14", "sess-hackathon", "CROWD_FLOW", base_time + datetime.timedelta(hours=5), base_time + datetime.timedelta(hours=8), "PENDING", 0),
    ]
    for s_id, v_id, sess_id, role, s_time, e_time, status, score in shifts_data:
        db.add(VolunteerShift(
            id=s_id,
            event_id=event_id,
            volunteer_id=v_id,
            session_id=sess_id,
            role_required=role,
            start_time=s_time,
            end_time=e_time,
            assignment_status=status,
            allocation_score=score
        ))

    # 9. Explicit Dependencies (16 Realistic Dependencies forming the critical path)
    dependencies_data = [
        # Venue -> Session
        ("dep-01", "VENUE", "ven-aud-1", "SESSION", "sess-keynote", "HOSTS", "CRITICAL"),
        ("dep-02", "VENUE", "ven-aud-1", "SESSION", "sess-robotics", "HOSTS", "CRITICAL"),
        ("dep-03", "VENUE", "ven-hall-a", "SESSION", "sess-web3", "HOSTS", "HIGH"),
        ("dep-04", "VENUE", "ven-lab-3", "SESSION", "sess-edge-ai", "HOSTS", "HIGH"),

        # Resource -> Session
        ("dep-05", "RESOURCE", "res-led-wall", "SESSION", "sess-keynote", "REQUIRES", "CRITICAL"),
        ("dep-06", "RESOURCE", "res-mic-kit", "SESSION", "sess-keynote", "REQUIRES", "CRITICAL"),
        ("dep-07", "RESOURCE", "res-fiber-link", "SESSION", "sess-hackathon", "REQUIRES", "CRITICAL"),

        # Task -> Session
        ("dep-08", "TASK", "task-02", "SESSION", "sess-keynote", "PREREQUISITE", "CRITICAL"),
        ("dep-09", "TASK", "task-04", "SESSION", "sess-keynote", "PREREQUISITE", "HIGH"),
        ("dep-10", "TASK", "task-17", "SESSION", "sess-keynote", "PREREQUISITE", "HIGH"),
        ("dep-11", "TASK", "task-26", "SESSION", "sess-keynote", "PREREQUISITE", "CRITICAL"),

        # Session -> Next Session (Sequential dependence)
        ("dep-12", "SESSION", "sess-keynote", "SESSION", "sess-robotics", "FOLLOWS", "HIGH"),
        ("dep-13", "SESSION", "sess-robotics", "SESSION", "sess-hackathon", "FOLLOWS", "HIGH"),
        ("dep-14", "SESSION", "sess-hackathon", "SESSION", "sess-valedictory", "FOLLOWS", "CRITICAL"),

        # Task -> Task
        ("dep-15", "TASK", "task-13", "TASK", "task-11", "NOTIFIES", "HIGH"),
        ("dep-16", "TASK", "task-25", "TASK", "task-22", "ENABLES", "HIGH"),
    ]
    for d_id, st, sid, tt, tid, dtype, crit in dependencies_data:
        db.add(Dependency(
            id=d_id,
            event_id=event_id,
            source_type=st,
            source_id=sid,
            target_type=tt,
            target_id=tid,
            dependency_type=dtype,
            criticality=crit
        ))

    # 10. Risks (5 Realistic Risks)
    risks_data = [
        ("rsk-01", "RF Intermodulation on Wireless Audio Channel", "CRITICAL", "HIGH", "Speaker audio cutout during live 480-attendee keynote.", "Deploy backup wired podium SM58 mic and retune Axient receiver to 540MHz clear bank.", "OPEN"),
        ("rsk-02", "Auditorium 1 Air Conditioning Overheating Surge", "HIGH", "MEDIUM", "Thermal trip of projection rack if room ambient exceeds 28C.", "Pre-cool auditorium 2 hours prior; standby industrial air blowers in wings.", "MITIGATED"),
        ("rsk-03", "Registration Desks Entry Gate Bottleneck", "HIGH", "HIGH", "Queue spilling into Campus 6 main boulevard causing traffic delay.", "Station 4 roaming QR badge scanners with volunteer leads.", "OPEN"),
        ("rsk-04", "Keynote Speaker Flight Delay from Delhi", "MEDIUM", "LOW", "Session start delayed by up to 35 minutes.", "Swap Keynote slot with Robotics Arena demonstration via automated impact protocol.", "MITIGATED"),
        ("rsk-05", "Campus Grid Power Fluctuations During Peak Load", "HIGH", "MEDIUM", "Brownout reset of 4K LED wall controllers.", "Auditorium 1 isolated on dedicated 125kVA diesel generator for full festival duration.", "RESOLVED")
    ]
    for r_id, title, sev, prob, imp, mit, stat in risks_data:
        db.add(Risk(
            id=r_id,
            event_id=event_id,
            title=title,
            severity=sev,
            probability=prob,
            impact=imp,
            mitigation=mit,
            status=stat
        ))

    # 11. Initial Change Log
    db.add(ChangeLog(
        id="chg-init",
        event_id=event_id,
        entity_type="EVENT_INITIALIZATION",
        entity_id=event_id,
        previous_value=None,
        new_value={"event": "KIIT TECHNICAL FEST 2026", "status": "ACTIVE"},
        impact_summary="Master event initialized with 3 venues, 8 sessions, 30 tasks, and 20 volunteers.",
        approved=True,
        created_at=now
    ))

    # 12. Post-Event Knowledge Records (2 Seed Incident Post-Mortems)
    knowledge_data = [
        {
            "id": "knw-01",
            "title": "Mitigation of 620MHz RF Interference in Campus 6 Auditorium",
            "department": "Tech & AV",
            "problem": "Severe RF dropout on wireless microphones during sound check due to uncoordinated campus repeater.",
            "root_cause": "Campus 6 security repeater transmitting spurious harmonics within UHF wireless mic spectrum.",
            "resolution": "Shifted Shure Axient banks to 540MHz G57 band and applied directional paddle antennas.",
            "lessons_learned": "Always execute a 24-hour RF spectrum scan 48 hours prior to high-profile keynotes.",
            "recommended_future_action": "Mandate campus-wide RF moratorium with security department 72h prior to Tech Fest 2027.",
            "tags": ["AV", "Microphones", "RF_Spectrum", "Keynote"],
            "source_references": ["Task-02", "Risk-01"]
        },
        {
            "id": "knw-02",
            "title": "Rapid QR Check-In Buffer Optimization for Morning Surge",
            "department": "Hospitality & Registration",
            "problem": "Peak arrival surge at 08:45 AM produced a 140-person line at Gate 1.",
            "root_cause": "Fixed desktop badge printers throttled throughput to 12 badges per minute per desk.",
            "resolution": "Deployed mobile thermal belt printers with roaming volunteers to prescan badges in queue.",
            "lessons_learned": "Queue presorting reduced counter interaction time from 45 seconds to 9 seconds.",
            "recommended_future_action": "Default to 100% pre-issued digital wallet passes with NFC tap entry for future editions.",
            "tags": ["Registration", "Queueing", "Crowd_Flow"],
            "source_references": ["Task-16", "Risk-03"]
        }
    ]
    for kr in knowledge_data:
        db.add(KnowledgeRecord(event_id=event_id, **kr))

    db.commit()
    print("✅ Seed successfully completed! Fictional demonstration data for 'KIIT TECHNICAL FEST 2026' ready.")
    db.close()

if __name__ == "__main__":
    run_seed()
