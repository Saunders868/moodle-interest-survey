<?php
require_once(__DIR__ . '/../../config.php');

defined('MOODLE_INTERNAL') || die();

global $PAGE, $OUTPUT, $DB, $USER;

require_login();

$context = context_system::instance();
$PAGE->set_context($context);
$PAGE->set_url(new moodle_url('/local/interest_survey/index.php'));
$PAGE->set_title('Digital Skills Assessment');
$PAGE->set_heading('Digital Skills Assessment');

require_once(__DIR__ . '/classes/form/survey_form.php');

$form = new \local_interest_survey\form\survey_form();

if ($form->is_cancelled()) {
    redirect(new moodle_url('/'));
} else if ($data = $form->get_data()) {

    // Map textual choices to numeric scores.
    $score_map = [
        'Foundational' => 1,
        'Intermediate' => 2,
        'Advanced' => 3,
        'Highly Specialised' => 4
    ];

    // Categories mapping corresponding question fields.
    $categories = [
        'Information & Digital Literacy' => ['q1','q2','q3'],
        'Communication & Collaboration'  => ['q4','q5'],
        'Digital Content Creation'       => ['q6','q7'],
        'Safety & Security'              => ['q8','q9','q10','q11'],
        'Problem Solving'                => ['q12','q13'],
        'Entrepreneurship'               => ['q14'],
        'Attitude to Digital Environment'=> ['q15']
    ];

    $total_score = 0;
    $category_scores = [];

    foreach ($categories as $catname => $questions) {
        $cat_total = 0;
        foreach ($questions as $qfield) {
            $choice = isset($data->{$qfield}) ? $data->{$qfield} : 'Foundational';
            $qscore = isset($score_map[$choice]) ? $score_map[$choice] : 1;
            $cat_total += $qscore;
            $total_score += $qscore;
        }
        $category_scores[$catname] = $cat_total;
    }

    // Classification thresholds.
    if ($total_score <= 25) {
        $classification = 'Foundational';
    } else if ($total_score <= 40) {
        $classification = 'Intermediate';
    } else if ($total_score <= 52) {
        $classification = 'Advanced';
    } else {
        $classification = 'Highly Specialised';
    }

    // Save survey record.
    $record = new stdClass();
    $record->userid = $USER->id;
    $record->fullname = $data->fullname;
    $record->email = $data->email;
    $record->department = $data->department;
    $record->date = isset($data->date) ? $data->date : time();
    $record->totalscore = $total_score;
    $record->classification = $classification;
    $record->category_scores = json_encode($category_scores);
    $record->timecreated = time();

    $DB->insert_record('local_interest_survey', $record);

    // Mark user as completed so the form does not show again.
    set_user_preference('interest_survey_completed', 1, $USER);

    /*
     * ---------------------------------------------------------
     * UPDATE USER INTERESTS TAGS
     * ---------------------------------------------------------
     */

    // 1. Load existing interests (tags)
    require_once($CFG->dirroot . '/tag/lib.php');
    $usercontext = context_user::instance($USER->id);
    $existing_tags = core_tag_tag::get_item_tags_array('core', 'user', $USER->id);

    // 2. Add classification as a new interest
    $new_interest = "Digital Skills: $classification";

    if (!in_array($new_interest, $existing_tags)) {
        $existing_tags[] = $new_interest;
    }

    // 3. Save tags back into Moodle
    core_tag_tag::set_item_tags(
        'core',
        'user',
        $USER->id,
        $usercontext,
        $existing_tags
    );

    /*
     * ---------------------------------------------------------
     * END INTERESTS UPDATE
     * ---------------------------------------------------------
     */

    // Recommendations.
    switch ($classification) {
        case 'Foundational':
            $recommendation = 'Enroll in Digital Skills Foundation Course';
            break;
        case 'Intermediate':
            $recommendation = 'Continue with Intermediate Learning Path';
            break;
        case 'Advanced':
            $recommendation = 'Eligible for Advanced Digital Skills Certification';
            break;
        default:
            $recommendation = 'Consider applying as a Digital Skills Mentor';
    }

    // Output results.
    echo $OUTPUT->header();
    echo $OUTPUT->heading('Assessment Complete!');
    echo html_writer::tag('p', 'Your Total Score: ' . $total_score . ' / 60');
    echo html_writer::tag('p', 'Your Classification: ' . $classification);
    echo html_writer::tag('p', 'Recommended Next Step: ' . $recommendation);
    echo $OUTPUT->continue_button(new moodle_url('/'));
    echo $OUTPUT->footer();
    exit;
}

echo $OUTPUT->header();
$form->display();
echo $OUTPUT->footer();
