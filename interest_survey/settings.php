<?php
    defined('MOODLE_INTERNAL') || die();

    if ($hassiteconfig) {
        $settings = new admin_settingpage('local_interest_survey', get_string('pluginname', 'local_interest_survey'));
        $ADMIN->add('localplugins', $settings);
    }
