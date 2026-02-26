import streamlit as st
import pandas as pd

from db_backend import (
    init_db,
    authenticate_leader,
    upsert_constituency,
    add_ambulance,
    get_ambulances,
    add_project,
    get_projects_by_constituency,
    get_project_by_id,
    save_media_file,
    get_media_for_project,
)

init_db()
st.set_page_config(
    page_title="INFRASIGHT – Infrastructure Equality Platform",
    layout="wide",
)

if "leader" not in st.session_state:
    st.session_state.leader = None
if "role" not in st.session_state:
    st.session_state.role = None


# ------------- AUTH -------------

def leader_login_ui():
    st.sidebar.subheader("Leader Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Log in as Leader")

    if login_btn:
        user = authenticate_leader(username, password)
        if user:
            st.session_state.leader = user
            st.sidebar.success(
                f"Logged in as {user['username']} ({user['constituency']})"
            )
        else:
            st.sidebar.error("Invalid credentials")

    if st.session_state.leader:
        if st.sidebar.button("Log out"):
            st.session_state.leader = None


leader_login_ui()


# ------------- LEADER PANEL -------------

def leader_panel():
    leader = st.session_state.leader
    if not leader:
        st.info(
            "Leaders: Please log in from the sidebar to manage your constituency data."
        )
        return

    constituency = leader["constituency"]
    st.header(f"Leader Panel – {constituency}")

    tab1, tab2, tab3 = st.tabs(
        ["Constituency Metrics", "Emergency Assets (Ambulances)", "Development Projects"]
    )

    # Constituency metrics
    with tab1:
        st.subheader("Update Constituency Metrics")

        col1, col2, col3 = st.columns(3)
        with col1:
            ambulances_count = st.number_input("Total ambulances", min_value=0, step=1)
            hospitals_count = st.number_input(
                "Total hospitals/clinics", min_value=0, step=1
            )
            road_density = st.number_input(
                "Road density (km/km²)", min_value=0.0, step=0.1
            )
        with col2:
            electricity_coverage = st.number_input(
                "Electricity coverage (%)", min_value=0.0, max_value=100.0, step=1.0
            )
            water_access = st.number_input(
                "Water access (%)", min_value=0.0, max_value=100.0, step=1.0
            )
            equality_index = st.number_input(
                "Equality Index (EIS)", min_value=0.0, max_value=100.0, step=0.1
            )
        with col3:
            need_factor = st.number_input(
                "Need Factor (0–1)", min_value=0.0, max_value=1.0, step=0.01
            )
            health_per_10k = st.number_input(
                "Health facilities per 10,000", min_value=0.0, step=0.1
            )
            schools_per_10k = st.number_input(
                "Schools per 10,000", min_value=0.0, step=0.1
            )
            emergency_units_index = st.number_input(
                "Emergency units index", min_value=0.0, step=0.1
            )

        if st.button("Save metrics"):
            upsert_constituency(
                name=constituency,
                ambulances_count=int(ambulances_count),
                hospitals_count=int(hospitals_count),
                equality_index=float(equality_index) if equality_index else None,
                need_factor=float(need_factor) if need_factor else None,
                road_density=float(road_density) if road_density else None,
                electricity_coverage=float(electricity_coverage)
                if electricity_coverage
                else None,
                water_access=float(water_access) if water_access else None,
                health_per_10k=float(health_per_10k) if health_per_10k else None,
                schools_per_10k=float(schools_per_10k)
                if schools_per_10k
                else None,
                emergency_units_index=float(emergency_units_index)
                if emergency_units_index
                else None,
            )
            st.success("Constituency metrics saved.")

    # Ambulances
    with tab2:
        st.subheader("Register Ambulances")

        with st.form("ambulance_form"):
            amb_name = st.text_input("Ambulance name / identifier")
            amb_plate = st.text_input("Number plate")
            amb_hospital = st.text_input("Attached hospital")
            amb_location = st.text_input("Base location / ward")
            submit_amb = st.form_submit_button("Add ambulance")

        if submit_amb:
            if amb_name and amb_plate:
                add_ambulance(
                    constituency_name=constituency,
                    name=amb_name,
                    number_plate=amb_plate,
                    attached_hospital=amb_hospital,
                    location=amb_location,
                )
                st.success("Ambulance registered.")
            else:
                st.error("Name and number plate are required.")

        ambulances = get_ambulances(constituency)
        if ambulances:
            df_amb = pd.DataFrame(
                ambulances,
                columns=[
                    "id",
                    "name",
                    "number_plate",
                    "attached_hospital",
                    "location",
                ],
            )
            st.subheader("Registered ambulances")
            st.dataframe(df_amb, use_container_width=True)
        else:
            st.info("No ambulances registered yet.")

    # Projects
    with tab3:
        st.subheader("Register Development Projects")

        with st.form("project_form"):
            proj_name = st.text_input("Project name")
            proj_status = st.selectbox("Status", ["Planned", "Ongoing", "Completed"])
            proj_budget = st.number_input(
                "Budget (KES)", min_value=0.0, step=100000.0
            )
            proj_implementer = st.text_input("Implementer")
            proj_timeline = st.text_input("Timeline (e.g. 2025–2027)")
            proj_verif = st.selectbox(
                "Verification status", ["Pending", "Verified", "Flagged", "Unknown"]
            )
            proj_location = st.text_input(
                "Project location (ward, coordinates, landmark)"
            )
            proj_lat = st.number_input("Latitude (optional)", format="%.6f")
            proj_lon = st.number_input("Longitude (optional)", format="%.6f")
            proj_desc = st.text_area("Description / notes")
            submit_proj = st.form_submit_button("Add project")

        if submit_proj:
            if proj_name:
                add_project(
                    constituency_name=constituency,
                    name=proj_name,
                    status=proj_status,
                    budget=float(proj_budget),
                    implementer=proj_implementer,
                    timeline=proj_timeline,
                    verification_status=proj_verif,
                    location=proj_location,
                    description=proj_desc,
                    lat=float(proj_lat) if proj_lat else None,
                    lon=float(proj_lon) if proj_lon else None,
                )
                st.success("Project registered.")
            else:
                st.error("Project name is required.")

        projects = get_projects_by_constituency(constituency)
        if projects:
            df_proj = pd.DataFrame(
                projects,
                columns=[
                    "id",
                    "name",
                    "status",
                    "budget",
                    "implementer",
                    "timeline",
                    "verification_status",
                    "location",
                    "description",
                    "lat",
                    "lon",
                ],
            )
            st.subheader("Registered projects")
            st.dataframe(df_proj, use_container_width=True)
        else:
            st.info("No projects registered yet.")


# ------------- TEMP ADMIN: CREATE LEADER -------------

def debug_create_leader_form():
    """Temporary admin form to create a leader directly from the UI."""
    with st.expander("⚙️ Debug: Create leader (temporary admin tool)"):
        u = st.text_input("New leader username")
        p = st.text_input("New leader password", type="password")
        c = st.text_input("Constituency for this leader", value="AINABKOI")
        if st.button("Create leader user"):
            from db_backend import ensure_leader

            ensure_leader(u, p, c)
            st.success(
                f"Leader '{u}' for '{c}' created. You can now log in in the sidebar."
            )


# ------------- CITIZEN VIEW (projects + media) -------------

def citizen_view():
    st.header("INFRASIGHT – Citizen Role Dashboard")

    st.write(
        "Browse real projects, see uploaded photos/videos, and contribute your own observations."
    )

    st.subheader("1. Select constituency")
    constituency_name = st.text_input(
        "Enter constituency name (must match what leaders use)", value="AINABKOI"
    )

    projects = []
    if constituency_name:
        projects = get_projects_by_constituency(constituency_name)

    if not projects:
        st.info("No projects found for that constituency yet.")
        return

    df = pd.DataFrame(
        projects,
        columns=[
            "id",
            "name",
            "status",
            "budget",
            "implementer",
            "timeline",
            "verification_status",
            "location",
            "description",
            "lat",
            "lon",
        ],
    )

    st.subheader("2. Pick a project")
    proj_options = {
        f"{row['name']} (#{row['id']})": int(row["id"]) for _, row in df.iterrows()
    }
    selected_label = st.selectbox("Project", list(proj_options.keys()))
    selected_id = proj_options[selected_label]

    project = get_project_by_id(selected_id)
    if not project:
        st.error("Project not found.")
        return

    (
        pid,
        p_constituency,
        p_name,
        p_status,
        p_budget,
        p_impl,
        p_timeline,
        p_verif,
        p_location,
        p_desc,
        p_lat,
        p_lon,
    ) = project

    st.markdown(f"### Project: {p_name}")
    st.write(f"**Constituency:** {p_constituency}")
    st.write(f"**Status:** {p_status}")
    st.write(f"**Budget:** {p_budget}")
    st.write(f"**Implementer:** {p_impl}")
    st.write(f"**Timeline:** {p_timeline}")
    st.write(f"**Verification:** {p_verif}")
    st.write(f"**Location:** {p_location}")
    if p_desc:
        st.write(p_desc)

    st.markdown("---")
    st.subheader("3. Project evidence & media")

    # Upload form
    with st.form("media_upload_form"):
        uploader_name = st.text_input("Your name (optional)")
        caption = st.text_area("Comment / observation")
        uploaded_files = st.file_uploader(
            "Upload photos/videos (you can select multiple)",
            type=["jpg", "jpeg", "png", "mp4", "mov", "avi"],
            accept_multiple_files=True,
        )
        submit_media = st.form_submit_button("Submit evidence")

    if submit_media and uploaded_files:
        for f in uploaded_files:
            ext = f.name.lower().split(".")[-1]
            if ext in ["jpg", "jpeg", "png"]:
                media_type = "image"
            else:
                media_type = "video"

            save_media_file(
                project_id=pid,
                filename=f.name,
                content=f.read(),
                media_type=media_type,
                caption=caption,
                uploader_name=uploader_name or "Anonymous",
            )
        st.success("Your evidence has been submitted.")

    # Gallery
    media_items = get_media_for_project(pid)
    if media_items:
        st.markdown("#### Gallery")

        images = [m for m in media_items if m[1] == "image"]
        videos = [m for m in media_items if m[1] == "video"]

        if images:
            st.write("Photos:")
            cols = st.columns(3)
            for idx, m in enumerate(images):
                mid, mtype, path, mcap, muploader, mtime = m
                col = cols[idx % 3]
                with col:
                    st.image(path, use_container_width=True)
                    if mcap:
                        st.caption(mcap)
                    st.caption(f"By {muploader} • {mtime}")

        if videos:
            st.write("Videos:")
            for m in videos:
                mid, mtype, path, mcap, muploader, mtime = m
                st.video(path)
                if mcap:
                    st.caption(mcap)
                st.caption(f"By {muploader} • {mtime}")
    else:
        st.info("No media has been uploaded for this project yet.")


# ------------- MAIN ROLE SELECTION -------------

def main():
    st.title("INFRASIGHT – Infrastructure Equality Platform")
    st.caption("Citizens • Implementers • Leaders • Admins")

    st.markdown("### Welcome to INFRASIGHT.")
    st.write("Select your role to enter the appropriate workspace.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### I am logging in as:")
        citizen_btn = st.button("Citizen")
        leader_btn = st.button("Leader")

    if citizen_btn:
        st.session_state.role = "citizen"
    if leader_btn:
        st.session_state.role = "leader"

    st.markdown("---")

    # TEMP admin tool to create leader accounts
    debug_create_leader_form()

    if st.session_state.role == "leader":
        leader_panel()
    elif st.session_state.role == "citizen":
        citizen_view()
    else:
        st.info("Choose a role above to continue.")


if __name__ == "__main__":
    main()
