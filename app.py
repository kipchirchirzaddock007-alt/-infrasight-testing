import streamlit as st


def main():
    st.set_page_config(
        page_title="INFRASIGHT Platform",
        page_icon="🌍",
        layout="wide",
    )

    st.title("INFRASIGHT – Infrastructure Equality Platform")
    st.caption("Citizens • Implementers • Leaders • Admins")

    st.markdown(
        """
Welcome to **INFRASIGHT**.  
Select your role to enter the appropriate workspace.
        """
    )

    # Simple role selector on the homepage.
    # In production, this role will come from your authentication layer.
    role = st.selectbox(
        "I am logging in as:",
        ["Citizen", "Implementer", "Leader", "Admin"],
        index=0,
    )

    st.markdown("---")

    st.markdown(f"### Continue as **{role}**")

    st.write(
        {
            "Citizen": "Explore equality, report issues, and see development in your area.",
            "Implementer": "Manage reports, plan interventions, and update execution status.",
            "Leader": "Track issues in your constituency, follow implementers, and communicate with citizens.",
            "Admin": "Oversee users, data, resources, and system-level governance.",
        }[role]
    )

    # Navigation buttons per role
    if role == "Citizen":
        if st.button("Open Citizen Dashboard"):
            # Multipage apps (Streamlit >= 1.22) – ensure file name matches exactly
            st.switch_page("pages/10_Citizen.py")

    elif role == "Implementer":
        if st.button("Open Implementer Console"):
            st.switch_page("pages/11_Implementer.py")

    elif role == "Leader":
        if st.button("Open Leader Dashboard"):
            st.switch_page("pages/13_Leader.py")

    elif role == "Admin":
        if st.button("Open Admin Dashboard"):
            st.switch_page("pages/12_Admin.py")

    st.markdown("---")

    st.info(
        "Note: In the production version, this role selection will be automatic based on login "
        "(email/phone + password + 2FA), and users will be taken directly to their role dashboard."
    )


if __name__ == "__main__":
    main()
