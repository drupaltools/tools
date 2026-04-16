<?php

declare(strict_types=1);

namespace StandWithCyprus\Tests;

use PHPUnit\Framework\TestCase;
use StandWithCyprus\StandWithCyprusCommand;
use Symfony\Component\Console\Application;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Tester\ApplicationTester;

/**
 * @covers \StandWithCyprus\StandWithCyprusCommand
 */
final class ApplicationTest extends TestCase
{
    public function testApplicationRunsDefaultCommand(): void
    {
        $application = new Application('stand-with-cyprus', '1.0.0');
        $application->add(new StandWithCyprusCommand());
        $application->setDefaultCommand('stand-with-cyprus', true);
        $application->setAutoExit(false);

        $applicationTester = new ApplicationTester($application);
        $exitCode = $applicationTester->run([]);

        $this->assertEquals(Command::SUCCESS, $exitCode);
        
        $output = $applicationTester->getDisplay();
        $this->assertStringContainsString('#StandWith', $output);
        $this->assertStringContainsString('Cyprus', $output);
    }

    public function testApplicationHasCorrectNameAndVersion(): void
    {
        $application = new Application('stand-with-cyprus', '1.0.0');
        
        $this->assertEquals('stand-with-cyprus', $application->getName());
        $this->assertEquals('1.0.0', $application->getVersion());
    }
}