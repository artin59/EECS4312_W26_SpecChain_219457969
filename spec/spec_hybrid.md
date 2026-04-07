# Requirement ID: FR_auto_1
- Description: The system shall clearly display the duration  of the free trial on the app's sign-up page.
- Source Persona: Frustrated Fiona
- Traceability: Derived from review group A1
- Acceptance Criteria: Given a user is on the app's sign-up page, When they tap on the "Start Free Trial" button, Then they are presented with a clear and concise summary of the free trial terms.
- Notes: Had multiple requirements in 1 so I split them up into two

# Requirement ID: FR_auto_1.5
- Description: The system shall clearly display any charges that will be incurred after the trial period, on the app's sign-up page.
- Source Persona: Frustrated Fiona
- Traceability: Derived from review group A1
- Acceptance Criteria: Given a user is on the app's sign-up page, When they tap on the "Start Free Trial" button, Then they are presented with a clear and concise summary of the free trial terms.
- Notes: Had multiple requirements in 1 so I split them up into two

# Requirement ID: FR_auto_2
- Description: The system shall provide an easy-to-use cancellation process that allows users to cancel their subscription within 5 steps.
- Source Persona: Frustrated Fiona
- Traceability: Derived from review group A1
- Acceptance Criteria: Given a user is logged into their account, When they navigate to the account settings, Then they can cancel their subscription within 5 steps.
- Notes: Ambigous wording ("minimal number of steps") so i removed it

# Requirement ID: FR_auto_3
- Description: The system shall notify the user of their successful cancelation after they cancel their subscription
- Source Persona: Frustrated Fiona
- Traceability: Derived from review group A1
- Acceptance Criteria: Given a user has canceled their subscription, When the system processes the cancellation, Then a confirmation notification is sent to the user
- Notes: Had implementation details and was way too detailed for a good requirment so i removed it the parts talking about emailing specific details with a simply notify the user

# Requirement ID: FR_auto_4
- Description: The system shall provide a library of at least 500 meditation sessions, with a minimum of 20 new sessions added every month.
- Source Persona: Disappointed Calm User
- Traceability: Derived from review group A2
- Acceptance Criteria: Given the user has a stable internet connection, When the user accesses the meditation library, Then they can browse and play at least 500 meditation sessions, with clear indications of new content added within the last month.
- Notes: No changes

# Requirement ID: FR_auto_5
- Description: The system shall ensure that all audio content is encoded at a minimum of 128 kbps bitrate 
- Source Persona: Disappointed Calm User
- Traceability: Derived from review group A2
- Acceptance Criteria: Given the user has a device capable of playing high-quality audio, When the user plays any meditation session or sleep story, Then the audio plays without distortion or skipping, with clear and crisp sound.
- Notes: Many requirements in 1 so i removed them (had "and"s) 

# Requirement ID: FR_auto_6
- Description: The system shall allow users to search sleep stories by categories
- Source Persona: Disappointed Calm User
- Traceability: Derived from review group A2
- Acceptance Criteria: Given the user has access to the sleep story section, When the user applies searches for sleep stories, Then the system displays a list of relevant sleep stories that match the user's criteria, with clear information on story type, narrator, and duration.
- Notes: Again had multiple requirements withint one so i removed them and concised it into 1 good requirement format3

# Requirement ID: FR_auto_7
- Description: The system shall have an uptime of 99.99%
- Source Persona: Alex Chen
- Traceability: Derived from review group A3
- Acceptance Criteria: Given a user has a stable internet connection, When the user initiates a meditation session, Then the session shall play continuously without interruption or glitch.
- Notes: The requirement was way too broad and ambiguous so I replaced it with an NFR about availability metrics (uptime)

# Requirement ID: FR_auto_8
- Description: The system shall provide screen reader functionality
- Source Persona: Alex Chen
- Traceability: Derived from review group A3
- Acceptance Criteria: Given a user with vision impairments is using the app, When the user enables screen reader feature, Then the app shall provide screen reader functionality across the whole app
- Notes: Requirement was way too broad and ambigous so I brought it down to one accesebaility feature

# Requirement ID: FR_auto_

- Notes: I removed this requirement because it didn't make any sense, had multiple requirements within 1, and was way too broad and ambigous. In all it was beyond saving

# Requirement ID: FR_auto_
- Notes: I removed this requirement because it didn't make any sense, had multiple requirements within 1, and was way too broad and ambigous. In all it was beyond saving


# Requirement ID: FR_auto_11
- Description: The system shall shall allow the user loop to audio playback
- Source Persona: Mindful Emma
- Traceability: Derived from review group A4
- Acceptance Criteria: Given a user has navigated to the sleep section, When they select a sleep story or sound, Then the audio can be looped continuously.
- Notes: Requirement had multiple requirements and too ambigous so I brought it down to one feature

# Requirement ID: FR_auto_12
- Description: The system shall track a user's progress in meditation practices
- Source Persona: Mindful Emma
- Traceability: Derived from review group A4
- Acceptance Criteria: Given a user has completed a meditation or sleep session, When they view their progress dashboard, Then their total number of sessions are displayed accurately 
- Notes: Too ambigous and multiple requirements so I brought it down to 1 good requirement

# Requirement ID: FR_auto_13
- Notes: This is the same as requirement 1 and 1.5

# Requirement ID: FR_auto_14
- Description: The system shall provide a response from customer support within 1 week
- Source Persona: Skeptical Sarah
- Traceability: Derived from review group A5
- Acceptance Criteria: Given a user has a subscription or billing issue, When they submit a support request through the app or website, Then they shall receive a response within 1 week
- Notes: Requirement was too ambigous and broad. I made it into an NFR with a more reasanable timeline for response

# Requirement ID: FR_auto_15
- Description: The system shall provide users with the ability to delete their personal data
- Source Persona: Skeptical Sarah
- Traceability: Derived from review group A5
- Acceptance Criteria: Given a user wants to delete their personal data, When they navigate to the app's settings or account section and press the delete button, Then their personal data should be deleted within 72 hours
- Notes: There was multiple requirements so i boiled it down into 1
