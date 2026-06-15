import streamlit as st
from auth import check_login
from styles import get_css

def render_login():
    st.markdown(get_css(), unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="small")

    with col_left:
        st.markdown("""
        <div class="login-left">
            <img src="https://www.rareglobalfood.com/_next/image?url=%2Fimages%2Fhero%2FRare-Website-Mockup-12.avif&w=640&q=75&dpl=dpl_6vdcgELGC6YVk7vrgyNQioBcioQu"
                 alt=""
                 style="position:absolute;top:0;left:0;right:0;bottom:0;width:100%;height:100%;object-fit:cover;object-position:center;z-index:0;display:block;">
            <div class="login-left-overlay"></div>
            <div class="login-left-content">
                <div class="login-brand-big">RARE</div>
                <div class="login-brand-sub">GLOBAL FOOD</div>
                <div class="login-tagline">
                    Lender Target Database<br>
                    <span style="font-size:0.8rem;color:#FFFFFF;letter-spacing:2px;text-transform:uppercase;font-weight:600;text-shadow:0 1px 8px rgba(0,0,0,0.9);">
                        Finance Intelligence Platform
                    </span>
                </div>
                <div style="margin-top:48px;">
                    <div style="width:48px;height:3px;background:#86000B;margin:0 auto 16px;"></div>
                    <div style="font-size:0.7rem;letter-spacing:3px;color:#FFFFFF;text-align:center;text-transform:uppercase;font-weight:600;text-shadow:0 1px 8px rgba(0,0,0,0.9);">
                        Internal Use Only
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Vertical spacer to push form to center
        st.markdown('<div style="height:calc(50vh - 200px);min-height:40px;"></div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-bottom:28px;">
            <img src="https://www.rareglobalfood.com/_next/image?url=%2Fimages%2Fbrand%2Flogo-light-bg.png&w=256&q=75&dpl=dpl_6vdcgELGC6YVk7vrgyNQioBcioQu"
                 style="height:56px;width:auto;object-fit:contain;margin-bottom:20px;display:block;margin-left:auto;margin-right:auto;"
                 alt="RARE Global Food">
            <div style="font-size:1.2rem;font-weight:800;letter-spacing:3px;
                        text-transform:uppercase;color:#1B2419;margin-bottom:8px;">
                Sign In
            </div>
            <div style="font-size:0.75rem;color:#6B7068;margin-bottom:20px;letter-spacing:1px;">
                Authorized Personnel Only
            </div>
            <div style="width:40px;height:3px;background:#86000B;margin:0 auto;"></div>
        </div>
        """, unsafe_allow_html=True)

        _, form_col, _ = st.columns([1, 5, 1])
        with form_col:
            username = st.text_input("Username", placeholder="Enter username", key="lu")
            password = st.text_input("Password", placeholder="Enter password", type="password", key="lp")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("SIGN IN", use_container_width=True, key="ls"):
                if check_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.markdown('<div class="alert-error">Invalid credentials.</div>', unsafe_allow_html=True)
