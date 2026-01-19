<?php
    defined('MOODLE_INTERNAL') || die();

    $observers = [
        [
            'eventname' => '\core\event\user_loggedin',
            'callback'  => '\local_interest_survey\observer::user_loggedin',
            'internal'  => false,
            'priority'  => 1000,
        ],
    ];
