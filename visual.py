import streamlit as st


def custom_alert(title, message):
    st.success(title)
    st.write(f'<p style="text-align: justify;">{message}</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("The app development is in progress. And current version is early beta version.")


# Building UI
st.title("Brand positioning analyser")


if __name__ == '__main__':
    print("Running visual ...")
else:
    print("Initialization visual models ...")