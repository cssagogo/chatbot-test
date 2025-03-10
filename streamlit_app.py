import streamlit as st
from openai import OpenAI

# Set page config
st.set_page_config(
    page_title="SpotGPT | iSpot.tv",
    initial_sidebar_state="collapsed"
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Add logos
st.logo(image="images/ispot-logo.png", 
        icon_image="images/ispot-logo.png", size="large")

# Inject CSS
st.markdown('<style>' + open('styles.css').read() + '</style>', unsafe_allow_html=True)

# Build sidebard
with st.sidebar:
    st.header("Ad Collection")

    ad_collection = st.selectbox(
        'Choose an Ad Collection:',
        [
            'Eli Lilly', 
            'Consumer Cellular', 
            'Zillow', 
            'Progressive',
            'Balance of Nature'
        ],
        label_visibility="collapsed"
    )

# Show opening question
if "messages" not in st.session_state:
    st.title("What would you like to know about your ads?")
    st.write(
        '<span class="muted">SpotGPT can make mistakes. Please verify important information.</span>', 
        unsafe_allow_html=True
    )

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "You are a conversational AI developed by iSpot.tv to assist with inquiries and tasks about " + ad_collection + "'s TV ads. Always keep in mind that you are discussing " + ad_collection + "'s TV ads in this context. All your responses should refer to " + ad_collection + "'s TV ads.  When you are talking to someone, and they refer to 'my tv ads', the are referring to " + ad_collection}  # Hidden system context
    ]

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    if message["role"] != "system":  # Skip displaying system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("Ask SpotGPT a question about " + ad_collection + "'s ad collection."):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API.
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})


