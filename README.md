# Digital Skills Assessment Survey for Moodle

## Short Description
This Moodle plugin presents a **Digital Skills Assessment** to users on their first login. Based on their answers, it calculates a score, classifies their digital skill level, and updates their **Interests** profile field automatically. Recommended learning paths are also displayed to guide users.

---

## Features
- **Custom survey form** with 15 questions covering:
  - Information & Digital Literacy
  - Communication & Collaboration
  - Digital Content Creation
  - Safety & Security
  - Problem Solving
  - Entrepreneurship
  - Attitude to Digital Environment
- **Automatic scoring** and classification:
  - Foundational
  - Intermediate
  - Advanced
  - Highly Specialised
- **Saves results** in a custom plugin table (`local_interest_survey`)
- **Updates Moodle Interests field** without overwriting existing tags
- Prevents repeated submissions using a user preference flag
- Displays personalized recommendation after submission

---

## Installation

1. Place the plugin in your Moodle installation:
moodle/local/interest_survey/

The folder structure should look like this:
├── classes/
│ └── form/
│ └── survey_form.php
├── db/
│ └── install.xml
├── index.php
└── version.php


2. Navigate to **Site Administration → Notifications** to install the plugin and create the database table.

3. Ensure users can access the survey:
- You can add a **first-login redirect** using an event observer or via a custom block/page.

4. Verify that the plugin works:
- Log in as a test user
- Complete the survey
- Check the **Interests** field in the user profile for the classification tag.

---

## How it Works

1. The survey is displayed using Moodle's `formslib` API.
2. User responses are mapped to numeric scores.
3. Scores are totaled per category and overall.
4. Classification thresholds determine the user's skill level.
5. The **Interests** profile field is updated using Moodle’s **Tag API**:
```php
core_tag_tag::set_item_tags('core', 'user', $USER->id, context_user::instance($USER->id), $tags);

Results are stored in the plugin’s table (local_interest_survey) for reporting purposes.
Users are shown a recommendation based on their classification.

Requirements:
Moodle 5.0 or higher
PHP 8.2+ recommended
