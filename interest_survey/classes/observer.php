<?php
    namespace local_interest_survey;
    defined('MOODLE_INTERNAL') || die();

    use moodle_url;

    class observer {

        /**
         * User logged in event observer.
         *
         * Redirects a user on first login (or if survey not completed) to the survey page.
         */
        public static function user_loggedin(\core\event\user_loggedin $event) {
            global $USER, $SESSION;

            // Don't redirect admins (optional).
            if (is_siteadmin($USER)) {
                return;
            }

            // If user already marked as complete, do nothing.
            $completed = get_user_preferences('interest_survey_completed', 0, $USER);
            if ($completed) {
                return;
            }

            // If it's first login (lastlogin == 0) or not completed, redirect.
            // lastlogin is 0 on first successful login.
            if (empty($USER->lastlogin) || !$completed) {
                // ensure we don't loop by setting a wantsurl and redirecting only once.
                $surveyurl = new moodle_url('/local/interest_survey/index.php');
                // Save wantsurl so after login flow Moodle can handle properly
                $SESSION->wantsurl = $surveyurl;
                redirect($surveyurl);
            }
        }
    }
