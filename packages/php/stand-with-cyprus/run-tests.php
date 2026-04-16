<?php

declare(strict_types=1);

require_once __DIR__ . '/vendor/autoload.php';

use StandWithCyprus\StandWithCyprusCommand;
use Symfony\Component\Console\Application;
use Symfony\Component\Console\Tester\ApplicationTester;
use Symfony\Component\Console\Tester\CommandTester;

echo "Running Stand With Cyprus Tests\n";
echo "=====================================\n\n";

// Test 1: Command execution
echo "Test 1: Command execution\n";
try {
    $application = new Application();
    $application->add(new StandWithCyprusCommand());

    $command = $application->find('stand-with-cyprus');
    $commandTester = new CommandTester($command);
    $commandTester->execute([]);

    $output = $commandTester->getDisplay();
    
    if (strpos($output, '#StandWith') !== false && 
        strpos($output, 'Cyprus') !== false && 
        strpos($output, 'Political message:') !== false) {
        echo "✅ PASSED - Command outputs correct message\n";
    } else {
        echo "❌ FAILED - Command output incorrect\n";
        echo "Output: " . $output . "\n";
    }
    
    if ($commandTester->getStatusCode() === 0) {
        echo "✅ PASSED - Command returns success code\n";
    } else {
        echo "❌ FAILED - Command returns error code: " . $commandTester->getStatusCode() . "\n";
    }
} catch (Exception $e) {
    echo "❌ FAILED - Exception: " . $e->getMessage() . "\n";
}

echo "\n";

// Test 2: Command name and description
echo "Test 2: Command name and description\n";
try {
    $command = new StandWithCyprusCommand();
    
    if ($command->getName() === 'stand-with-cyprus') {
        echo "✅ PASSED - Command name is correct\n";
    } else {
        echo "❌ FAILED - Command name incorrect: " . $command->getName() . "\n";
    }
    
    if ($command->getDescription() === 'Display a political message supporting Cyprus') {
        echo "✅ PASSED - Command description is correct\n";
    } else {
        echo "❌ FAILED - Command description incorrect: " . $command->getDescription() . "\n";
    }
} catch (Exception $e) {
    echo "❌ FAILED - Exception: " . $e->getMessage() . "\n";
}

echo "\n";

// Test 3: Application integration
echo "Test 3: Application integration\n";
try {
    $application = new Application('stand-with-cyprus', '1.0.0');
    $application->add(new StandWithCyprusCommand());
    $application->setDefaultCommand('stand-with-cyprus', true);
    $application->setAutoExit(false);

    $applicationTester = new ApplicationTester($application);
    $exitCode = $applicationTester->run([]);

    if ($exitCode === 0) {
        echo "✅ PASSED - Application runs successfully\n";
    } else {
        echo "❌ FAILED - Application exit code: " . $exitCode . "\n";
    }
    
    $output = $applicationTester->getDisplay();
    if (strpos($output, '#StandWith') !== false && strpos($output, 'Cyprus') !== false) {
        echo "✅ PASSED - Application output contains expected content\n";
    } else {
        echo "❌ FAILED - Application output incorrect\n";
    }
} catch (Exception $e) {
    echo "❌ FAILED - Exception: " . $e->getMessage() . "\n";
}

echo "\n=====================================\n";
echo "Tests completed\n";