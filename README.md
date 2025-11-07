# Email AI Agent

An intelligent email automation system that monitors inbox for new emails and generates automated responses based on content analysis. The system uses Gmail's IMAP and SMTP protocols for email operations and implements smart response generation based on message context.

## Features

- Real-time Email Monitoring
- Automated Response Generation
- Smart Content Analysis
- Multi-encoding Support
- Secure Email Authentication
- Continuous Operation Mode

## Technical Stack

- Python 3.x
- IMAP/SMTP Protocols
- Gmail API Integration

## Setup

1. Clone the repository:
```bash
git clone https://github.com/tanshi2003/Email-Ai-agent.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Gmail:
   - Enable 2-Step Verification in your Google Account
   - Generate an App Password for this application
   - Update the credentials in `email_agent.py`

## Usage

Run the email agent:
```bash
python email_agent.py
```

## Security Note

- Never commit your email credentials to Git
- Use environment variables or configuration files for sensitive data
- Always use App-specific passwords for Gmail

## Project Structure

- `email_agent.py`: Main application entry point
- `email_reader.py`: Handles email retrieval and processing
- `email_sender.py`: Manages email sending operations
- `ai_logic.py`: Implements response generation logic