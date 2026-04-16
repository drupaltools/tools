<?php

declare(strict_types=1);

namespace StandWithCyprus\Tests;

use PHPUnit\Framework\TestCase;
use StandWithCyprus\StandWithCyprusCommand;
use Symfony\Component\Console\Application;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Tester\CommandTester;

/**
 * @covers \StandWithCyprus\StandWithCyprusCommand
 */
final class StandWithCyprusCommandTest extends TestCase
{
    private CommandTester $commandTester;

    protected function setUp(): void
    {
        $application = new Application();
        $application->add(new StandWithCyprusCommand());

        $command = $application->find('stand-with-cyprus');
        $this->commandTester = new CommandTester($command);
    }

    public function testExecuteCommand(): void
    {
        $this->commandTester->execute([]);

        $output = $this->commandTester->getDisplay();
        $this->assertStringContainsString('#StandWith', $output);
        $this->assertStringContainsString('Cyprus', $output);
        $this->assertStringContainsString('Political message:', $output);
        $this->assertEquals(Command::SUCCESS, $this->commandTester->getStatusCode());
    }

    public function testCommandName(): void
    {
        $command = new StandWithCyprusCommand();
        $this->assertEquals('stand-with-cyprus', $command->getName());
    }

    public function testCommandDescription(): void
    {
        $command = new StandWithCyprusCommand();
        $this->assertEquals('Display a political message supporting Cyprus', $command->getDescription());
    }

    public function testOutputContainsFormattedMessage(): void
    {
        $this->commandTester->execute([]);

        $output = $this->commandTester->getDisplay();
        $this->assertStringContainsString('<bg=white;fg=blue> #StandWith </>', $output);
        $this->assertStringContainsString('<fg=black;bg=#f9a942> Cyprus </>', $output);
    }

    public function testCommandReturnsSuccessExitCode(): void
    {
        $exitCode = $this->commandTester->execute([]);

        $this->assertEquals(Command::SUCCESS, $exitCode);
    }
}