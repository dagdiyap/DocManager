"""Message templates for WhatsApp bot."""

def welcome_message(client_name: str) -> str:
    """Welcome message with main menu."""
    return f"""👋 Welcome {client_name}!

Reply with:
1️⃣ Download Documents
2️⃣ Upload Documents
3️⃣ Talk to CA

🌐 Website: https://ca-lokesh-dagdiya.vercel.app"""


def unregistered_message() -> str:
    """Message for unregistered phone numbers."""
    return """This number is not registered with Dagdiya Associates.

Please contact us:
📞 +91 98901 54945
📧 lokeshdagdiya@gmail.com"""


def year_menu(years: list[str]) -> str:
    """Generate year selection menu."""
    options = "\n".join([f"{i+1}️⃣ {year}" for i, year in enumerate(years)])
    return f"""Select Year:
{options}"""


def document_type_menu(doc_types: list[str]) -> str:
    """Generate document type selection menu."""
    options = "\n".join([f"{i+1}️⃣ {doc_type}" for i, doc_type in enumerate(doc_types)])
    return f"""Select Document Type:
{options}
{len(doc_types)+1}️⃣ All Documents"""


def upload_prompt() -> str:
    """Prompt for document upload."""
    return """📤 Please send your documents (PDF, images, or zip files).

When done, reply DONE."""


def upload_confirmation(file_count: int, file_names: list[str]) -> str:
    """Confirmation after successful upload."""
    file_list = "\n".join([f"- {name}" for name in file_names])
    return f"""✅ Received {file_count} file(s):
{file_list}

Uploading to CA's system... Done!
CA will review shortly."""


def manual_mode_message() -> str:
    """Message when switching to manual CA chat."""
    return """📞 Connecting you to CA...

You can now chat directly. CA will respond shortly."""


def invalid_input_message() -> str:
    """Message for invalid input."""
    return """Invalid option. Please reply with a number (1, 2, or 3)."""


def document_sending_message(doc_type: str) -> str:
    """Message while sending document."""
    return f"""📄 Sending {doc_type}..."""


def document_sent_message() -> str:
    """Confirmation after document sent."""
    return """✅ Document sent successfully!

Need anything else?
1️⃣ Download more documents
2️⃣ Main menu
3️⃣ Exit"""


def no_documents_found_message(year: str = None, doc_type: str = None) -> str:
    """Message when no documents found."""
    if year and doc_type:
        return f"""❌ No {doc_type} documents found for {year}.

Please contact CA for assistance."""
    elif year:
        return f"""❌ No documents found for {year}.

Please contact CA for assistance."""
    else:
        return """❌ No documents found.

Please contact CA for assistance."""


def error_message() -> str:
    """Generic error message."""
    return """❌ Something went wrong. Please try again or contact CA.

📞 +91 98901 54945"""


def goodbye_message() -> str:
    """Exit message."""
    return """👋 Thank you for using Dagdiya Associates bot!

Type HI anytime to start again."""
