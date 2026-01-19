<?php
    namespace local_interest_survey\form;

    defined('MOODLE_INTERNAL') || die();
    require_once($CFG->libdir . '/formslib.php');

    class survey_form extends \moodleform {

        private $options = [
            'Foundational'        => 'I don\'t know how to do it – Foundational',
            'Intermediate'        => 'I can do it with guidance – Intermediate',
            'Advanced'            => 'I can do it on my own – Advanced',
            'Highly Specialised'  => 'I can do it with confidence and guide others – Highly Specialised',
        ];

        public function definition() {
            global $CFG;
            $mform = $this->_form;

            // Learner info
            $mform->addElement('header', 'learnerinfo', 'Section 1: Learner Information');
            $mform->addElement('text', 'fullname', 'Full Name');
            $mform->setType('fullname', PARAM_TEXT);
            $mform->addRule('fullname', get_string('required'), 'required');

            $mform->addElement('text', 'email', 'Email Address');
            $mform->setType('email', PARAM_EMAIL);
            $mform->addRule('email', get_string('required'), 'required');

            $mform->addElement('text', 'department', 'Department / Course');
            $mform->setType('department', PARAM_TEXT);

            $mform->addElement('date_selector', 'date', 'Date');

            // Information & Digital Literacy
            $mform->addElement('header', 'idl', 'Information & Digital Literacy');
            $mform->addElement('select', 'q1', '1. I can identify my information needs and find data/content through a simple search.', $this->options);
            $mform->addRule('q1', get_string('required'), 'required');
            $mform->addElement('select', 'q2', '2. I know how to use a search engine effectively using personal strategies.', $this->options);
            $mform->addRule('q2', get_string('required'), 'required');
            $mform->addElement('select', 'q3', '3. I know how to manage and organize emails effectively.', $this->options);
            $mform->addRule('q3', get_string('required'), 'required');

            // Communication & Collaboration
            $mform->addElement('header', 'cc', 'Communication & Collaboration');
            $mform->addElement('select', 'q4', '4. I can select appropriate digital communication tools for a given context.', $this->options);
            $mform->addRule('q4', get_string('required'), 'required');
            $mform->addElement('select', 'q5', '5. I know how to exercise proper behavioural norms when using digital technologies.', $this->options);
            $mform->addRule('q5', get_string('required'), 'required');

            // Digital Content Creation
            $mform->addElement('header', 'dcc', 'Digital Content Creation');
            $mform->addElement('select', 'q6', '6. I can create and edit digital text files (Word, Google Docs, etc.).', $this->options);
            $mform->addRule('q6', get_string('required'), 'required');
            $mform->addElement('select', 'q7', '7. I can use online learning tools to improve my digital skills.', $this->options);
            $mform->addRule('q7', get_string('required'), 'required');

            // Safety & Security
            $mform->addElement('header', 'ss', 'Safety & Security');
            $mform->addElement('select', 'q8', '8. I can check if a website is secure before providing personal data.', $this->options);
            $mform->addRule('q8', get_string('required'), 'required');
            $mform->addElement('select', 'q9', '9. I can protect my devices and content from risks and threats.', $this->options);
            $mform->addRule('q9', get_string('required'), 'required');
            $mform->addElement('select', 'q10', '10. I know how to avoid health risks related to digital technology use.', $this->options);
            $mform->addRule('q10', get_string('required'), 'required');
            $mform->addElement('select', 'q11', '11. I know how to stay safe when making online purchases.', $this->options);
            $mform->addRule('q11', get_string('required'), 'required');

            // Problem Solving
            $mform->addElement('header', 'ps', 'Problem Solving');
            $mform->addElement('select', 'q12', '12. When I face a technical problem, I can find solutions online.', $this->options);
            $mform->addRule('q12', get_string('required'), 'required');
            $mform->addElement('select', 'q13', '13. I can troubleshoot basic hardware issues.', $this->options);
            $mform->addRule('q13', get_string('required'), 'required');

            // Entrepreneurship
            $mform->addElement('header', 'ent', 'Entrepreneurship');
            $mform->addElement('select', 'q14', '14. I am capable of creating a business out of my digital skills.', $this->options);
            $mform->addRule('q14', get_string('required'), 'required');

            // Attitude to Digital Environment
            $mform->addElement('header', 'ade', 'Attitude to Digital Environment');
            $mform->addElement('select', 'q15', '15. I am comfortable using technology to access services.', $this->options);
            $mform->addRule('q15', get_string('required'), 'required');

            $this->add_action_buttons(true, 'Submit Assessment');
        }
    }
