#!/usr/bin/env php

<?php

declare(strict_types=1);

if (file_exists(__DIR__.'/vendor/autoload.php')) {
    require __DIR__.'/vendor/autoload.php';
}

use StandWithCyprus\StandWithCyprusCommand;
use Symfony\Component\Console\Application;
use Symfony\Component\Console\Exception\ExceptionInterface;

try {
    $application = new Application('stand-with-cyprus', '1.0.0');
    $application->add(new StandWithCyprusCommand());
    $application->setDefaultCommand('stand-with-cyprus', true);
    $application->run();
} catch (ExceptionInterface $e) {
}
